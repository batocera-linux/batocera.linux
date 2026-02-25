from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class DosboxPure(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_dosbox_pure') or None

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_dosbox_pure') or None

    @cached_property
    def rom_argument(self) -> str | Path | None:
        rom = self.rom

        # PURE zip games use the same command as all cores. .pc and .dos use their own.
        if self.system == 'dos' and rom.suffix in {'.dos', '.pc'}:
            stem_bat = rom / f'{rom.stem}.bat'
            if stem_bat.exists() and ' ' not in rom.stem:
                return stem_bat

            dosbox_bat = rom / 'dosbox.bat'
            if dosbox_bat.exists() and not stem_bat.exists():
                return dosbox_bat

        return rom

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        if controller1 := self.config.get('controller1_dosbox_pure'):
            custom_config.set('input_player1_analog_dpad_mode', '3' if controller1 == '3' else '0')

        if controller2 := self.config.get('controller2_dosbox_pure'):
            custom_config.set('input_player2_analog_dpad_mode', '3' if controller2 == '3' else '0')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # allow to read a custom dosbox.conf present in the game directory
        core_options.set('dosbox_pure_conf', 'inside')

        # CPU Type
        cpu_type = self.config.get('pure_cpu_type', 'automatic')
        core_options.set('dosbox_pure_cpu_type', 'auto' if cpu_type == 'automatic' else cpu_type)

        # CPU Core
        cpu_core = self.config.get('pure_cpu_core', 'automatic')
        core_options.set('dosbox_pure_cpu_core', 'auto' if cpu_core == 'automatic' else cpu_core)

        # Emulated performance (CPU Cycles)
        cpu_cycles = self.config.get('pure_cycles', 'automatic')
        core_options.set('dosbox_pure_cycles', 'auto' if cpu_cycles == 'automatic' else cpu_cycles)

        # Graphics Chip type
        core_options.set_from_config('dosbox_pure_machine', 'pure_machine', default='svga')

        # Memory size
        core_options.set_from_config('dosbox_pure_memory_size', 'pure_memory_size', default='16')

        # Save state
        core_options.set_from_config('dosbox_pure_savestate', 'pure_savestate', default='on')

        # Keyboard Layout
        core_options.set_from_config('dosbox_pure_keyboard_layout', 'pure_keyboard_layout', default='us')

        # Automatic Gamepad Mapping
        core_options.set_from_config('dosbox_pure_auto_mapping', 'pure_auto_mapping', default='true')

        # Joystick Analog Deadzone
        core_options.set_from_config(
            'dosbox_pure_joystick_analog_deadzone', 'pure_joystick_analog_deadzone', default='15'
        )

        # Enable Joystick Timed Intervals
        core_options.set_from_config('dosbox_pure_joystick_timed', 'pure_joystick_timed', default='true')

        # SoundBlaster Type
        core_options.set_from_config('dosbox_pure_sblaster_type', 'pure_sblaster_type', default='sb16')

        # Enable Gravis Sound
        core_options.set_from_config('dosbox_pure_gus', 'pure_gravis', default='false')

        # Midi Type
        core_options.set_from_config('dosbox_pure_midi', 'pure_midi', default='disabled')

        # OS Disk Modifications
        core_options.set_from_config('dosbox_pure_bootos_ramdisk', 'pure_bootos_ramdisk', default='false')
