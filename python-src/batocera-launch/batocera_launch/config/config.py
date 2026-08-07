from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from collections import ChainMap
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, Self, cast, overload

from batocera_common.paths import BATOCERA_CONF
from batocera_launch.config.defaults import load_defaults, load_system_defaults
from batocera_launch.config.key_value_config import KeyValueConfig
from batocera_launch.exceptions import MissingEmulator
from batocera_launch.paths import BATOCERA_SHADERS, ES_SETTINGS, USER_SHADERS

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Iterator, KeysView, MutableMapping, ValuesView
    from pathlib import Path


_logger: Final = logging.getLogger(__name__)

type UIMode = Literal['Full', 'Kiosk', 'Kid']


@dataclass(slots=True)
class Config:
    TRUE_VALUES: ClassVar[set[Literal['1', 'true', 'on', 'enabled', True]]] = {'1', 'true', 'on', 'enabled', True}

    data: MutableMapping[str, Any]

    def __len__(self) -> int:
        return len(self.data)

    def __contains__(self, x: object, /) -> bool:
        return x in self.data

    def __getitem__(self, key: str, /) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any, /) -> None:
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __iter__(self) -> Iterator[Any]:
        return self.data.__iter__()

    @overload
    def get(self, key: str, /) -> Any | None: ...

    @overload
    def get[T](self, key: str, /, default: T) -> Any | T: ...

    def get[T](self, key: str, /, default: T | None = None) -> Any | T | None:
        return self.data.get(key, default)

    @overload
    def get_bool(self, key: str, /, default: bool = False) -> bool: ...

    @overload
    def get_bool[T, F](self, key: str, /, default: bool = False, *, return_values: tuple[T, F]) -> T | F: ...

    def get_bool[T, F](
        self, key: str, /, default: bool = False, *, return_values: tuple[T, F] | None = None
    ) -> bool | T | F:
        value = self.data.get(key)

        if value is None:
            if return_values is None:
                return default

            return return_values[not default]

        if isinstance(value, str):
            value = value.lower()

        if return_values is None:
            return value in self.TRUE_VALUES

        return return_values[value not in self.TRUE_VALUES]

    @overload
    def get_str(self, key: str, /) -> str | None: ...

    @overload
    def get_str(self, key: str, /, default: str) -> str: ...

    def get_str(self, key: str, /, default: str | None = None) -> str | None:
        value = self.data.get(key)

        if value is None:
            return default

        return str(value)

    @overload
    def get_int(self, key: str, /) -> int | None: ...

    @overload
    def get_int(self, key: str, /, default: int) -> int: ...

    def get_int(self, key: str, /, default: int | None = None) -> int | None:
        value = self.data.get(key)

        if value is None:
            return default

        return int(value)

    @overload
    def get_float(self, key: str, /) -> float | None: ...

    @overload
    def get_float(self, key: str, /, default: float) -> float: ...

    def get_float(self, key: str, /, default: float | None = None) -> float | None:
        value = self.data.get(key)

        if value is None:
            return default

        return float(value)

    def items(self, /, *, starts_with: str | None = None) -> Iterator[tuple[str, Any]]:
        if starts_with is None:
            yield from self.data.items()
        else:
            starts_with_len = len(starts_with)
            for key, value in self.data.items():
                if key.startswith(starts_with):
                    yield key[starts_with_len:], value

    def keys(self) -> KeysView[str]:
        return self.data.keys()

    def values(self) -> ValuesView[Any]:
        return self.data.values()


@dataclass(slots=True)
class SystemConfig(Config):
    system: str
    rom: Path
    emulator: str
    emulator_forced: bool
    raw_core: str | None
    core: str
    core_forced: bool
    use_guns: bool
    use_wheels: bool
    ui_mode: Literal['Full', 'Kiosk', 'Kid']
    show_fps: bool
    netplay_mode: str | None
    netplay_password: str | None
    netplay_server_ip: str | None
    netplay_server_port: str | None
    netplay_server_session: str | None
    state_slot: str | None
    autosave: str | None
    state_filename: str | None

    __render_config: Config | None = field(init=False, default=None)

    @property
    def video_mode(self) -> str:
        return self.data.get('videomode', 'default')  # type: ignore[no-any-return]

    @property
    def render_config(self) -> Config:
        if self.__render_config is None:
            render_data: dict[str, Any] = {}
            if (shader_set := self.get('shaderset')) is not None:
                if shader_set == 'none':
                    rendering_defaults = BATOCERA_SHADERS / 'configs' / 'rendering-defaults.yml'
                else:
                    rendering_defaults = USER_SHADERS / 'configs' / shader_set / 'rendering-defaults.yml'
                    if not rendering_defaults.exists():
                        rendering_defaults = BATOCERA_SHADERS / 'configs' / shader_set / 'rendering-defaults.yml'

                render_data = load_defaults(
                    self.system, rendering_defaults, rendering_defaults.with_name('rendering-defaults-arch.yml')
                )
            self.__render_config = Config(render_data)

        return self.__render_config

    @classmethod
    def load(cls, args: Namespace, /) -> Self:
        # load configuration from batocera.conf
        user_config = KeyValueConfig()
        user_config.read(BATOCERA_CONF)

        rom = args.rom

        # sanitize rule by EmulationStation
        # see FileData::getConfigurationName() on batocera-emulationstation
        settings_name = rom.name.replace('=', '').replace('#', '')

        user_settings = ChainMap(
            user_config.section(f'{args.system}["{settings_name}"]'),  # game-specific
            user_config.section(f'{args.system}.folder["{rom.parent}"]'),  # folder-specific
            user_config.section(args.system),
            user_config.section('global'),
        )

        # A few emulators have config options named "language", so "system.language" is chosen
        # in order to prevent conflicts with config options from es_features.yaml
        language = user_config.get('system.language')

        data = ChainMap[str, Any](
            {},
            user_settings,
            {'system.language': language} if language is not None else {},
            {f'controllers.{key}': value for key, value in user_config.section_items('controllers')},
            {f'display.{key}': value for key, value in user_config.section_items('display', keep_defaults=True)},
            # read the configuration from the configgen defaults files
            load_system_defaults(args.system),
        )

        if 'emulator' not in data or not data['emulator']:
            _logger.error('no emulator defined. exiting.')
            raise MissingEmulator

        try:
            es_config = ET.parse(ES_SETTINGS)

            # showFPS
            draw_framerate_node = es_config.find('./bool[@name="DrawFramerate"]')
            draw_framerate_value = draw_framerate_node.attrib['value'] if draw_framerate_node is not None else 'false'
            if draw_framerate_value not in ['false', 'true']:
                draw_framerate_value = 'false'

            show_fps = draw_framerate_value == 'true'

            # uimode
            ui_mode_node = es_config.find('./string[@name="UIMode"]')
            ui_mode_value = ui_mode_node.attrib['value'] if ui_mode_node is not None else 'Full'
            if ui_mode_value not in ['Full', 'Kiosk', 'Kid']:
                ui_mode_value = 'Full'

            ui_mode = cast('UIMode', ui_mode_value)
        except Exception:
            show_fps = False
            ui_mode = 'Full'

        emulator = data['emulator']
        if args.emulator is not None:
            emulator = args.emulator

        core = data.get('core', None)
        if args.core is not None:
            core = args.core

        return cls(
            data,
            system=args.system,
            rom=rom,
            emulator=emulator,
            emulator_forced=('emulator' in user_settings or args.emulator is not None),
            raw_core=core,
            core=core or '',
            core_forced=('core' in user_settings or args.core is not None),
            use_guns=data.get('use_guns', args.lightgun or False),
            use_wheels=data.get('use_wheels', args.wheel or False),
            ui_mode=ui_mode,
            show_fps=show_fps,
            netplay_mode=args.netplaymode,
            netplay_password=args.netplaypass,
            netplay_server_ip=args.netplayip,
            netplay_server_port=args.netplayport,
            netplay_server_session=args.netplaysession,
            state_slot=args.state_slot,
            autosave=args.autosave,
            state_filename=args.state_filename,
        )
