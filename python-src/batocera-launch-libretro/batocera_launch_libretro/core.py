from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, NotRequired, ReadOnly, TypedDict

from batocera_launch import Controller, Controllers, Gun, Guns, Rom, SystemConfig, cached_dataclass, cached_property

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

    from batocera_launch import DeviceInfoMapping

    from .config import LibretroConfig
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

    @property
    def can_rewind(self) -> bool:
        return self.config.get_bool('rewind')

    @property
    def runahead(self) -> int:
        return self.config.get_int('runahead', 0)

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


class DisableAutoLightgunMappingMixin(Core):
    @cached_property
    def map_lightguns(self) -> bool:
        return self.config.get_bool('lightgun_map', False)


class DisableAnalogModeMixin(Core):
    def get_analog_mode(self, controller: Controller, /) -> Literal['0']:
        return '0'


class DisableRewindMixin(Core):
    @property
    def can_rewind(self) -> bool:
        return False


class DisableRunaheadMixin(Core):
    @property
    def runahead(self) -> int:
        return 0


class AssociatedMouseMixin(Core):
    def get_mouse_index(self, controller: Controller, /) -> str:
        from batocera_launch import get_associated_mouse, get_device_info

        associated_mouse = get_associated_mouse(get_device_info(), controller.device_path)

        if associated_mouse is not None:
            return associated_mouse

        return super().get_mouse_index(controller)


class GLCoreOverrideMixin(Core):
    def override_default_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'gl':
            return 'glcore'

        return super().override_default_gfx_backend(default_gfx_backend)


class GLOverrideMixin(Core):
    def override_default_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'glcore':
            return 'gl'

        return super().override_default_gfx_backend(default_gfx_backend)


class GLCoreForceMixin(Core):
    def force_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'gl':
            return 'glcore'

        return super().force_gfx_backend(default_gfx_backend)


class GLForceMixin(Core):
    def force_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'glcore':
            return 'gl'

        return super().force_gfx_backend(default_gfx_backend)


class SquashFSMixin(Core):
    squashfs_rom_globs: ClassVar[Mapping[str, Iterable[str]]]

    @cached_property
    def rom_argument(self) -> str | Path | None:
        if (
            (globs := self.squashfs_rom_globs.get(self.system)) is not None
            and 'squashfs' in str(self.rom)
            and self.rom.is_dir()
        ):
            return next(itertools.chain(*(self.rom.glob(glob) for glob in globs)))

        return self.rom
