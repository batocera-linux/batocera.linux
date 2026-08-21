from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, GLCoreForceMixin, LibretroConfig


@cached_dataclass
class Pcsx2(GLCoreForceMixin, Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Fast Boot
        core_options.set_from_config('pcsx2_fastboot', 'lr_pcsx2_fast_boot', default='disabled')
        # Fast CD/DVD Access
        core_options.set_from_config('pcsx2_fastcdvd', 'lr_pcsx2_fast_cdvd', default='disabled')
        # Enable Cheats
        core_options.set_from_config('pcsx2_enable_cheats', 'lr_pcsx2_fast_cheats', default='disabled')
        # Language Unlock
        core_options.set_from_config('pcsx2_hint_language_unlock', 'lr_pcsx2_language_unlock', default='disabled')
        # Graphics API
        if self.config.get('gfxbackend') == 'vulkan':
            core_options.set('pcsx2_renderer', 'Vulkan')
        else:
            core_options.set('pcsx2_renderer', 'OpenGL')
        # Render resolution
        core_options.set_from_config('pcsx2_upscale_multiplier', 'lr_pcsx2_resolution', default='1x Native (PS2)')
        # Texture Filtering
        core_options.set_from_config('pcsx2_texture_filtering', 'lr_pcsx2_texture_filtering', default='Bilinear (PS2)')
        # Trilinear Filtering
        core_options.set_from_config('pcsx2_trilinear_filtering', 'lr_pcsx2_trilinear_filtering', default='Automatic')
        # Anisotropic Filtering
        core_options.set_from_config('pcsx2_anisotropic_filtering', 'lr_pcsx2_anisotropic', default='disabled')
        # Dithering
        core_options.set_from_config('pcsx2_dithering', 'lr_pcsx2_dithering', default='Unscaled')
        # Blending Accuracy
        core_options.set_from_config('pcsx2_blending_accuracy', 'lr_pcsx2_blending', default='Basic')
        # Widescreen hint
        widescreenhint = self.config.get('ratio')
        if widescreenhint == '16/9' or widescreenhint == 'full':
            core_options.set('pcsx2_widescreen_hint', 'enabled (16:9)')
        elif widescreenhint == '16/10':
            core_options.set('pcsx2_widescreen_hint', 'enabled (16:10)')
        elif widescreenhint == '21/9':
            core_options.set('pcsx2_widescreen_hint', 'enabled (21:9)')
        elif widescreenhint == '32/9':
            core_options.set('pcsx2_widescreen_hint', 'enabled (32:9)')
        else:
            core_options.set('pcsx2_widescreen_hint', 'disabled')
