from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Gambatte(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # GB / GBC: Use official Bootlogo
        core_options.set_from_config('gambatte_gb_bootloader', 'gb_bootloader', default='enabled')

        # GB / GBC: Interframe Blending (LCD ghosting effects)
        core_options.set_from_config('gambatte_mix_frames', 'gb_mix_frames', default='disabled')

        if self.system == 'gbc':
            # GBC Color Correction
            core_options.set_from_config('gambatte_gbc_color_correction', 'gbc_color_correction', default='disabled')
        elif self.system == 'gb':
            core_options.set('gambatte_gbc_color_correction', 'disabled')

        if self.system == 'gb':
            # GB: Colorization of GB games
            match self.config.get('gb_colorization', 'GB - DMG'):
                case 'none':  # No Selection --> Classic Green
                    colorization = 'internal'
                    palette = 'Special 1'
                case 'GB - Disabled':  # Disabled --> Black and White Color
                    colorization = 'disabled'
                    palette = 'Special 1'
                case 'GB - SmartColor':  # Smart Coloring --> Gambatte's most colorful/appropriate color
                    colorization = 'auto'
                    palette = 'Special 1'
                case (
                    'GBC - Game Specific'
                ):  # Game specific --> Select automatically a game-specific Game Boy Color palette
                    colorization = 'GBC'
                    palette = 'Special 1'
                case 'custom':  # Custom Palettes --> Use the custom palettes in the bios/palettes folder
                    colorization = 'custom'
                    palette = 'Special 1'
                case _ as gb_colorization:  # User Selection or default (classic green)
                    colorization = 'internal'
                    palette = gb_colorization

            core_options.set('gambatte_gb_colorization', colorization)
            core_options.set('gambatte_gb_internal_palette', palette)
