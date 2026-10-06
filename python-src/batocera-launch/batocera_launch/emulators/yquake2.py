from __future__ import annotations

import platform
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Controller, Emulator, HotkeysContext

_DEFAULT_OPTIONS: Final = {
    # Special keys for hotkey shortcuts
    'bind PRINT': 'screenshot jpg 90',
    'bind MENU': 'menu_joy',
    # Default gamepad controls
    'bind SHOULDR_LEFT': '+movedown',
    'bind TRIG_LEFT': '+moveup',
    'bind SHOULDR_RIGHT': '+joyaltselector',
    'bind TRIG_RIGHT': '+attack',
    'bind BTN_SOUTH': '+moveup',
    'bind BTN_EAST': '+movedown',
    'bind BTN_WEST': 'weapnext',
    'bind BTN_NORTH': 'weapprev',
    'bind BTN_BACK': 'cmd help',
    'bind BTN_GUIDE': '',
    'bind STICK_LEFT': '',
    'bind STICK_RIGHT': 'centerview',
    'bind DP_UP': (
        'cycleweap weapon_plasmabeam weapon_boomer weapon_chaingun weapon_etf_rifle weapon_machinegun weapon_blaster'
    ),
    'bind DP_DOWN': 'cycleweap weapon_supershotgun weapon_shotgun weapon_chainfist',
    'bind DP_LEFT': (
        'cycleweap weapon_phalanx weapon_rocketlauncher weapon_proxlauncher weapon_grenadelauncher ammo_grenades'
    ),
    'bind DP_RIGHT': (
        'cycleweap weapon_bfg weapon_disintegrator weapon_railgun weapon_hyperblaster ammo_tesla ammo_trap'
    ),
    'bind BTN_WEST_ALT': 'invuse',
    'bind BTN_NORTH_ALT': 'invdrop',
    'bind BTN_BACK_ALT': 'inven',
    'bind DP_UP_ALT': 'invprev',
    'bind DP_DOWN_ALT': 'invnext',
    'bind DP_LEFT_ALT': 'invprev',
    'bind DP_RIGHT_ALT': 'invnext',
    # Gameplay options, check YQ2 documentation
    'set aimfix': '1',
    'set cl_run': '1',
    'set g_machinegun_norecoil': '1',
    'set g_quick_weap': '1',
    'set g_swap_speed': '2',
    # Audio & Video
    'set ogg_ignoretrack0': '1',
    'set gl_znear': '3.2',
    'set vid_fullscreen': '1',
    'set r_mode': '-2',
}


def _cpu_max_mhz() -> int:
    try:
        for path in Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/cpuinfo_max_freq'):
            return int(path.read_text().strip()) // 1000
    except OSError, ValueError:
        pass
    return 0


def _is_pc() -> bool:
    return platform.machine().lower().startswith('x86')


@cached_dataclass
class YQuake2(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'yquake2',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F9',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.resolution.width / self.resolution.height > ((16.0 / 9.0) - 0.1) else 4 / 3

    def _create_default_config(self) -> None:
        config_file = self.config_dir / 'baseq2' / 'yq2.cfg'
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Define the default options to add
        options = dict(_DEFAULT_OPTIONS)

        # Disable OpenAL on slow CPUs
        if _cpu_max_mhz() < 2000:
            options['set s_openal'] = '0'

        if not _is_pc():
            options['set gl1_discardfb'] = '1'
            options['set gl1_lightmapcopies'] = '1'
            options['set gl1_pointparameters'] = '0'

        config_file.write_text(''.join(f'{key} "{value}"\n' for key, value in options.items()))

    async def configure(self) -> Command:
        config_file = self.config_dir / 'baseq2' / 'yq2.cfg'
        if not config_file.exists():
            self._create_default_config()

        swap_buttons = '1' if self.es_settings.get_bool('InvertButtons') else '0'
        args: list[str | Path] = [
            '/usr/bin/yquake2/quake2',
            '-cfgdir',
            'configs/yquake2',
            '+set',
            'joy_confirm',
            swap_buttons,
        ]

        if pad := Controller.find_player_number(self.controllers, 1):
            args.extend(['+set', 'in_initjoy', str(pad.index + 1)])

        # Mission Packs
        rom_name = self.rom.name.lower()
        if 'reckoning' in rom_name:
            args.extend(['+set', 'game', 'xatrix'])
        elif 'zero' in rom_name:
            args.extend(['+set', 'game', 'rogue'])
        elif 'zaero' in rom_name:
            args.extend(['+set', 'game', 'zaero'])

        return Command(args, env={'SDL_JOYSTICK_HIDAPI': '0'})
