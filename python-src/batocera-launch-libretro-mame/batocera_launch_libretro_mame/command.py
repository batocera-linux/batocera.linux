from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass
from batocera_common.paths import BIOS, ROMS, SAVES
from batocera_launch.paths import USER_DECORATIONS
from batocera_launch_mame_common import (
    MessSystemInfo,
    get_atom_autorun_command,
    get_coco_autorun_command,
    get_fm7_autorun_command,
    get_generic_autorun_command,
)
from batocera_launch_mame_common.paths import MAME_BIN_DIR

from .base import MAMEBase

_logger = logging.getLogger(__name__)

_SUBDIR_SOFT_LIST: Final = ['mac_hdd', 'bbc_hdd', 'cdi', 'archimedes_hdd', 'fmtowns_cd']
_SOFT_DIR: Final = Path('/var/run/mame_software')
_MAC_FLOPPY_DISKS: Final = {'macos30', 'macos608', 'macos701', 'macos75'}


def _quote(value: str | Path, /) -> str:
    return f'"{value}"'


def _prep_software_list(bios_dir: Path, soft_list: str, rom_parent: Path, /) -> None:
    hash_dir = bios_dir / 'hash'
    _SOFT_DIR.mkdir(parents=True, exist_ok=True)
    hash_dir.mkdir(parents=True, exist_ok=True)

    for check_file in _SOFT_DIR.iterdir():
        if check_file.is_symlink():
            check_file.unlink()
        if check_file.is_dir():
            shutil.rmtree(check_file)

    for file in hash_dir.iterdir():
        if file.suffix == '.xml':
            file.unlink()

    shutil.copy2(MAME_BIN_DIR / 'hash' / f'{soft_list}.xml', hash_dir / f'{soft_list}.xml')

    if soft_list in _SUBDIR_SOFT_LIST:
        (_SOFT_DIR / soft_list).symlink_to(rom_parent.parent, target_is_directory=True)
    else:
        (_SOFT_DIR / soft_list).symlink_to(rom_parent, target_is_directory=True)


def _apple2gs_flop_type(rom: Path, /) -> str:
    rom_extension = rom.suffix.lower()
    if rom_extension == '.zip':
        with zipfile.ZipFile(rom, 'r') as zip_file:
            file_list = zip_file.namelist()
            if len(file_list) == 1:
                rom_extension = Path(file_list[0]).suffix.lower()

    # 5.25" images are at most 140 KB, anything bigger is a 3.5" disk
    if rom_extension in {'.2mg', '.2img', '.img', '.image'} or (
        rom.suffix.lower() != '.zip' and rom.stat().st_size > 143360
    ):
        return '-flop3'

    return '-flop1'


@cached_dataclass
class MAMECommand(MAMEBase):
    def __mess_media_args(self) -> list[str | Path]:
        args: list[str | Path] = []
        alt_rom_type = self.config.get_str('altromtype')
        boot_disk = self.config.get('bootdisk')
        rom_extension = self.rom.suffix.lower()

        if self.system != 'macintosh':
            if alt_rom_type:
                if alt_rom_type == 'flop1' and self.mess_model == 'fmtmarty':
                    args.append('-flop')
                else:
                    args.append(f'-{alt_rom_type}')
            elif self.system == 'adam':
                if rom_extension == '.ddp':
                    args.append('-cass1')
                elif rom_extension == '.dsk':
                    args.append('-flop1')
                else:
                    args.append('-cart1')
            elif self.system == 'coco':
                if self.rom.suffix.casefold() == '.cas':
                    args.append('-cass')
                elif self.rom.suffix.casefold() == '.dsk':
                    args.append('-flop1')
                else:
                    args.append('-cart')
            elif self.system == 'apple2gs':
                args.append(_apple2gs_flop_type(self.rom))
            elif self.mess_system_info is not None:
                args.append(f'-{self.mess_system_info.rom_type}')
        elif boot_disk:
            if (alt_rom_type == 'flop1' or not alt_rom_type) and boot_disk in _MAC_FLOPPY_DISKS:
                args.append('-flop2')
            elif alt_rom_type:
                args.append(f'-{alt_rom_type}')
            elif self.mess_system_info is not None:
                args.append(f'-{self.mess_system_info.rom_type}')
        elif alt_rom_type:
            args.append(f'-{alt_rom_type}')
        elif self.mess_system_info is not None:
            args.append(f'-{self.mess_system_info.rom_type}')

        args.extend([_quote(self.rom), '-rompath', _quote(f'{self.rom.parent};{BIOS}')])

        if self.system == 'macintosh' and boot_disk:
            if boot_disk in _MAC_FLOPPY_DISKS:
                args.extend(['-flop1', _quote(BIOS / f'{boot_disk}.img')])
            else:
                args.extend(['-hard', _quote(BIOS / f'{boot_disk}.chd')])

        if self.config.get_bool('addblankdisk'):
            if self.system == 'fmtowns':
                blank_disk = Path('/usr/share/mame/blank.fmtowns')
                target_disk = self.saves_dir / self.system / f'{self.rom.stem}.fmtowns'
            else:
                blank_disk = Path('/usr/share/mame/blank.default')
                target_disk = self.saves_dir / self.system / f'{self.rom.stem}.default'

            target_disk.parent.mkdir(parents=True, exist_ok=True)
            if not target_disk.exists():
                shutil.copy2(blank_disk, target_disk)

            if self.mess_model == 'fmtmarty':
                args.extend(['-flop', _quote(target_disk)])
            elif alt_rom_type == 'flop2':
                args.extend(['-flop1', _quote(target_disk)])
            else:
                args.extend(['-flop2', _quote(target_disk)])

        return args

    def __system_args(self) -> list[str | Path]:
        args: list[str | Path] = []

        if self.system == 'ti99':
            args.extend(['-ioport', 'peb'])
            if self.config.get_bool('ti99_32kram'):
                args.extend(['-ioport:peb:slot2', '32kmem'])
            if self.config.get_bool('ti99_speech', True):
                args.extend(['-ioport', 'speechsyn'])

        if self.system == 'laser310':
            args.extend(['-io', 'joystick', '-mem', self.config.get('memslot', 'laser_64k')])

        if self.system == 'bbcmicro' and (stick_type := self.config.get('sticktype', 'none')) != 'none':
            args.extend(['-analogue', stick_type])

        if self.system == 'apple2':
            if self.rom.suffix.lower() in {'.hdv', '.2mg', '.chd', '.iso', '.bin', '.cue'}:
                args.extend(['-sl7', 'cffa202'])
            if (gameio := self.config.get('gameio', 'none')) != 'none' and (
                gameio != 'joyport' or self.mess_model == 'apple2p'
            ):
                args.extend(['-gameio', gameio])

        ram_size = self.config.get_int('ramsize')
        if self.system != 'macintosh' and ram_size:
            args.extend(['-ramsize', f'{ram_size}M'])

        if self.system == 'macintosh' and ram_size:
            if self.mess_model in {'maciix', 'maclc3'}:
                if self.mess_model == 'maclc3' and ram_size == 2:
                    ram_size = 4
                if self.mess_model == 'maclc3' and ram_size > 80:
                    ram_size = 80
                if self.mess_model == 'maciix' and ram_size == 16:
                    ram_size = 32
                if self.mess_model == 'maciix' and ram_size == 48:
                    ram_size = 64
                args.extend(['-ramsize', f'{ram_size}M'])
            if self.mess_model == 'maciix':
                image_slot = self.config.get('imagereader', 'nba')
                if image_slot != 'disabled':
                    args.extend([f'-{image_slot}', 'image'])

        return args

    def __get_autorun_command(
        self,
        mess_system: MessSystemInfo,
        alt_rom_type: str | None,
        soft_list: str,
        /,
    ) -> tuple[str, int]:
        # bbc has different boots for floppy & cassette, no special boot for carts
        if self.system == 'bbcmicro':
            if alt_rom_type or soft_list:
                if alt_rom_type == 'cass' or soft_list[-4:] == 'cass':
                    return r'*tape\nchain""\n', 2

                if (alt_rom_type and alt_rom_type.startswith('flop')) or 'flop' in soft_list:
                    return r'*cat\n\n\n\n*exec !boot\n', 3
            else:
                return r'*cat\n\n\n\n*exec !boot\n', 3

            return '', 0

        if self.system == 'fm7':
            return get_fm7_autorun_command(alt_rom_type, soft_list)

        if self.system == 'coco':
            return get_coco_autorun_command(self.config_dir, self.system, self.rom, alt_rom_type, soft_list)

        if self.system == 'atom':
            return get_atom_autorun_command(self.rom, mess_system, alt_rom_type, soft_list, autorun_delay=2)

        return get_generic_autorun_command(self.rom, mess_system, alt_rom_type, soft_list)

    def __build_command_line(self) -> list[str]:
        command_line: list[str | Path] = []

        if self.is_arcade:
            self.cfg_path.mkdir(parents=True, exist_ok=True)

            if self.system == 'vis':
                command_line.extend(['vis', '-cdrom', _quote(self.rom)])
            else:
                command_line.append(self.rom.stem)

            command_line.extend(['-cfg_directory', _quote(self.cfg_path)])
            command_line.extend(['-rompath', _quote(f'{self.rom.parent};{self.bios_dir};{BIOS}')])

            plugins_to_load: list[str] = []
            if self.config.get_bool('hiscoreplugin', True):
                plugins_to_load.append('hiscore')
            if self.config.get_bool('coindropplugin'):
                plugins_to_load.append('coindrop')
            if self.config.get_bool('offscreenreload'):
                plugins_to_load.append('offscreenreload')
            if plugins_to_load:
                command_line.extend(['-plugins', '-plugin', ','.join(plugins_to_load)])
        else:
            assert self.mess_system_info is not None

            mess_system = self.mess_system_info

            soft_list = self.config.get_str('softList', 'none')
            soft_list = '' if soft_list == 'none' else (soft_list or '')

            command_line.append(self.mess_model)

            if (
                self.system == 'fmtowns'
                and not soft_list
                and (ROMS / 'fmtowns' / f'{self.rom.parent.name}.zip').exists()
            ):
                soft_list = 'fmtowns_cd'

            if not mess_system.name:
                command_line.append(self.rom.stem)
                command_line.extend(['-cfg_directory', _quote(self.cfg_path)])
                command_line.extend(['-rompath', _quote(f'{self.rom.parent};{BIOS}')])
            else:
                command_line.extend(self.__system_args())

                alt_rom_type = self.config.get_str('altromtype')

                if soft_list:
                    _prep_software_list(self.bios_dir, soft_list, self.rom.parent)
                    command_line.append(self.rom.parent.name if soft_list in _SUBDIR_SOFT_LIST else self.rom.stem)
                    command_line.extend(['-rompath', _quote(f'{_SOFT_DIR};{BIOS}')])
                    command_line.extend(['-swpath', _quote(_SOFT_DIR)])
                    command_line.append('-verbose')
                else:
                    command_line.extend(self.__mess_media_args())

                if self.config.get_bool('enableui', True):
                    command_line.append('-ui_active')

                self.cfg_path.mkdir(parents=True, exist_ok=True)
                command_line.extend(['-cfg_directory', _quote(self.cfg_path)])

                # lr-mame does NOT support multiple ini paths
                ini_dir = self.saves_dir / 'mame' / 'ini'
                ini_dir.mkdir(parents=True, exist_ok=True)
                ini_file = ini_dir / 'batocera.ini'
                ini_file.unlink(missing_ok=True)

                command_line.extend(['-inipath', _quote(ini_dir)])

                autorun_command, autorun_delay = self.__get_autorun_command(mess_system, alt_rom_type, soft_list)
                if autorun_command:
                    if autorun_command.startswith("'"):
                        autorun_command = autorun_command.replace("'", '')
                    ini_file.write_text(
                        f'autoboot_command          {autorun_command}\nautoboot_delay            {autorun_delay}'
                    )

                if self.config.get_bool('addblankdisk'):
                    lr_mess_dsk = SAVES / 'lr-mess' / self.system / self.rom.stem
                    if not lr_mess_dsk.exists():
                        lr_mess_dsk.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2('/usr/share/mame/blank.dsk', lr_mess_dsk)
                    if alt_rom_type == 'flop2':
                        command_line.extend(['-flop1', _quote(lr_mess_dsk)])
                    else:
                        command_line.extend(['-flop2', _quote(lr_mess_dsk)])

        # Art paths - lr-mame displays artwork in the game area and not in the bezel area,
        # so using regular MAME artwork + shaders is not recommended.
        # By default, will ignore standalone MAME's art paths.
        if self.config.core != 'same_cdi':
            if self.config.get_bool('sharemameart', True):
                art_path = f'/var/run/mame_artwork/;{MAME_BIN_DIR / "artwork"};{BIOS / "lr-mame" / "artwork"};{self.bios_dir / "artwork"};{USER_DECORATIONS}'
            else:
                art_path = f'/var/run/mame_artwork/;{MAME_BIN_DIR / "artwork"};{BIOS / "lr-mame" / "artwork"}'
            if self.system != 'ti99':
                command_line.extend(['-artpath', _quote(art_path)])

        # Artwork crop - default to On for lr-mame
        if 'artworkcrop' not in self.config:
            if self.system not in {'pdp1', 'vgmplay', 'ti99'}:
                command_line.append('-artwork_crop')
        elif self.config.get_bool('artworkcrop'):
            command_line.append('-artwork_crop')

        if self.system != 'ti99':
            command_line.extend(['-pluginspath', _quote(f'{MAME_BIN_DIR / "plugins"};{self.saves_dir / "plugins"}')])
            command_line.extend(['-homepath', self.saves_dir / 'plugins'])
        if self.system not in {'gamecom', 'ti99'}:
            command_line.extend(['-samplepath', self.bios_dir / 'samples'])

        (self.saves_dir / 'plugins').mkdir(parents=True, exist_ok=True)
        (self.bios_dir / 'samples').mkdir(parents=True, exist_ok=True)

        return [str(item) for item in command_line]

    def write_cmd_file(self) -> None:
        cmd_dir = self.cmd_filename.parent
        cmd_dir.mkdir(parents=True, exist_ok=True)
        for file in cmd_dir.iterdir():
            if file.suffix == '.cmd':
                file.unlink()

        default_custom_cmd = Path(f'{self.rom}.cmd')
        if default_custom_cmd.is_file():
            shutil.copyfile(default_custom_cmd, self.cmd_filename)
        else:
            self.cmd_filename.write_text(' '.join(self.__build_command_line()))
