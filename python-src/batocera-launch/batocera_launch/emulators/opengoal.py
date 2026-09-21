from __future__ import annotations

import json
import logging
import re
import shutil
from contextlib import suppress
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from batocera_common.asyncio import run
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext
from batocera_launch.exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

_logger: Final = logging.getLogger(__name__)

_INSTALL_DIR: Final = Path('/usr/bin/opengoal')
_SHIPPED_DATA: Final = _INSTALL_DIR / 'data'
_RELEASE_FILE: Final = _INSTALL_DIR / 'version'

_GAMES: Final = ('jak1', 'jak2', 'jak3')

_RUNTIME_PROJECT_DIRS: Final = ('goal_src', 'decompiler', 'game', 'custom_assets')
_GAME_PROJECT_DIRS: Final = ('iso_data', 'decompiler_out', 'out')
_PLAY_PROJECT_DIRS: Final = ('iso_data', 'out')

_SERIAL_GAMES: Final = {
    'SCUS-97124': 'jak1',
    'SCES-50361': 'jak1',
    'SCPS-15021': 'jak1',
    'SCPS-56003': 'jak1',
    'SCUS-97265': 'jak2',
    'SCES-51608': 'jak2',
    'SCPS-15057': 'jak2',
    'SCKA-20010': 'jak2',
    'SCUS-97330': 'jak3',
    'SCUS-97516': 'jak3',
    'SCES-52460': 'jak3',
    'SCKA-20040': 'jak3',
}

_FULLSCREEN: Final = 1

_BUILD_MARKER: Final = 'opengoal-build.json'

# the PS2 visibility data only holds for exactly 4:3 or 16:9, so auto cannot use it
_ASPECT_STATES: Final = {
    'auto': ('aspect4x3 4 3 #t', '#f'),
    '4:3': ('aspect4x3 4 3 #f', '#t'),
    '16:9': ('aspect16x9 4 3 #f', '#t'),
}

_ELF_NAME_RE: Final = re.compile(r'([A-Z]{4})_(\d{3})\.(\d{2})')

_ISO_SECTOR: Final = 2048
_ISO_FIRST_DESCRIPTOR: Final = 16
_ISO_MAX_DESCRIPTORS: Final = 32

_PCKERNEL_VERSION_RE: Final = re.compile(
    r'\(defconstant\s+PC_KERNEL_VERSION\s+\(static-pckernel-version\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\)'
)


def _pckernel_version(goal_src: Path, game: str, /) -> int | None:
    try:
        text = (goal_src / game / 'pc' / 'pckernel-impl.gc').read_text()
    except OSError:
        return None

    if not (match := _PCKERNEL_VERSION_RE.search(text)):
        return None

    major, minor, revision, build = map(int, match.groups())
    return major << 48 | minor << 32 | revision << 16 | build


def _serial_from_elf_name(name: str, /) -> str | None:
    if match := _ELF_NAME_RE.fullmatch(name.split(';', 1)[0]):
        return f'{match.group(1)}-{match.group(2)}{match.group(3)}'

    return None


def _iso_root_directory(iso: Path, /) -> bytes | None:
    with iso.open('rb') as f:
        for index in range(_ISO_FIRST_DESCRIPTOR, _ISO_FIRST_DESCRIPTOR + _ISO_MAX_DESCRIPTORS):
            f.seek(index * _ISO_SECTOR)
            descriptor = f.read(_ISO_SECTOR)

            if len(descriptor) < _ISO_SECTOR or descriptor[1:6] != b'CD001' or descriptor[0] == 255:
                return None

            if descriptor[0] == 1:
                record = descriptor[156:190]
                extent = int.from_bytes(record[2:6], 'little')
                size = int.from_bytes(record[10:14], 'little')

                f.seek(extent * _ISO_SECTOR)
                return f.read(min(size, 1 << 20))

    return None


def _iso_serial(iso: Path, /) -> str | None:
    try:
        directory = _iso_root_directory(iso)
    except OSError:
        return None

    if directory is None:
        return None

    offset = 0
    while offset < len(directory):
        length = directory[offset]

        if length == 0:
            offset = (offset // _ISO_SECTOR + 1) * _ISO_SECTOR
            continue

        if length < 34 or offset + length > len(directory):
            return None

        name_length = directory[offset + 32]
        name = directory[offset + 33 : offset + 33 + name_length].decode('ascii', errors='replace')

        if serial := _serial_from_elf_name(name):
            return serial

        offset += length

    return None


def _read_json(path: Path, /) -> dict[str, object] | None:
    try:
        loaded = json.loads(path.read_text())
    except OSError, ValueError:
        return None

    return cast('dict[str, object]', loaded) if isinstance(loaded, dict) else None


def _read_build(built_dir: Path, /) -> tuple[str, str] | None:
    if (marker := _read_json(built_dir / _BUILD_MARKER)) is None:
        return None

    game = marker.get('game')
    release = marker.get('release')

    if game not in _GAMES or not isinstance(release, str) or not release:
        return None

    if not (built_dir / 'out' / game / 'iso' / 'KERNEL.CGO').is_file():
        return None

    return game, release


def _link_or_replace(link: Path, target: Path, /) -> None:
    if link.is_symlink():
        if link.readlink() == target:
            return
        link.unlink()
    elif link.exists():
        return  # a real directory from an older layout, better stale than deleted

    link.symlink_to(target)


def _has_content(path: Path, /) -> bool:
    return path.is_dir() and any(path.iterdir())


def _game_data_target(local: Path, supplied: Path | None, /) -> Path:
    # a rebuild lands in local, and must win next launch or the ROM's stale data is picked again
    if _has_content(local):
        return local

    if supplied is not None and supplied.is_dir():
        return supplied

    return local


def _goal_bool(value: bool, /) -> str:
    return '#t' if value else '#f'


def _top_level_forms(text: str, /) -> Iterator[str]:
    depth = 0
    start = 0

    for index, char in enumerate(text):
        if char == '(':
            if depth == 1:
                start = index
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 1:
                yield text[start : index + 1]


def _merge_pc_settings(existing_text: str, version: int, managed: Mapping[str, str], /) -> str:
    kept: list[str] = []
    seen: set[str] = set()

    for form in _top_level_forms(existing_text):
        key = form[1:].split(maxsplit=1)[0].rstrip(')')
        if key in managed:
            seen.add(key)
            kept.append(f'({key} {managed[key]})')
        else:
            kept.append(form)

    kept.extend(f'({key} {value})' for key, value in managed.items() if key not in seen)

    body = '\n'.join(f'  {form}' for form in kept)
    return f'(settings #x{version:x}\n{body}\n  )\n'


@cached_dataclass
class OpenGOAL(Emulator):
    needs_sdl_game_controller_config = True

    _repacked: tuple[str, str] | None = field(init=False, default=None)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'opengoal',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        match self.config.get_str('opengoal_aspect', 'auto'):
            case '4:3':
                return 4 / 3
            case '16:9':
                return 16 / 9
            case _:
                return 16 / 9 if self.resolution.width / self.resolution.height > (16 / 9 - 0.1) else 4 / 3

    @property
    def execution_path(self) -> Path | None:
        # the base class chdirs here before configure() runs, so it has to exist already
        self.project_dir.mkdir(parents=True, exist_ok=True)
        return self.project_dir

    @cached_property
    def project_dir(self) -> Path:
        return CACHE / 'opengoal' / self.rom.id

    @cached_property
    def data_dir(self) -> Path:
        return self.roms_dir / self.rom.id

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'OpenGOAL'

    def _settings_dir(self, game: str, /) -> Path:
        return self.config_dir / game / 'settings'

    def _misc_dir(self, game: str, /) -> Path:
        return self.config_dir / game / 'misc'

    def _game_saves_dir(self, game: str, /) -> Path:
        return self.saves_dir / game

    @cached_property
    def screenshots_dir(self) -> Path:
        return SCREENSHOTS / self.name

    def _prepare_project_dir(self, supplied: Path | None, /) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / 'log').mkdir(exist_ok=True)

        for directory in _RUNTIME_PROJECT_DIRS:
            _link_or_replace(self.project_dir / directory, _SHIPPED_DATA / directory)

        for directory in _PLAY_PROJECT_DIRS:
            target = _game_data_target(
                self.data_dir / directory, supplied / directory if supplied is not None else None
            )
            target.mkdir(parents=True, exist_ok=True)
            _link_or_replace(self.project_dir / directory, target)

    def _built_data_dir(self) -> Path:
        return (self.project_dir / 'out').resolve().parent

    @cached_property
    def _release(self) -> str:
        try:
            release = _RELEASE_FILE.read_text().strip()
        except OSError:
            release = ''

        if not release:
            raise BatoceraException(f'the installed OpenGOAL does not say which release it is ({_RELEASE_FILE})')

        return release

    def _ensure_writable_outputs(self) -> None:
        for directory in ('decompiler_out', 'out'):
            target = self.data_dir / directory
            target.mkdir(parents=True, exist_ok=True)
            _link_or_replace(self.project_dir / directory, target)

    async def _build(self, source: Path, game: str, /, *, folder: bool) -> None:
        self._ensure_writable_outputs()

        marker = self.data_dir / _BUILD_MARKER
        marker.unlink(missing_ok=True)

        args = [str(source), '--proj-path', str(self.project_dir), '-g', game, '-d', '-c']
        args += ['-f'] if folder else ['-e', '-v']

        _logger.info(
            'Building the game from %s. This decompiles and recompiles the whole game and takes a '
            'long time on the first run; later launches reuse the result in %s.',
            source,
            self.data_dir,
        )

        result = await run(_INSTALL_DIR / 'extractor', *args, capture_output=False)

        if result.returncode:
            raise BatoceraException(
                f'OpenGOAL could not build {game} from {self.rom.source} (extractor exit code {result.returncode}), '
                f'see {self.project_dir / "log"}'
            )

        marker.write_text(json.dumps({'game': game, 'release': self._release}, indent=2))

        if _read_build(self.data_dir) is None:
            raise BatoceraException(f'the extractor finished but left no {game} build in {self.data_dir}')

    async def _resolve_game(self) -> str:
        if self.rom.prepared is not None:
            return await self._resolve_build()

        if self.rom.is_file():
            return await self._resolve_disc()

        raise BatoceraException(f'{self.rom.source} is neither a disc image nor a .squashfs of a built game')

    async def _resolve_disc(self) -> str:
        serial = _iso_serial(self.rom)

        if (game := _SERIAL_GAMES.get(serial or '')) is None:
            raise BatoceraException(
                f'{self.rom.source} is not a supported Jak PS2 disc image (serial {serial or "unknown"})'
            )

        self._prepare_project_dir(None)

        if _read_build(self._built_data_dir()) != (game, self._release):
            await self._build(self.rom, game, folder=False)

        return game

    async def _resolve_build(self) -> str:
        if (build := _read_build(self.rom)) is None:
            raise BatoceraException(f'{self.rom.source} is not a finished OpenGOAL build')

        game, _ = build
        current = (game, self._release)

        if build == current:
            self._drop_local_build(current)

        self._prepare_project_dir(self.rom)

        if _read_build(self._built_data_dir()) != current:
            _logger.info('%s was built by another OpenGOAL version, rebuilding it', self.rom.source)

            if not (self.project_dir / 'iso_data' / game / 'DGO').is_dir():
                raise BatoceraException(f'{self.rom.source} has no iso_data to rebuild {game} from')

            await self._build(self.project_dir / 'iso_data' / game, game, folder=True)

        if build != current:
            await self._repack(current)

        return game

    async def _repack(self, current: tuple[str, str], /) -> None:
        source = self.rom.source
        staging = source.with_name(f'.{source.name}.new')
        staging.unlink(missing_ok=True)

        _logger.info('Repacking %s with the rebuilt game', source)

        result = await run(
            'mksquashfs',
            self.rom / 'iso_data',
            self.data_dir / 'out',
            self.data_dir / _BUILD_MARKER,
            staging,
            '-comp',
            'zstd',
            '-noappend',
            '-no-progress',
            '-quiet',
        )

        if result.returncode or _read_build(self.data_dir) != current:
            staging.unlink(missing_ok=True)
            _logger.warning(
                'could not repack %s (%s), playing from %s and trying again next launch',
                source,
                result.stderr.decode(errors='replace').strip(),
                self.data_dir,
            )
            return

        staging.replace(source)
        self._repacked = current

    def _drop_local_build(self, current: tuple[str, str], /) -> None:
        if _read_build(self.data_dir) != current or _has_content(self.data_dir / 'iso_data'):
            return

        _logger.info('Removing %s, the .squashfs holds the same build', self.data_dir)

        (self.data_dir / _BUILD_MARKER).unlink(missing_ok=True)

        for directory in _GAME_PROJECT_DIRS:
            shutil.rmtree(self.data_dir / directory, ignore_errors=True)

        with suppress(OSError):
            self.data_dir.rmdir()

    async def run(self) -> int:
        try:
            return await super().run()
        finally:
            if self._repacked is not None:
                self._drop_local_build(self._repacked)

    def _write_settings(self, game: str, /) -> None:
        settings_dir = self._settings_dir(game)
        settings_dir.mkdir(parents=True, exist_ok=True)

        misc_dir = self._misc_dir(game)
        misc_dir.mkdir(parents=True, exist_ok=True)

        self._write_display_settings(settings_dir / 'display-settings.json')
        self._write_debug_settings(misc_dir / 'debug-settings.json')
        self._write_pc_settings(game, settings_dir / 'pc-settings.gc')

    def _write_display_settings(self, path: Path, /) -> None:
        settings = _read_json(path) or {'version': '1.2'}

        settings['display_mode'] = _FULLSCREEN
        path.write_text(json.dumps(settings, indent=2))

    def _write_debug_settings(self, path: Path, /) -> None:
        settings = _read_json(path) or {'version': '1.2'}

        # left alt alone toggles the debug menu bar, and that is half of the exit hotkey
        settings['ignore_hide_imgui'] = True
        settings['show_imgui'] = False
        path.write_text(json.dumps(settings, indent=2))

    def _write_pc_settings(self, game: str, path: Path, /) -> None:
        if (version := _pckernel_version(_SHIPPED_DATA / 'goal_src', game)) is None:
            raise BatoceraException(f'the installed OpenGOAL has no PC kernel version for {game}')

        aspect = self.config.get_str('opengoal_aspect', 'auto')
        # use-vis? has to stay after aspect-state, whose handler resets it on the way past
        aspect_state, use_vis = _ASPECT_STATES.get(aspect, _ASPECT_STATES['auto'])

        managed = {
            'window-size': f'{self.resolution.width} {self.resolution.height}',
            'game-size': f'{self.resolution.width} {self.resolution.height}',
            'aspect-state': aspect_state,
            'use-vis?': use_vis,
            'fps': self.config.get_str('opengoal_fps', '60'),
            'msaa': self.config.get_str('opengoal_msaa', '1'),
            'vsync': _goal_bool(self.config.get_bool('opengoal_vsync', True)),
            'letterbox': _goal_bool(self.config.get_bool('opengoal_letterbox', True)),
            'ps2-lod-dist?': _goal_bool(self.config.get_bool('opengoal_ps2_lod', False)),
            'ps2-parts?': _goal_bool(self.config.get_bool('opengoal_ps2_parts', False)),
            'ps2-shadow?': _goal_bool(self.config.get_bool('opengoal_ps2_shadow', False)),
            'ps2-read-speed?': _goal_bool(self.config.get_bool('opengoal_ps2_read_speed', False)),
            'ps2-hints?': _goal_bool(self.config.get_bool('opengoal_ps2_hints', True)),
            'force-envmap?': _goal_bool(self.config.get_bool('opengoal_force_envmap', True)),
            'hinttitles?': _goal_bool(self.config.get_bool('opengoal_hinttitles', False)),
            'subtitle-speaker': self._subtitle_speaker,
            'speedrunner-mode?': _goal_bool(self.config.get_bool('opengoal_speedrunner_mode', False)),
            'discord-rpc?': '#f',
        }

        existing_text = path.read_text() if path.is_file() else ''
        path.write_text(_merge_pc_settings(existing_text, version, managed))

    @property
    def _subtitle_speaker(self) -> str:
        match self.config.get_str('opengoal_subtitle_speaker', 'auto'):
            case 'true':
                return '#t'
            case 'false':
                return '#f'
            case _:
                return 'auto'

    async def configure(self) -> Command:
        game = await self._resolve_game()
        self._write_settings(game)

        saves_dir = self._game_saves_dir(game)
        saves_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        args: list[str | Path] = [
            _INSTALL_DIR / 'gk',
            '--game',
            game,
            '--proj-path',
            self.project_dir,
            # gk appends OpenGOAL/<game>/ of its own
            '--config-path',
            self.config_dir.parent,
            '--saves-path',
            saves_dir,
            '--screenshots-path',
            self.screenshots_dir,
        ]

        if self.config.get_bool('opengoal_verbose_log'):
            args.append('--verbose')

        # gk boots the debug kernel otherwise, and fakeiso is the only working disc mode
        args += ['--', '-boot', '-fakeiso']

        # SDL's own HID drivers report a different GUID than the one batocera's mapping is keyed on
        return Command(args, env={'SDL_JOYSTICK_HIDAPI': '0'})
