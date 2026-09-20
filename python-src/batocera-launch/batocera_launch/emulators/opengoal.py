from __future__ import annotations

import json
import logging
import re
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

_GAMES: Final = ('jak1', 'jak2', 'jak3')

_RUNTIME_PROJECT_DIRS: Final = ('goal_src', 'decompiler', 'game', 'custom_assets')
_GAME_PROJECT_DIRS: Final = ('iso_data', 'decompiler_out', 'out')

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

# SYSTEM.CNF's boot line, which names the ELF after the disc serial
_BOOT_SERIAL_RE: Final = re.compile(rb'cdrom0:\\?([A-Z]{4}_\d{3}\.\d{2})')
_SERIAL_SEARCH_BYTES: Final = 16 << 20

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


def _built_games(project_dir: Path, /) -> list[str]:
    return [game for game in _GAMES if (project_dir / 'out' / game / 'iso' / 'KERNEL.CGO').is_file()]


def _extracted_games(project_dir: Path, /) -> list[str]:
    return [game for game in _GAMES if (project_dir / 'iso_data' / game / 'DGO').is_dir()]


def _rom_project_dir(rom: Path, /) -> Path | None:
    if not rom.is_dir():
        return None

    for candidate in (rom / 'data', rom):
        if any((candidate / directory).is_dir() for directory in _GAME_PROJECT_DIRS):
            return candidate

    return None


def _disc_serial(iso_data: Path, /) -> str | None:
    if (buildinfo := iso_data / 'buildinfo.json').is_file():
        try:
            entries = json.loads(buildinfo.read_text())
        except OSError, ValueError:
            entries = None

        if isinstance(entries, list):
            for entry in cast('list[dict[str, str]]', entries):
                if serial := entry.get('serial'):
                    return serial

    # BOOT2 = cdrom0:\SCES_503.61;1
    if (system_cnf := iso_data / 'SYSTEM.CNF').is_file():
        try:
            text = system_cnf.read_text(errors='replace')
        except OSError:
            return None

        if match := re.search(r'([A-Z]{4})_(\d{3})\.(\d{2})', text):
            return f'{match.group(1)}-{match.group(2)}{match.group(3)}'

    return None


def _iso_serial(iso: Path, /) -> str | None:
    """The disc serial, read out of an ISO without extracting it."""
    try:
        with iso.open('rb') as f:
            carry = b''
            while len(carry) < _SERIAL_SEARCH_BYTES:
                chunk = f.read(1 << 20)
                if not chunk:
                    return None
                if match := _BOOT_SERIAL_RE.search(carry + chunk):
                    return match.group(1).decode().replace('_', '-').replace('.', '')
                carry = chunk[-64:]
    except OSError:
        return None

    return None


def _read_json(path: Path, /) -> dict[str, object] | None:
    try:
        loaded = json.loads(path.read_text())
    except OSError, ValueError:
        return None

    return cast('dict[str, object]', loaded) if isinstance(loaded, dict) else None


def _recorded_version(marker: Path, /) -> int | None:
    try:
        recorded = json.loads(marker.read_text())
    except OSError, ValueError:
        return None

    if not isinstance(recorded, dict):
        return None

    version = cast('dict[str, str]', recorded).get('pc_kernel_version')

    try:
        return int(version, 16) if isinstance(version, str) else None
    except ValueError:
        return None


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

    def _prepare_project_dir(self, rom_project_dir: Path | None, /) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / 'log').mkdir(exist_ok=True)

        for directory in _RUNTIME_PROJECT_DIRS:
            _link_or_replace(self.project_dir / directory, _SHIPPED_DATA / directory)

        for directory in _GAME_PROJECT_DIRS:
            target = _game_data_target(
                self.data_dir / directory,
                rom_project_dir / directory if rom_project_dir is not None else None,
            )
            target.mkdir(parents=True, exist_ok=True)
            _link_or_replace(self.project_dir / directory, target)

    def _built_data_dir(self) -> Path:
        return (self.project_dir / 'out').resolve().parent

    def _record_build(self, game: str, /) -> str:
        if (version := _pckernel_version(_SHIPPED_DATA / 'goal_src', game)) is not None:
            marker = self.data_dir / _BUILD_MARKER
            marker.write_text(json.dumps({'game': game, 'pc_kernel_version': f'{version:#x}'}, indent=2))

        return game

    def _matches_runtime(self, built_dir: Path, game: str, /) -> bool:
        built_version = _recorded_version(built_dir / _BUILD_MARKER)

        if built_version is None and (goal_src := built_dir / 'goal_src').is_dir():
            built_version = _pckernel_version(goal_src, game)

        runtime_version = _pckernel_version(_SHIPPED_DATA / 'goal_src', game)

        if built_version is None or runtime_version is None:
            _logger.debug('no version to check %s against, using its built data as-is', built_dir)
            return True

        if built_version != runtime_version:
            _logger.info(
                '%s was built for PC kernel version %#x, this runtime is %#x - rebuilding from iso_data',
                built_dir,
                built_version,
                runtime_version,
            )
            return False

        return True

    def _ensure_writable_outputs(self) -> None:
        for directory in ('decompiler_out', 'out'):
            target = self.data_dir / directory
            target.mkdir(parents=True, exist_ok=True)
            _link_or_replace(self.project_dir / directory, target)

    async def _extract(self, source: Path, game: str | None, /, *, folder: bool) -> bool:
        self._ensure_writable_outputs()

        flags = ['-d', '-c'] if folder else ['-e', '-d', '-c']
        args = [str(source), '--proj-path', str(self.project_dir), *flags]

        if folder:
            args.append('-f')

        if game is not None:
            args += ['-g', game]

        _logger.info(
            'Building the game from %s. This decompiles and recompiles the whole game and takes a '
            'long time on the first run; later launches reuse the result in %s.',
            source,
            self.data_dir,
        )

        result = await run(_INSTALL_DIR / 'extractor', *args, capture_output=False)

        if result.returncode:
            _logger.error('extractor failed with exit code %s, see %s', result.returncode, self.project_dir / 'log')
            return False

        return True

    async def _resolve_game(self) -> str:
        rom_project_dir = _rom_project_dir(self.rom)
        self._prepare_project_dir(rom_project_dir)

        def first(games: list[str], /) -> str | None:
            return games[0] if games else None

        if (game := first(_built_games(self.project_dir))) is not None and self._matches_runtime(
            self._built_data_dir(), game
        ):
            return game

        if (game := first(_extracted_games(self.project_dir))) is not None:
            iso_data = self.project_dir / 'iso_data' / game
            if await self._extract(iso_data, game, folder=True):
                return self._record_build(game)

        # the extractor validates the disc against -g before it corrects the game from the
        # serial, and -g defaults to jak1, so jak2 and jak3 have to be named up front
        if (
            self.rom.is_file()
            and await self._extract(self.rom, _SERIAL_GAMES.get(_iso_serial(self.rom) or ''), folder=False)
            and (game := first(_built_games(self.project_dir))) is not None
        ):
            return self._record_build(game)

        # a bare disc folder, not yet arranged as iso_data/<game>
        if (self.rom / 'DGO').is_dir():
            serial = _disc_serial(self.rom)

            if (game := _SERIAL_GAMES.get(serial or '')) is None:
                raise BatoceraException(
                    f'{self.rom.source} is not a Jak disc OpenGOAL knows (serial {serial or "unknown"})'
                )

            if await self._extract(self.rom, game, folder=True):
                return self._record_build(game)

        raise BatoceraException(f'no playable OpenGOAL game data could be produced from {self.rom.source}')

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
        version = _pckernel_version(_SHIPPED_DATA / 'goal_src', game)

        if version is None:
            _logger.warning('could not read the PC kernel version for %s, leaving pc-settings.gc alone', game)
            return

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
