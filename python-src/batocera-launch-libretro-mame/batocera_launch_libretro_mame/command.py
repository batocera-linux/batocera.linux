from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.paths import BIOS, CONFIGS, ROMS, SAVES
from batocera_launch.paths import USER_DECORATIONS
from batocera_launch_mame_common import get_autorun_command
from batocera_launch_mame_common.paths import MAME_BIN_DIR, MAME_BIOS, MAME_SAVES

if TYPE_CHECKING:
    from .core import Mame

_logger = logging.getLogger(__name__)

_ARCADE_SYSTEMS: Final = {
    'mame',
    'neogeo',
    'lcdgames',
    'tvgames',
    'vis',
    'namco22',
    'model2',
    'cave3rd',
    'gaelco',
    'hikaru',
}
_SUBDIR_SOFT_LIST: Final = ['mac_hdd', 'bbc_hdd', 'cdi', 'archimedes_hdd', 'fmtowns_cd']
_SOFT_DIR: Final = Path('/var/run/mame_software')
_CMD_DIR: Final = Path('/var/run/cmdfiles')
_CORE_CONFIG: Final = CONFIGS / 'lr-mame'
_MAC_FLOPPY_DISKS: Final = {'macos30', 'macos608', 'macos701', 'macos75'}


def _quote(value: str | Path, /) -> str:
    return f'"{value}"'


def _prep_software_list(soft_list: str, rom_parent: Path, /) -> None:
    hash_dir = MAME_BIOS / 'hash'
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

    if rom_extension in {'.2mg', '.2img', '.img', '.image'}:
        return '-flop3'

    return '-flop1'


def _mess_media_args(core: Mame, mess_model: str, /) -> list[str | Path]:
    args: list[str | Path] = []
    alt_rom_type = core.config.get_str('altromtype')
    boot_disk = core.config.get('bootdisk')
    rom_extension = core.rom.suffix.lower()

    if core.system != 'macintosh':
        if alt_rom_type:
            if alt_rom_type == 'flop1' and mess_model == 'fmtmarty':
                args.append('-flop')
            else:
                args.append(f'-{alt_rom_type}')
        elif core.system == 'adam':
            if rom_extension == '.ddp':
                args.append('-cass1')
            elif rom_extension == '.dsk':
                args.append('-flop1')
            else:
                args.append('-cart1')
        elif core.system == 'coco':
            if core.rom.suffix.casefold() == '.cas':
                args.append('-cass')
            elif core.rom.suffix.casefold() == '.dsk':
                args.append('-flop1')
            else:
                args.append('-cart')
        elif core.system == 'apple2gs':
            args.append(_apple2gs_flop_type(core.rom))
        elif core.mess_system_info is not None:
            args.append(f'-{core.mess_system_info.rom_type}')
    elif boot_disk:
        if (alt_rom_type == 'flop1' or not alt_rom_type) and boot_disk in _MAC_FLOPPY_DISKS:
            args.append('-flop2')
        elif alt_rom_type:
            args.append(f'-{alt_rom_type}')
        elif core.mess_system_info is not None:
            args.append(f'-{core.mess_system_info.rom_type}')
    elif alt_rom_type:
        args.append(f'-{alt_rom_type}')
    elif core.mess_system_info is not None:
        args.append(f'-{core.mess_system_info.rom_type}')

    args.extend([_quote(core.rom), '-rompath', _quote(f'{core.rom.parent};{BIOS}')])

    if core.system == 'macintosh' and boot_disk:
        if boot_disk in _MAC_FLOPPY_DISKS:
            args.extend(['-flop1', _quote(BIOS / f'{boot_disk}.img')])
        else:
            args.extend(['-hard', _quote(BIOS / f'{boot_disk}.chd')])

    if core.config.get_bool('addblankdisk'):
        if core.system == 'fmtowns':
            blank_disk = Path('/usr/share/mame/blank.fmtowns')
            target_disk = MAME_SAVES / core.system / f'{core.rom.id}.fmtowns'
        else:
            blank_disk = Path('/usr/share/mame/blank.default')
            target_disk = MAME_SAVES / core.system / f'{core.rom.id}.default'

        target_disk.parent.mkdir(parents=True, exist_ok=True)
        if not target_disk.exists():
            shutil.copy2(blank_disk, target_disk)

        if mess_model == 'fmtmarty':
            args.extend(['-flop', _quote(target_disk)])
        elif alt_rom_type == 'flop2':
            args.extend(['-flop1', _quote(target_disk)])
        else:
            args.extend(['-flop2', _quote(target_disk)])

    return args


def _system_args(core: Mame, mess_model: str, /) -> tuple[list[str | Path], str]:
    args: list[str | Path] = []
    special_controller = 'none'

    if core.system == 'ti99':
        args.extend(['-ioport', 'peb'])
        if core.config.get_bool('ti99_32kram'):
            args.extend(['-ioport:peb:slot2', '32kmem'])
        if core.config.get_bool('ti99_speech', True):
            args.extend(['-ioport', 'speechsyn'])

    if core.system == 'laser310':
        args.extend(['-io', 'joystick', '-mem', core.config.get('memslot', 'laser_64k')])

    if core.system == 'bbcmicro' and (stick_type := core.config.get('sticktype', 'none')) != 'none':
        args.extend(['-analogue', stick_type])
        special_controller = stick_type

    if core.system == 'apple2':
        if core.rom.suffix.lower() in {'.hdv', '.2mg', '.chd', '.iso', '.bin', '.cue'}:
            args.extend(['-sl7', 'cffa202'])
        if (game_io := core.config.get('gameio', 'none')) != 'none':
            if game_io == 'joyport' and mess_model != 'apple2p':
                _logger.debug('Joyport is only compatible with Apple II Plus')
            else:
                args.extend(['-gameio', game_io])
                special_controller = game_io

    ram_size = core.config.get_int('ramsize')
    if core.system != 'macintosh' and ram_size:
        args.extend(['-ramsize', f'{ram_size}M'])

    if core.system == 'macintosh' and ram_size:
        if mess_model in {'maciix', 'maclc3'}:
            if mess_model == 'maclc3' and ram_size == 2:
                ram_size = 4
            if mess_model == 'maclc3' and ram_size > 80:
                ram_size = 80
            if mess_model == 'maciix' and ram_size == 16:
                ram_size = 32
            if mess_model == 'maciix' and ram_size == 48:
                ram_size = 64
            args.extend(['-ramsize', f'{ram_size}M'])
        if mess_model == 'maciix':
            image_slot = core.config.get('imagereader', 'nba')
            if image_slot != 'disabled':
                args.extend([f'-{image_slot}', 'image'])

    return args, special_controller


def build_command_line(core: Mame, /) -> tuple[list[str], Path, str, str]:
    command_line: list[str | Path] = []
    special_controller = 'none'
    mess_model = ''
    custom_cfg = core.config.get_bool('customcfg')

    if core.system in _ARCADE_SYSTEMS:
        cfg_path = (_CORE_CONFIG / 'custom') if custom_cfg else (MAME_SAVES / 'mame' / 'cfg')
        cfg_path.mkdir(parents=True, exist_ok=True)

        if core.system == 'vis':
            command_line.extend(['vis', '-cdrom', _quote(core.rom)])
        else:
            command_line.append(core.rom.id)

        command_line.extend(['-cfg_directory', _quote(cfg_path)])
        command_line.extend(['-rompath', _quote(f'{core.rom.parent};{MAME_BIOS};{BIOS}')])

        plugins_to_load: list[str] = []
        if core.config.get_bool('hiscoreplugin', True):
            plugins_to_load.append('hiscore')
        if core.config.get_bool('coindropplugin'):
            plugins_to_load.append('coindrop')
        if core.config.get_bool('offscreenreload'):
            plugins_to_load.append('offscreenreload')
        if plugins_to_load:
            command_line.extend(['-plugins', '-plugin', ','.join(plugins_to_load)])
    else:
        mess_system = core.mess_system_info
        if mess_system is None:
            raise ValueError(f'Unknown MAME/MESS system: {core.system}')

        soft_list = core.config.get_str('softList', 'none')
        soft_list = '' if soft_list == 'none' else (soft_list or '')

        if core.system == 'fmtowns' and not soft_list and (ROMS / 'fmtowns' / f'{core.rom.parent.name}.zip').exists():
            soft_list = 'fmtowns_cd'

        mess_model = core.config.get('altmodel') or mess_system.name
        command_line.append(mess_model)

        if not mess_system.name:
            cfg_path = (_CORE_CONFIG / 'custom') if custom_cfg else (MAME_SAVES / 'mame' / 'cfg')
            cfg_path.mkdir(parents=True, exist_ok=True)
            command_line.append(core.rom.id)
            command_line.extend(['-cfg_directory', _quote(cfg_path)])
            command_line.extend(['-rompath', _quote(f'{core.rom.parent};{BIOS}')])
        else:
            system_args, special_controller = _system_args(core, mess_model)
            command_line.extend(system_args)

            alt_rom_type = core.config.get_str('altromtype')

            if soft_list:
                _prep_software_list(soft_list, core.rom.parent)
                command_line.append(core.rom.parent.name if soft_list in _SUBDIR_SOFT_LIST else core.rom.id)
                command_line.extend(['-rompath', _quote(f'{_SOFT_DIR};{BIOS}')])
                command_line.extend(['-swpath', _quote(_SOFT_DIR)])
                command_line.append('-verbose')
            else:
                command_line.extend(_mess_media_args(core, mess_model))

            if core.config.get_bool('enableui', True):
                command_line.append('-ui_active')

            if custom_cfg:
                cfg_path = _CORE_CONFIG / mess_system.name / 'custom'
            else:
                cfg_path = MAME_SAVES / 'cfg' / mess_system.name
            if core.config.get_bool('pergamecfg'):
                cfg_path = _CORE_CONFIG / mess_system.name / core.rom.name
            cfg_path.mkdir(parents=True, exist_ok=True)
            command_line.extend(['-cfg_directory', _quote(cfg_path)])

            # lr-mame does NOT support multiple ini paths
            ini_dir = MAME_SAVES / 'mame' / 'ini'
            ini_dir.mkdir(parents=True, exist_ok=True)
            ini_file = ini_dir / 'batocera.ini'
            ini_file.unlink(missing_ok=True)

            autorun_command, autorun_delay = get_autorun_command(
                core.system, core.rom, mess_system, alt_rom_type, soft_list
            )
            command_line.extend(['-inipath', _quote(ini_dir)])
            if autorun_command:
                if autorun_command.startswith("'"):
                    autorun_command = autorun_command.replace("'", '')
                ini_file.write_text(
                    f'autoboot_command          {autorun_command}\nautoboot_delay            {autorun_delay}'
                )

            if core.config.get_bool('addblankdisk'):
                lr_mess_dsk = SAVES / 'lr-mess' / core.system / core.rom.id
                if not lr_mess_dsk.exists():
                    lr_mess_dsk.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2('/usr/share/mame/blank.dsk', lr_mess_dsk)
                if alt_rom_type == 'flop2':
                    command_line.extend(['-flop1', _quote(lr_mess_dsk)])
                else:
                    command_line.extend(['-flop2', _quote(lr_mess_dsk)])

    # Art paths - lr-mame displays artwork in the game area and not in the bezel area
    if core.config.get_bool('sharemameart', True):
        art_path = f'/var/run/mame_artwork/;{MAME_BIN_DIR / "artwork"};{BIOS / "lr-mame" / "artwork"};{MAME_BIOS / "artwork"};{USER_DECORATIONS}'
    else:
        art_path = f'/var/run/mame_artwork/;{MAME_BIN_DIR / "artwork"};{BIOS / "lr-mame" / "artwork"}'
    if core.system != 'ti99':
        command_line.extend(['-artpath', _quote(art_path)])

    # Artwork crop - default to On for lr-mame
    if 'artworkcrop' not in core.config:
        if core.system not in {'pdp1', 'vgmplay', 'ti99'}:
            command_line.append('-artwork_crop')
    elif core.config.get_bool('artworkcrop'):
        command_line.append('-artwork_crop')

    if core.system != 'ti99':
        command_line.extend(['-pluginspath', _quote(f'{MAME_BIN_DIR / "plugins"};{MAME_SAVES / "plugins"}')])
        command_line.extend(['-homepath', MAME_SAVES / 'plugins'])
    if core.system not in {'gamecom', 'ti99'}:
        command_line.extend(['-samplepath', MAME_BIOS / 'samples'])

    (MAME_SAVES / 'plugins').mkdir(parents=True, exist_ok=True)
    (MAME_BIOS / 'samples').mkdir(parents=True, exist_ok=True)

    return [str(item) for item in command_line], cfg_path, mess_model, special_controller


def write_cmd_file(core: Mame, command_line: list[str], /) -> Path:
    _CMD_DIR.mkdir(parents=True, exist_ok=True)
    for file in _CMD_DIR.iterdir():
        if file.suffix == '.cmd':
            file.unlink()

    cmd_filename = _CMD_DIR / f'{core.rom.id}.cmd'
    default_custom_cmd = Path(f'{core.rom}.cmd')
    if default_custom_cmd.is_file():
        shutil.copyfile(default_custom_cmd, cmd_filename)
    else:
        cmd_filename.write_text(' '.join(command_line))

    return cmd_filename
