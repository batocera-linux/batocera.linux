from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


def _find_iname(directory: Path, filename: str) -> Path | None:
    if not directory.is_dir():
        return None

    lower_filename = filename.lower()
    return next(
        (f for f in directory.iterdir() if f.is_file() and f.name.lower() == lower_filename),
        None,
    )


@cached_dataclass
class DosBoxStaging(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dosboxstaging',
            'keys': {'exit': ['KEY_LEFTCTRL', 'KEY_F9']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'dosbox'

    @property
    def needs_mouse(self) -> bool:
        return True

    @property
    def needs_overlayfs(self) -> bool:
        return self.config.get_bool('dosbox_staging_writes_to_rom')

    async def configure(self) -> Command:
        # Handle the single-file ROM case
        game_dir = self.rom if self.rom.is_dir() else self.rom.parent

        common_resource_conf = _find_iname(self.config_dir, 'dosbox-staging.conf')

        dosbox_cfg = _find_iname(game_dir, 'dosbox.cfg')
        dosbox_conf = _find_iname(game_dir, 'dosbox.conf')
        dosbox_bat = _find_iname(game_dir, 'dosbox.bat')

        is_configured = dosbox_cfg or dosbox_conf or dosbox_bat

        args: list[str | Path] = [
            '/usr/bin/dosbox-staging',
            '--fullscreen',
            '--working-dir',
            game_dir,
            '-c',
            f'set WORKDIR={game_dir}',
        ]

        if self.config_dir.is_dir():
            args.extend(['-c', f'set RESDIR={self.config_dir}'])

        if common_resource_conf:
            args.extend(['-c', f'set RESCONF={common_resource_conf}'])

        if dosbox_cfg:
            args.extend(['--conf', dosbox_cfg.name, '-c', f'set GAMECFG={dosbox_cfg.name}'])
        elif dosbox_conf:
            args.extend(['--conf', dosbox_conf.name, '-c', f'set GAMECONF={dosbox_conf.name}'])

        if dosbox_bat:
            args.extend([dosbox_bat.name, '-c', f'set GAMEBAT={dosbox_bat.name}'])

        if is_configured:
            # If the game's configured, then we can disable the startup logos and
            # automatically exit when the game quits.
            args.extend(['--set', 'startup_verbosity=quiet', '--exit'])
        else:
            # If the game's not configured, then place the user at a valid C:\>
            # prompt inside the game's root directory.
            args.extend(
                [
                    '-c',
                    '@echo off',
                    '-c',
                    'mount c .',
                    '-c',
                    'c:',
                ]
            )

        return Command(args)
