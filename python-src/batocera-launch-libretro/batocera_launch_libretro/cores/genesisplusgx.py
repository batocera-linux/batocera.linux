from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig, SquashFSMixin

from ._megadrive_core import MegadriveControllerRemapMixin

if TYPE_CHECKING:
    from batocera_launch import Gun


@cached_dataclass
class GenesisPlusGX(SquashFSMixin, MegadriveControllerRemapMixin, Core):
    supports_retroachievements: ClassVar = True
    megadrive_controller_option: ClassVar = 'gx'
    squashfs_rom_globs: ClassVar = {'megadrive-msu': ('*.md',)}
    gun_mapping: ClassVar = {
        'megadrive': {
            'device': 516,
            'p2': 0,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '772'}],
        },
        'mastersystem': {'device': 260, 'p1': 0, 'p2': 1},
        'megacd': {
            'device': 516,
            'p2': 0,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '772'}],
        },
    }

    @cached_property
    def player1_device_type(self) -> str | None:
        if self.system == 'megadrive':
            return self.config.get_str('controller1_md', '513')  # 513 = 6 button
        if self.config.core == 'genesisplusgx' and self.system == 'mastersystem':
            return self.config.get_str('controller1_ms', '769')
        return None

    @cached_property
    def player2_device_type(self) -> str | None:
        if self.system == 'megadrive':
            return self.config.get_str('controller2_md', '513')  # 513 = 6 button
        if self.config.core == 'genesisplusgx' and self.system == 'mastersystem':
            return self.config.get_str('controller2_ms', '769')
        return None

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Allows each game to have its own one brm file for save without lack of space
        core_options.set('genesis_plus_gx_system_bram', 'per game')

        # Sometimes needs to be forced to NTSC-U for MSU-MD to work (this is to avoid an intentionally coded lock-out screen):
        # https://arcadetv.github.io/msu-md-patches/wiki/Lockout-screen.html
        core_options.set_from_config('genesis_plus_region_detect', 'gpgx_region', default='auto')

        # Reduce sprite flickering
        core_options.set_from_config('genesis_plus_gx_no_sprite_limit', 'gpgx_no_sprite_limit', default='disabled')

        # Blargg NTSC filter
        if self.system == 'megadrive':
            ntsc_filter = self.config.get('gpgx_blargg_filter_md', 'Off')
        elif self.system == 'mastersystem':
            ntsc_filter = self.config.get('gpgx_blargg_filter_ms', 'Off')
        else:
            ntsc_filter = 'Off'

        core_options.set('genesis_plus_gx_blargg_ntsc_filter', ntsc_filter)

        # Show Lightgun Crosshair
        if (self.system == 'megadrive' and (cursor := self.config.get('gun_cursor_md'))) or (
            self.system == 'mastersystem' and (cursor := self.config.get('gun_cursor_ms'))
        ):
            gun_cursor = cursor
        else:
            gun_cursor = 'enabled' if self.emulator.guns_need_crosses else 'disabled'

        core_options.set('genesis_plus_gx_gun_cursor', gun_cursor)

        # Megadrive FM (YM2612)
        core_options.set_from_config('genesis_plus_gx_ym2612', 'gpgx_fm', default='mame (ym2612)')

        # system.name == 'mastersystem'
        # Master System FM (YM2413)
        ym2413 = self.config.get('ym2413', 'automatic')
        core_options.set('genesis_plus_gx_ym2413', 'auto' if ym2413 == 'automatic' else ym2413)

        # system.name == 'gamegear'
        # Game Gear LCD Ghosting Filter
        core_options.set_from_config('genesis_plus_gx_lcd_filter', 'lcd_filter', default='disabled')

        # Game Gear Extended Screen
        core_options.set_from_config('genesis_plus_gx_gg_extra', 'gg_extra', default='disabled')

        # system.name == 'msu-md'
        # MSU-MD/MegaCD

        # Needs to be forced to sega/mega cd for MSU-MD to work.
        add_on = self.config.get('gpgx_cd_add_on', 'sega/mega cd' if self.system == 'megadrive-msu' else 'auto')
        core_options.set('genesis_plus_gx_add_on', add_on)

        # Volume setting is actually important, unlike MegaCD the MSU-MD is pre-amped at a different rate.
        # That is, the default level 100 will make the CD audio drown out the cartridge sound effects.
        cdda_volume = self.config.get('gpgx_cdda_volume', '70' if self.system == 'megadrive-msu' else '100')
        core_options.set('genesis_plus_gx_cdda_volume', cdda_volume)

        # gun
        if self.config.use_guns and self.guns:
            core_options.set('genesis_plus_gx_gun_input', 'lightgun')

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_select_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
        custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', 3)
        custom_config.set(f'input_player{player_number}_gun_start_mbtn', 4)


@cached_dataclass
class GenesisPlusGXExpanded(GenesisPlusGX):
    gun_mapping: ClassVar = {
        'megadrive': {
            'device': 516,
            'p2': 0,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '772'}],
        }
    }
