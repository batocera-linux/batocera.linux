from __future__ import annotations

import csv
import tomllib
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Final

from .atom import is_atom_floppy
from .paths import MAME_BIN_DIR, MAME_CONFIG, MAME_DEFAULT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Rom

    from .mess_system_info import MessSystemInfo


_SOFT_LIST_HASH_DIR: Final = MAME_BIN_DIR / 'hash'


def _get_soft_list_usage(soft_list: str, rom_name: str, /) -> str | None:
    if soft_list:
        soft_list_file = _SOFT_LIST_HASH_DIR / f'{soft_list}.xml'
        if soft_list_file.exists():
            software_list = ET.parse(soft_list_file)
            for software in software_list.findall('software'):
                if software.attrib and software.get('name') == rom_name:
                    for info in software.iter('info'):
                        if info.get('name') == 'usage':
                            return rf'{info.get("value")}\n'

    return None


def _load_autorun_csv_override(csv_path: Path, rom_name: str, /) -> str | None:
    if not csv_path.exists():
        return None

    with csv_path.open() as f:
        for row in csv.reader(f, delimiter=';', quotechar="'"):
            if row and not row[0].startswith('#') and row[0].casefold() == rom_name.casefold():
                return row[1]

    return None


def _load_autorun_override(toml_path: Path, rom_name: str, /) -> str | None:
    if toml_path.exists():
        overrides = {key.casefold(): value for key, value in tomllib.loads(toml_path.read_text()).items()}
        return overrides.get(rom_name.casefold())

    return _load_autorun_csv_override(toml_path.with_suffix('.csv'), rom_name)


def _get_coco_autorun_command(
    system_name: str, rom_name: str, rom_extension: str, alt_rom_type: str | None, soft_list: str, /
) -> tuple[str, int]:
    rom_type = 'cart'
    autorun_cmd = ''

    # if using software list, use "usage" for autoRunCmd (if provided)
    if (usage := _get_soft_list_usage(soft_list, rom_name)) is not None:
        autorun_cmd = usage

    # if still undefined, default autoRunCmd based on media type
    if not autorun_cmd:
        if alt_rom_type == 'cass' or (soft_list and soft_list.endswith('cass')) or rom_extension.casefold() == '.cas':
            rom_type = 'cass'
            if rom_name.casefold().endswith('.bas'):
                autorun_cmd = 'CLOAD:RUN\\n'
            else:
                autorun_cmd = 'CLOADM:EXEC\\n'
        if (
            (alt_rom_type == 'flop1')
            or (soft_list and soft_list.endswith('flop'))
            or rom_extension.casefold() == '.dsk'
        ):
            rom_type = 'flop'
            if rom_name.casefold().endswith('.bas'):
                autorun_cmd = f'RUN "{rom_name}"\\n'
            else:
                autorun_cmd = f'LOADM "{rom_name}":EXEC\\n'

    # check for a user override
    if (
        override := _load_autorun_override(
            MAME_CONFIG / 'autoload' / f'{system_name}_{rom_type}_autoload.toml', rom_name
        )
    ) is not None:
        autorun_cmd = rf'{override}\n'

    return autorun_cmd, 2


def get_autorun_command(
    system_name: str,
    rom: Rom,
    mess_system: MessSystemInfo,
    alt_rom_type: str | None,
    soft_list: str,
    /,
) -> tuple[str, int]:
    rom_name = rom.id
    rom_extension = rom.suffix

    # Autostart computer games where applicable
    # bbc has different boots for floppy & cassette, no special boot for carts
    if system_name == 'bbcmicro':
        if alt_rom_type or soft_list:
            if alt_rom_type == 'cass' or soft_list.endswith('cass'):
                return '*tape\\nchain""\\n', 2

            if (alt_rom_type and alt_rom_type.startswith('flop')) or soft_list.endswith('flop'):
                return '*cat\\n\\n\\n\\n*exec !boot\\n', 3
        else:
            return '*cat\\n\\n\\n\\n*exec !boot\\n', 3

        return '', 0

    # fm7 boots floppies, needs cassette loading
    if system_name == 'fm7':
        if alt_rom_type == 'cass' or (soft_list and soft_list[-4:] == 'cass'):
            return 'LOADM”“,,R\\n', 5

        return '', 0

    if system_name in ('coco', 'dragon64'):
        return _get_coco_autorun_command(system_name, rom_name, rom_extension, alt_rom_type, soft_list)

    if system_name == 'mc10':
        rom_type = 'cart'
        autorun_cmd = ''

        # if using software list, use "usage" for autoRunCmd (if provided)
        if (usage := _get_soft_list_usage(soft_list, rom_name)) is not None:
            autorun_cmd = usage

        # if still undefined, default autoRunCmd based on media type
        if not autorun_cmd and (
            alt_rom_type == 'cass' or (soft_list and soft_list.endswith('cass')) or rom_extension.casefold() == '.cas'
        ):
            rom_type = 'cass'
            autorun_cmd = r'CLOAD\n'

        # check for a user override
        if (
            override := _load_autorun_override(
                MAME_CONFIG / 'autoload' / f'{system_name}_{rom_type}_autoload.toml', rom_name
            )
        ) is not None:
            autorun_cmd = rf'{override}\n'

        return autorun_cmd, 2

    if system_name == 'atom':
        autorun_delay = 1
        autorun_cmd = mess_system.auto_run or ''

        # Check if the media being used is a floppy type
        if ((alt_rom_type == 'flop1') or (soft_list and soft_list.endswith('flop')) or is_atom_floppy(rom)) and (
            override := _load_autorun_override(MAME_DEFAULT_DATA / 'atom_flop_autoload.toml', rom_name)
        ) is not None:
            autorun_cmd = rf'{override}\n'

        return autorun_cmd, autorun_delay

    # Check for an override file, otherwise use generic (if it exists)
    autorun_cmd = mess_system.auto_run or ''
    autorun_delay = 0

    if (override := _load_autorun_override(MAME_DEFAULT_DATA / f'{soft_list}_autoload.toml', rom_name)) is not None:
        autorun_cmd = rf'{override}\n'
        autorun_delay = 3

    return autorun_cmd, autorun_delay
