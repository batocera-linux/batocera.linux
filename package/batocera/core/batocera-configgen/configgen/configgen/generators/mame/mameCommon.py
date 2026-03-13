from __future__ import annotations

import csv
import logging
import subprocess
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, cast

from ...exceptions import InvalidConfiguration
from .mamePaths import MAME_CONFIG, MAME_DEFAULT_DATA

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from .mameTypes import MameControlScheme

_logger = logging.getLogger(__name__)

# The comprehensive list of known floppy disk extensions for the Atom system
_ATOM_FLOPPY_EXTENSIONS: Final = {
    '.mfi',
    '.dfi',
    '.hfe',
    '.mfm',
    '.td0',
    '.imd',
    '.d77',
    '.d88',
    '.1dd',
    '.cqm',
    '.cqi',
    '.dsk',
    '.40t',
}
_7Z_EXECUTABLE: Final = Path('/usr/bin/7z')
_SOFTLIST_HASH_DIR: Final = Path('/usr/bin/mame/hash')

_SPECIAL_CONTROL_LIST: Final = [
    'cdimono1',
    'apfm1000',
    'astrocde',
    'adam',
    'arcadia',
    'gamecom',
    'tutor',
    'crvision',
    'bbcb',
    'bbcm',
    'bbcm512',
    'bbcmc',
    'xegs',
    'socrates',
    'vgmplay',
    'pdp1',
    'vc4000',
    'fmtmarty',
    'gp32',
    'apple2p',
    'apple2e',
    'apple2ee',
]


@dataclass(slots=True)
class MessSystemInfo:
    name: str
    rom_type: str
    auto_run: str | None


def get_mess_system_info(system: Emulator, /) -> MessSystemInfo | None:
    mess_systems = tomllib.loads((MAME_DEFAULT_DATA / 'messSystems.toml').read_text())
    mess_system = mess_systems.get(system.name, None)

    # This must be an `is not None` check because the dictionary could be empty
    if mess_system is not None:
        return MessSystemInfo(
            mess_system.get('name', system.name),
            mess_system.get('rom_type', ''),
            mess_system.get('auto_run'),
        )

    return None


def _load_csv_autorun_override(csv_path: Path, rom_name: str, /) -> str | None:
    """Look up an autorun command override from a legacy CSV autoload file.

    The CSV format uses semicolon delimiters, single-quote quotechar,
    and lines starting with # are comments.
    """
    if not csv_path.exists():
        return None

    with csv_path.open() as f:
        for row in csv.reader(f, delimiter=';', quotechar="'"):
            if row and not row[0].startswith('#') and row[0].casefold() == rom_name.casefold():
                return row[1]

    return None


def _load_autorun_override(toml_path: Path, rom_name: str, /) -> str | None:
    """Look up an autorun command override from an autoload file.

    Checks for a TOML file first. If not found, falls back to a legacy CSV
    file at the same path with a .csv extension.

    Returns the command string if found (case-insensitive key match), or None.
    """
    if toml_path.exists():
        overrides = {k.casefold(): v for k, v in tomllib.loads(toml_path.read_text()).items()}
        return overrides.get(rom_name.casefold())

    return _load_csv_autorun_override(toml_path.with_suffix('.csv'), rom_name)


def _is_atom_floppy(rom: Path, /) -> bool:
    extension = rom.suffix.casefold()
    if extension in _ATOM_FLOPPY_EXTENSIONS:
        return True

    if extension == '.zip':
        try:
            with zipfile.ZipFile(rom, 'r') as zip_ref:
                for filename_in_zip in zip_ref.namelist():
                    if Path(filename_in_zip).suffix.lower() in _ATOM_FLOPPY_EXTENSIONS:
                        return True
        except zipfile.BadZipFile:
            _logger.warning('Could not read zip file: %s', rom)

    elif extension == '.7z':
        try:
            proc = subprocess.run([_7Z_EXECUTABLE, 'l', '-ba', str(rom)], capture_output=True, text=True, check=False)
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    if Path(line.strip()).suffix.lower() in _ATOM_FLOPPY_EXTENSIONS:
                        return True
            else:
                _logger.warning('7z command failed for %s: %s', rom, proc.stderr)
        except FileNotFoundError:
            _logger.error('The executable was not found at %s. Cannot inspect .7z files.', _7Z_EXECUTABLE)

    return False


def _get_coco_autorun(
    rom_name: str,
    rom_ext: str,
    altromtype: str | None,
    soft_list: str,
    system_name: str,
    /,
) -> tuple[str, int]:
    rom_type = 'cart'
    auto_run_cmd = ''
    auto_run_delay = 2

    # if using software list, use "usage" for autoRunCmd (if provided)
    if soft_list:
        soft_list_file = _SOFTLIST_HASH_DIR / f'{soft_list}.xml'
        if soft_list_file.exists():
            softwarelist = ET.parse(soft_list_file)
            for software in softwarelist.findall('software'):
                if software.attrib and software.get('name') == rom_name:
                    for info in software.iter('info'):
                        if info.get('name') == 'usage':
                            auto_run_cmd = rf'{info.get("value")}\n'

    # if still undefined, default autoRunCmd based on media type
    if not auto_run_cmd:
        if altromtype == 'cass' or (soft_list and soft_list.endswith('cass')) or rom_ext.casefold() == '.cas':
            rom_type = 'cass'
            if rom_name.casefold().endswith('.bas'):
                auto_run_cmd = r'CLOAD:RUN\n'
            else:
                auto_run_cmd = r'CLOADM:EXEC\n'
        if altromtype == 'flop1' or (soft_list and soft_list.endswith('flop')) or rom_ext.casefold() == '.dsk':
            rom_type = 'flop'
            if rom_name.casefold().endswith('.bas'):
                auto_run_cmd = rf'RUN "{rom_name}"\n'
            else:
                auto_run_cmd = rf'LOADM "{rom_name}":EXEC\n'

    # check for a user override
    override = _load_autorun_override(MAME_CONFIG / 'autoload' / f'{system_name}_{rom_type}_autoload.toml', rom_name)
    if override is not None:
        auto_run_cmd = rf'{override}\n'

    return auto_run_cmd, auto_run_delay


def get_autorun_command(
    system_name: str,
    mess_auto_run: str | None,
    rom: Path,
    altromtype: str | None,
    soft_list: str,
    /,
    *,
    atom_delay: int = 1,
) -> tuple[str, int]:
    """Determine the autorun command and delay for a MESS system.

    Returns (auto_run_cmd, auto_run_delay). auto_run_cmd is empty string if no autorun.
    """
    rom_name = rom.stem

    # bbc has different boots for floppy & cassette, no special boot for carts
    if system_name == 'bbcmicro':
        if altromtype or soft_list:
            if altromtype == 'cass' or soft_list.endswith('cass'):
                return r'*tape\nchain""\n', 2
            if (altromtype and altromtype.startswith('flop')) or soft_list.endswith('flop'):
                return r'*cat\n\n\n\n*exec !boot\n', 3
        else:
            return r'*cat\n\n\n\n*exec !boot\n', 3
        return '', 0

    # fm7 boots floppies, needs cassette loading
    if system_name == 'fm7':
        if altromtype == 'cass' or (soft_list and soft_list.endswith('cass')):
            return r'LOADM"",,R\n', 5
        return '', 0

    if system_name == 'coco':
        return _get_coco_autorun(rom_name, rom.suffix, altromtype, soft_list, system_name)

    if system_name == 'atom':
        auto_run_cmd = mess_auto_run or ''
        auto_run_delay = atom_delay
        if altromtype == 'flop1' or (soft_list and soft_list.endswith('flop')) or _is_atom_floppy(rom):
            override = _load_autorun_override(MAME_DEFAULT_DATA / 'atom_flop_autoload.toml', rom_name)
            if override is not None:
                auto_run_cmd = rf'{override}\n'
        return auto_run_cmd, auto_run_delay

    # Default: use mess_auto_run and check for softlist-specific override
    auto_run_cmd = mess_auto_run or ''
    auto_run_delay = 0
    if soft_list:
        override = _load_autorun_override(MAME_DEFAULT_DATA / f'{soft_list}_autoload.toml', rom_name)
        if override is not None:
            auto_run_cmd = rf'{override}\n'
            auto_run_delay = 3

    return auto_run_cmd, auto_run_delay


def get_mame_control_scheme(system: Emulator, rom_path: Path, /) -> MameControlScheme:
    # Controls for games with 5-6 buttons or other unusual controls
    controller_type = system.config.get_str('altlayout', 'auto')

    if controller_type in ['default', 'neomini', 'neocd', 'twinstick', 'qbert']:
        return controller_type  # pyright: ignore[reportReturnType]

    roms = cast('dict[str, list[str]]', tomllib.loads((MAME_DEFAULT_DATA / 'mameRoms.toml').read_text()))

    rom_name = rom_path.stem
    if rom_name in roms['capcom']:
        if controller_type in ['auto', 'snes']:
            return 'sfsnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['mortal_kombat']:
        if controller_type in ['auto', 'snes']:
            return 'mksnes'
        if controller_type == 'megadrive':
            return 'mkmegadrive'
        if controller_type == 'fightstick':
            return 'mkstick'
    elif rom_name in roms['killer_instinct']:
        if controller_type in ['auto', 'snes']:
            return 'kisnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['neogeo']:
        return 'neomini'
    elif rom_name in roms['twin_stick']:
        return 'twinstick'
    elif rom_name in roms['rotated_stick']:
        return 'qbert'
    else:
        if controller_type == 'fightstick':
            return 'fightstick'
        if controller_type == 'megadrive':
            return 'mddefault'

    return 'default'


def _get_mame_controls() -> dict[str, dict[str, str]]:
    return tomllib.loads((MAME_DEFAULT_DATA / 'mameControls.toml').read_text())


def _get_mame_control_mapping(controls: dict[str, dict[str, str]], control_scheme: str, /) -> dict[str, str]:
    # Common controls
    mapping = controls['default'].copy()

    # Buttons that change based on game/setting
    if alt_control_mappings := controls.get(control_scheme):
        mapping.update(alt_control_mappings)

    return mapping


def get_mame_control_mapping(control_scheme: str, /) -> dict[str, str]:
    return _get_mame_control_mapping(_get_mame_controls(), control_scheme)


def get_all_mame_control_mappings(
    controls_scheme: str, use_guns: bool = False, use_mouse: bool = False, /
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    controls = _get_mame_controls()

    control_mapping = _get_mame_control_mapping(controls, controls_scheme)

    # Only use gun buttons if lightguns are enabled to prevent conflicts with mouse
    gun_mapping = controls['gunbuttons'].copy() if use_guns else {}

    # For a standard mouse, left, right, scroll wheel should be mapped to action buttons, and if side buttons are available, they will be coin & start
    mouse_mapping = controls['mousebuttons'].copy() if use_mouse else {}

    return control_mapping, gun_mapping, mouse_mapping


@dataclass(slots=True)
class _BaseMessControl:
    player: int
    tag: str
    key: str
    mask: int
    default: int
    reversed: bool


@dataclass(slots=True)
class _BaseMessControlMapping(_BaseMessControl):
    mapping: str
    useMapping: str


@dataclass(slots=True)
class MessSpecialMapping(_BaseMessControlMapping):
    type: Literal['special']


@dataclass(slots=True)
class MessMainMapping(_BaseMessControlMapping):
    type: Literal['main']


@dataclass(slots=True)
class MessComboMapping(_BaseMessControlMapping):
    type: Literal['combo']
    kbMapping: str


@dataclass(slots=True)
class MessAnalogMapping(_BaseMessControl):
    type: Literal['analog']
    incMapping: str
    incUseMapping: str
    decMapping: str
    decUseMapping: str
    delta: int
    axis: str


type MessControlMapping = MessSpecialMapping | MessMainMapping | MessComboMapping | MessAnalogMapping


def _dict_to_mess_control_mapping(control_dict: dict[str, Any]) -> MessControlMapping:
    base: dict[str, Any] = {
        'player': control_dict['player'],
        'tag': control_dict['tag'],
        'key': control_dict['key'],
        'mask': control_dict['mask'],
        'default': control_dict['default'],
        'reversed': control_dict.get('reversed', False),
    }

    match control_dict['type']:
        case 'special' | 'main' | 'combo' as type:
            mapping = control_dict['mapping']
            kwargs: dict[str, Any] = {
                **base,
                'type': type,
                'mapping': mapping,
                'useMapping': control_dict.get('useMapping', mapping),
            }

            if type == 'main':
                return MessMainMapping(**kwargs)

            if type == 'special':
                return MessSpecialMapping(**kwargs)

            kwargs['kbMapping'] = control_dict['kbMapping']
            return MessComboMapping(**kwargs)
        case 'analog':
            return MessAnalogMapping(
                **base,
                type='analog',
                incMapping=control_dict['incMapping'],
                incUseMapping=control_dict.get('incUseMapping', control_dict['incMapping']),
                decMapping=control_dict['decMapping'],
                decUseMapping=control_dict.get('decUseMapping', control_dict['decMapping']),
                delta=control_dict['delta'],
                axis=control_dict['axis'],
            )
        case _:
            raise InvalidConfiguration(f'Unknown control mapping type: {control_dict["type"]}')


def get_mess_system_controls(mess_system_name: str, control_scheme: str, /) -> dict[str, MessControlMapping] | None:
    if mess_system_name not in _SPECIAL_CONTROL_LIST:
        return None

    mess_controls = tomllib.loads((MAME_DEFAULT_DATA / 'messControls.toml').read_text())

    return {key: _dict_to_mess_control_mapping(value) for key, value in mess_controls.get(control_scheme, {}).items()}
