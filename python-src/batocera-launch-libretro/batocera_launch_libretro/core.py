from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, NotRequired, ReadOnly, TypedDict

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import MissingCore

from .libretro_info import LibretroInfo

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from batocera_launch import Controller, Controllers, DeviceInfoMapping, Gun, Guns, LibretroConfig, Rom, SystemConfig

    from .emulator import Libretro

_PEDAL_KEYS: Final = {1: 'c', 2: 'v', 3: 'b', 4: 'n'}


class CoreGunMappingItem(TypedDict):
    device: ReadOnly[NotRequired[int]]
    device_p1: ReadOnly[NotRequired[int]]
    device_p2: ReadOnly[NotRequired[int]]
    device_p3: ReadOnly[NotRequired[int]]
    device_p4: ReadOnly[NotRequired[int]]
    p1: ReadOnly[NotRequired[int]]
    p2: ReadOnly[NotRequired[int]]
    p3: ReadOnly[NotRequired[int]]
    p4: ReadOnly[NotRequired[int]]
    gameDependant: ReadOnly[NotRequired[list[dict[str, Any]]]]


@cached_dataclass
class Core:
    force_slang_shaders: ClassVar[bool] = False
    supports_retroachievements: ClassVar[bool] = False
    gun_mapping: ClassVar[Mapping[str, CoreGunMappingItem] | None] = None

    emulator: Libretro

    @cached_property
    def library_prefix(self) -> str:
        return self.emulator.core

    @cached_property
    def info(self) -> LibretroInfo:
        info = LibretroInfo.load(self.library_prefix)

        if info is None:
            raise MissingCore

        return info

    @property
    def system(self) -> str:
        return self.emulator.system

    @property
    def config(self) -> SystemConfig:
        return self.emulator.config

    @property
    def rom(self) -> Rom:
        return self.emulator.rom

    @property
    def metadata(self) -> dict[str, str]:
        return self.emulator.metadata

    @property
    def controllers(self) -> Controllers:
        return self.emulator.controllers

    @property
    def guns(self) -> Guns:
        return self.emulator.guns

    @property
    def wheels(self) -> DeviceInfoMapping:
        return self.emulator.wheels

    @cached_property
    def __savestate_features(self) -> Literal['disabled', 'basic', 'serialized', 'deterministic']:
        # The following is based on core_info.c in RetroArch

        savestate = self.info.get_bool('savestate')

        if savestate is False:
            return 'disabled'

        if savestate and (features := self.info.get('savestate_features')) in ('basic', 'serialized'):
            return features

        return 'deterministic'

    @cached_property
    def can_rewind(self) -> bool:
        return self.__savestate_features in {'serialized', 'deterministic'} and self.config.get_bool('rewind')

    @cached_property
    def runahead(self) -> int:
        if self.__savestate_features == 'deterministic':
            return self.config.get_int('runahead', 0)

        return 0

    @property
    def disables_bezel(self) -> bool:
        return False

    @cached_property
    def map_lightguns(self) -> bool:
        return self.config.get_bool('lightgun_map', True)

    @cached_property
    def player1_device_type(self) -> str | None:
        return None

    @cached_property
    def player2_device_type(self) -> str | None:
        return None

    @cached_property
    def player3_device_type(self) -> str | None:
        return None

    @cached_property
    def player4_device_type(self) -> str | None:
        return None

    @cached_property
    def rom_argument(self) -> str | Path | None:
        return self.rom

    def force_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        return None

    def override_default_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        return None

    def get_command_arguments(self) -> list[str | Path] | None:
        return None

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        for direction in ('up', 'down', 'left', 'right'):
            if direction in controller.inputs and (
                controller.inputs[direction].type == 'button' or controller.inputs[direction].type == 'hat'
            ):
                return '1'

        return '0'

    def set_button_mappings(self, controller: Controller, button_mappings: dict[str, str], /) -> None:
        return None

    def get_mouse_index(self, controller: Controller, /) -> str:
        return '0'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        return None

    def set_gun_core_options(self, core_options: LibretroConfig, /) -> None:
        return None

    def generate_special_configs(self) -> None:
        return None

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        return None

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_offscreen_shot'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        return None
