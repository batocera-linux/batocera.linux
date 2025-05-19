from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Any

import yaml

from .batoceraPaths import BATOCERA_CONF, BATOCERA_SHADERS, DEFAULTS_DIR, ES_SETTINGS, USER_SHADERS
from .config import Config, SystemConfig
from .exceptions import MissingEmulator
from .settings.unixSettings import UnixSettings

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path
    from typing_extensions import deprecated

    from .gun import Guns

_logger = logging.getLogger(__name__)

# adapted from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def _dict_merge(destination: dict[str, Any], source: Mapping[str, Any]) -> None:
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param destination: dict onto which the merge is executed
    :param source: dict merged into destination
    :return: None
    """
    for key, value in source.items():
        if key in destination and isinstance(destination[key], dict) and isinstance(value, Mapping):
            _dict_merge(destination[key], value)
        else:
            destination[key] = value


def _load_defaults(system_name: str, default_yml: Path, default_arch_yml: Path, /) -> dict[str, Any]:
    with default_yml.open('r') as f:
        defaults = yaml.load(f, Loader=yaml.CLoader)

    arch_defaults: dict[str, Any] = {}
    if default_arch_yml.exists():
        with default_arch_yml.open('r') as f:
            loaded_arch_defaults = yaml.load(f, Loader=yaml.CLoader)
        if loaded_arch_defaults is not None:
            arch_defaults = loaded_arch_defaults

    config: dict[str, Any] = {}

    if 'default' in defaults:
        config = defaults['default']

    if 'default' in arch_defaults:
        _dict_merge(config, arch_defaults['default'])

    if system_name in defaults:
        _dict_merge(config, defaults[system_name])

    if system_name in arch_defaults:
        _dict_merge(config, arch_defaults[system_name])

    return config


def _load_system_config(system_name: str, default_yml: Path, default_arch_yml: Path, /) -> dict[str, Any]:
    defaults = _load_defaults(system_name, default_yml, default_arch_yml)

    # In the yaml files, the "options" structure is not flat, so we have to flatten it here
    # because the options are flat in batocera.conf to make it easier for end users to edit
    data: dict[str, Any] = {'emulator': defaults['emulator'], 'core': defaults['core']}

    if 'options' in defaults:
        _dict_merge(data, defaults['options'])

    return data


@dataclass(slots=True)
class Emulator:
    args: InitVar[Namespace]
    rom: InitVar[Path]

    name: str = field(init=False)
    config: SystemConfig = field(init=False)
    renderconfig: Config = field(init=False)
    game_info_xml: str = field(init=False)
    __es_game_info: dict[str, str] | None = field(init=False, default=None)

    @property
    def es_game_info(self) -> Mapping[str, str]:
        if self.__es_game_info is not None:
            return self.__es_game_info

        self.__es_game_info = {}
        vals = self.__es_game_info

        try:
            tree = ET.parse(self.game_info_xml)
            root = tree.getroot()
            for child in root:
                for metadata in child:
                    vals[metadata.tag] = metadata.text or ''
        except Exception:
            _logger.debug("An error occurred while reading ES metadata")

        return vals

    def __post_init__(self, args: Namespace, rom: Path, /) -> None:
        self.name = args.system
        self.game_info_xml = args.gameinfoxml

        # read the configuration from the system name
        system_data = _load_system_config(
            args.system,
            DEFAULTS_DIR / 'configgen-defaults.yml',
            DEFAULTS_DIR / 'configgen-defaults-arch.yml'
        )

        if not system_data['emulator']:
            _logger.error('no emulator defined. exiting.')
            raise MissingEmulator

        # sanitize rule by EmulationStation
        # see FileData::getConfigurationName() on batocera-emulationstation
        gsname = rom.name.replace('=', '').replace('#', '')
        _logger.info('game settings name: %s', gsname)

        # load configuration from batocera.conf
        settings = UnixSettings(BATOCERA_CONF)

        global_settings = settings.get_all('global')
        system_settings = settings.get_all(args.system)
        folder_settings = settings.get_all(f'{args.system}.folder["{rom.parent}"]')
        game_settings = settings.get_all(f'{args.system}["{gsname}"]')

        # update config
        system_data.update(settings.get_all_iter('display', keep_name=True, keep_defaults=True))
        system_data.update(settings.get_all_iter('controllers', keep_name=True))

        language = settings.config.get('DEFAULT', 'system.language', fallback=None)
        if language is not None:
            # A few emulators have config options named "language", so "system.language" is chosen
            # in order to prevent conflicts with config options from es_features.yaml
            system_data['system.language'] = language

        system_data.update(global_settings)
        system_data.update(system_settings)
        system_data.update(folder_settings)
        system_data.update(game_settings)

        try:
            es_config = ET.parse(ES_SETTINGS)

            # showFPS
            drawframerate_node = es_config.find('./bool[@name="DrawFramerate"]')
            drawframerate_value = drawframerate_node.attrib['value'] if drawframerate_node is not None else 'false'
            if drawframerate_value not in ['false', 'true']:
                drawframerate_value = 'false'

            system_data['showFPS'] = drawframerate_value == 'true'

            # uimode
            uimode_node = es_config.find('./string[@name="UIMode"]')
            uimode_value = uimode_node.attrib['value'] if uimode_node is not None else 'Full'
            if uimode_value not in ['Full', 'Kiosk', 'Kid']:
                uimode_value = 'Full'

            system_data['uimode'] = uimode_value
        except Exception:
            system_data['showFPS'] = False
            system_data['uimode'] = 'Full'

        _logger.debug('uimode: %s', system_data['uimode'])

        system_data['emulator-forced'] = (
            'emulator' in global_settings
            or 'emulator' in system_settings
            or 'emulator' in game_settings
            or args.emulator is not None
        )
        system_data['core-forced'] = (
            'core' in global_settings
            or 'core' in system_settings
            or 'core' in game_settings
            or args.core is not None
        )

        if args.emulator is not None:
            system_data['emulator'] = args.emulator

        if args.core is not None:
            system_data['core'] = args.core

        if 'use_guns' not in system_data and args.lightgun:
            system_data['use_guns'] = True

        if 'use_wheels' not in system_data and args.wheel:
            system_data['use_wheels'] = True

        # network options
        if args.netplaymode is not None:
            system_data['netplay.mode'] = args.netplaymode

        if args.netplaypass is not None:
            system_data['netplay.password'] = args.netplaypass

        if args.netplayip is not None:
            system_data['netplay.server.ip'] = args.netplayip

        if args.netplayport is not None:
            system_data['netplay.server.port'] = args.netplayport

        if args.netplaysession is not None:
            system_data['netplay.server.session'] = args.netplaysession

        # autosave arguments
        if args.state_slot is not None:
            system_data['state_slot'] = args.state_slot

        if args.autosave is not None:
            system_data['autosave'] = args.autosave

        if args.state_filename is not None:
            system_data['state_filename'] = args.state_filename

        self.config = SystemConfig(system_data)

        render_data: dict[str, Any] = {}
        if (shader_set := self.config.get('shaderset')) is not self.config.MISSING:
            if shader_set == 'none':
                rendering_defaults = BATOCERA_SHADERS / 'configs' / 'rendering-defaults.yml'
            else:
                rendering_defaults = USER_SHADERS / 'configs' / shader_set / 'rendering-defaults.yml'
                if not rendering_defaults.exists():
                    rendering_defaults = BATOCERA_SHADERS / 'configs' / shader_set / 'rendering-defaults.yml'

            render_data = _load_defaults(
                args.system, rendering_defaults, rendering_defaults.with_name('rendering-defaults-arch.yml')
            )

        # es only allow to update systemSettings and gameSettings in fact for the moment

        # for compatibility with earlier Batocera versions, let's keep -renderer
        # but it should be reviewed when we refactor configgen (to Python3?)
        # so that we can fetch them from system.shader without -renderer
        render_data.update(settings.get_all_iter(f'{args.system}-renderer'))
        render_data.update(settings.get_all_iter(f'{args.system}["{gsname}"]-renderer'))

        self.renderconfig = Config(render_data)

    if TYPE_CHECKING:
        @deprecated('Use "key" in config')
        def isOptSet(self, key: str) -> bool: ...

        @deprecated('Use config.get_bool()')
        def getOptBoolean(self, key: str) -> bool: ...

        @deprecated('Use config.get_str()')
        def getOptString(self, key: str) -> str: ...

    else:
        def isOptSet(self, key: str) -> bool:
            return key in self.config

        def getOptBoolean(self, key: str) -> bool:
            true_values = {'1', 'true', 'on', 'enabled', True}
            value = self.config.get(key)

            if isinstance(value, str):
                value = value.lower()

            return value in true_values

        def getOptString(self, key: str) -> str:
            if key in self.config:  # noqa: SIM102
                if self.config[key]:
                    return self.config[key]
            return ""

    # returns None if no border is wanted
    def guns_borders_size_name(self, guns: Guns) -> str | None:
        borders_size: str = self.config.get('controllers.guns.borderssize', 'medium')

        # overridden by specific options
        borders_mode = 'normal'
        if (config_borders_mode := (self.config.get('controllers.guns.bordersmode') or 'auto')) != 'auto':
            borders_mode = config_borders_mode
        if (config_borders_mode := (self.config.get('bordersmode') or 'auto')) != 'auto':
            borders_mode = config_borders_mode

        # others are gameonly and normal
        if borders_mode == 'hidden':
            return None

        if borders_mode == 'force':
            return borders_size

        for gun in guns:
            if gun.needs_borders:
                return borders_size

        return None

    # returns None to follow the bezel overlay size by default
    def guns_border_ratio_type(self, guns: Guns) -> str | None:
        return self.config.get('controllers.guns.bordersratio', None)
