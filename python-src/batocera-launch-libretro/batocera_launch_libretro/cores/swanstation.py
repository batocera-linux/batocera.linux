from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig

if TYPE_CHECKING:
    from batocera_launch import Controller, Gun


@cached_dataclass
class Duckstation(DisableRewindMixin, DisableRunaheadMixin, Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # renderer
        if self.config.get_bool('gpu_software'):
            core_options.set('swanstation_GPU_Renderer', 'Software')
        else:
            if gfxbackend := self.config.get('gfxbackend'):
                if gfxbackend == 'vulkan':
                    core_options.set('swanstation_GPU_Renderer', 'Vulkan')
                elif gfxbackend == 'gl' or gfxbackend == 'glcore':
                    core_options.set('swanstation_GPU_Renderer', 'OpenGL')
                else:
                    core_options.set('swanstation_GPU_Renderer', 'Auto')
            else:
                core_options.set('swanstation_GPU_Renderer', 'Auto')

        # Show official Bootlogo
        core_options.set_from_config('swanstation_BIOS_PatchFastBoot', 'swanstation_PatchFastBoot', default='false')

        # Video Resolution
        core_options.set_from_config('swanstation_GPU_ResolutionScale', 'swanstation_resolution_scale', default='1')

        # PGXP Geometry Correction
        core_options.set_from_config('swanstation_GPU_PGXPEnable', 'swanstation_pgxp', default='true')

        # Anti-aliasing (MSAA/SSAA)
        core_options.set_from_config('swanstation_GPU_MSAA', 'swanstation_antialiasing', default='1')

        # Texture Filtering
        core_options.set_from_config(
            'swanstation_GPU_TextureFilter', 'swanstation_texture_filtering', default='Nearest'
        )

        # Widescreen Hack
        if (
            self.config.get('swanstation_widescreen_hack') == 'true'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
        ):
            core_options.set('swanstation_GPU_WidescreenHack', 'true')
            core_options.set('swanstation_Display_AspectRatio', '16:9')
        else:
            core_options.set('swanstation_GPU_WidescreenHack', 'false')
            core_options.set('swanstation_Display_AspectRatio', '4:3')

        # Crop Mode
        core_options.set_from_config('swanstation_Display_CropMode', 'swanstation_CropMode', default='Overscan')

        # Gun crosshairs
        core_options.set_from_config(
            'swanstation_Controller_ShowCrosshair',
            'swanstation_Controller_ShowCrosshair',
            default='true' if self.emulator.guns_need_crosses else 'false',
        )


@cached_dataclass
class Swanstation(Duckstation):
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('swanstation_Controller1', '1')

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('swanstation_Controller2', '1')

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1:
            return '1' if self.config.get_str('swanstation_Controller1', '1') in {'261', '517'} else '0'
        if controller.player_number == 2:
            return '1' if self.config.get_str('swanstation_Controller2', '1') in {'261', '517'} else '0'
        return super().get_analog_mode(controller)

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
        custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', 3)
