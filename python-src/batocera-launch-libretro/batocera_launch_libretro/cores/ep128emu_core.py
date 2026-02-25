from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Ep128emuCore(DisableRunaheadMixin, Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Main thread wait (ms)
        core_options.set_from_config('ep128emu_wait', default='0')
        # High sound quality
        core_options.set_from_config('ep128emu_sdhq', default='1')
        # Use accelerated SW framebuffer
        core_options.set_from_config('ep128emu_swfb', default='0')
        # Enable resolution changes (requires restart)
        core_options.set_from_config('ep128emu_useh', default='1')
        # Border lines to keep when zooming in
        core_options.set_from_config('ep128emu_brds', default='0')
        # System ROM version (EP only)
        core_options.set_from_config('ep128emu_romv', default='Original')
        # User 1 Zoom button
        core_options.set_from_config('ep128emu_zoom', default='R3')
        # User 1 Info button
        core_options.set_from_config('ep128emu_info', default='L3')
        # User 1 Autofire for button
        core_options.set_from_config('ep128emu_afbt', default='None')
        # User 1 Autofire repeat delay
        core_options.set_from_config('ep128emu_afsp', default='1')
