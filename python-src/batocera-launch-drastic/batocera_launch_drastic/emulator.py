from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext, InputDict

_SHARE_DIR: Final = Path('/usr/share/drastic')

_LANGUAGE_MAPPING: Final = {
    'ja_JP': 0,
    'en_US': 1,
    'fr_FR': 2,
    'de_DE': 3,
    'it_IT': 4,
    'es_ES': 5,
}

_HAT_MASKS: Final = {
    'up': 1,
    'right': 2,
    'down': 4,
    'left': 8,
}

_DEFAULT_CODE: Final = '65535'

_CONTROLS_B_UNBOUND: Final = {
    'controls_b[CONTROL_INDEX_UP]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_DOWN]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_LEFT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_RIGHT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_A]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_B]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_X]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_Y]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_L]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_R]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_START]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_SELECT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_HINGE]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_TOUCH_CURSOR_UP]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_TOUCH_CURSOR_DOWN]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_TOUCH_CURSOR_LEFT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_TOUCH_CURSOR_PRESS]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_MENU]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_SAVE_STATE]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_LOAD_STATE]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_FAST_FORWARD]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_SWAP_SCREENS]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_SWAP_ORIENTATION_A]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_SWAP_ORIENTATION_B]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_LOAD_GAME]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_QUIT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_FAKE_MICROPHONE]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_UP]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_DOWN]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_LEFT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_RIGHT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_SELECT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_BACK]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_EXIT]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_PAGE_UP]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_PAGE_DOWN]': _DEFAULT_CODE,
    'controls_b[CONTROL_INDEX_UI_SWITCH]': _DEFAULT_CODE,
}


def _button_or_hat_value(inputs: InputDict, input_name: str, /) -> str:
    if (input := inputs.get(input_name)) is None:
        return _DEFAULT_CODE

    if input.type == 'button':
        return str(1024 + int(input.id))

    if input.type == 'hat':
        return str(1088 + _HAT_MASKS.get(input.name, 0))

    return _DEFAULT_CODE


def _read_existing_config(config_file: Path, /) -> dict[str, str]:
    config: dict[str, str] = {}

    if not config_file.exists():
        return config

    try:
        with config_file.open('r', encoding='ascii', errors='ignore') as conf_file:
            for line in conf_file:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    except OSError:
        pass

    return config


def _controls_b_from_inputs(inputs: InputDict, /) -> dict[str, str]:
    mappings = dict(_CONTROLS_B_UNBOUND)

    mappings['controls_b[CONTROL_INDEX_UP]'] = _button_or_hat_value(inputs, 'up')
    mappings['controls_b[CONTROL_INDEX_DOWN]'] = _button_or_hat_value(inputs, 'down')
    mappings['controls_b[CONTROL_INDEX_LEFT]'] = _button_or_hat_value(inputs, 'left')
    mappings['controls_b[CONTROL_INDEX_RIGHT]'] = _button_or_hat_value(inputs, 'right')
    mappings['controls_b[CONTROL_INDEX_A]'] = _button_or_hat_value(inputs, 'a')
    mappings['controls_b[CONTROL_INDEX_B]'] = _button_or_hat_value(inputs, 'b')
    mappings['controls_b[CONTROL_INDEX_X]'] = _button_or_hat_value(inputs, 'x')
    mappings['controls_b[CONTROL_INDEX_Y]'] = _button_or_hat_value(inputs, 'y')
    mappings['controls_b[CONTROL_INDEX_L]'] = _button_or_hat_value(inputs, 'l2')
    mappings['controls_b[CONTROL_INDEX_R]'] = _button_or_hat_value(inputs, 'r2')
    mappings['controls_b[CONTROL_INDEX_START]'] = _button_or_hat_value(inputs, 'start')
    mappings['controls_b[CONTROL_INDEX_SELECT]'] = _button_or_hat_value(inputs, 'select')
    mappings['controls_b[CONTROL_INDEX_SWAP_SCREENS]'] = _button_or_hat_value(inputs, 'pageup')
    mappings['controls_b[CONTROL_INDEX_FAST_FORWARD]'] = _button_or_hat_value(inputs, 'pagedown')

    if 'joystick1left' in inputs and 'joystick1up' in inputs:
        x_axis_id = int(inputs['joystick1left'].id)
        y_axis_id = int(inputs['joystick1up'].id)
        mappings['controls_b[CONTROL_INDEX_TOUCH_CURSOR_LEFT]'] = str(1216 + x_axis_id)
        mappings['controls_b[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]'] = str(1152 + x_axis_id)
        mappings['controls_b[CONTROL_INDEX_TOUCH_CURSOR_UP]'] = str(1216 + y_axis_id)
        mappings['controls_b[CONTROL_INDEX_TOUCH_CURSOR_DOWN]'] = str(1152 + y_axis_id)

    mappings['controls_b[CONTROL_INDEX_TOUCH_CURSOR_PRESS]'] = _button_or_hat_value(inputs, 'l3')

    menu_val = _button_or_hat_value(inputs, 'r3')
    if menu_val == _DEFAULT_CODE:
        menu_val = _button_or_hat_value(inputs, 'hotkey')
    if menu_val == _DEFAULT_CODE:
        menu_val = _button_or_hat_value(inputs, 'select')
    mappings['controls_b[CONTROL_INDEX_MENU]'] = menu_val

    mappings['controls_b[CONTROL_INDEX_UI_UP]'] = mappings['controls_b[CONTROL_INDEX_UP]']
    mappings['controls_b[CONTROL_INDEX_UI_DOWN]'] = mappings['controls_b[CONTROL_INDEX_DOWN]']
    mappings['controls_b[CONTROL_INDEX_UI_LEFT]'] = mappings['controls_b[CONTROL_INDEX_LEFT]']
    mappings['controls_b[CONTROL_INDEX_UI_RIGHT]'] = mappings['controls_b[CONTROL_INDEX_RIGHT]']
    mappings['controls_b[CONTROL_INDEX_UI_SELECT]'] = mappings['controls_b[CONTROL_INDEX_A]']
    mappings['controls_b[CONTROL_INDEX_UI_BACK]'] = mappings['controls_b[CONTROL_INDEX_X]']
    mappings['controls_b[CONTROL_INDEX_UI_EXIT]'] = mappings['controls_b[CONTROL_INDEX_B]']
    mappings['controls_b[CONTROL_INDEX_UI_PAGE_UP]'] = _button_or_hat_value(inputs, 'pagedown')
    mappings['controls_b[CONTROL_INDEX_UI_PAGE_DOWN]'] = _button_or_hat_value(inputs, 'pageup')
    mappings['controls_b[CONTROL_INDEX_UI_SWITCH]'] = mappings['controls_b[CONTROL_INDEX_Y]']

    return mappings


@cached_dataclass
class Drastic(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'drastic',
            'keys': {
                'exit': 'KEY_ESC',
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F7',
                'menu': 'KEY_F1',
                'fastforward': 'KEY_TAB',
                'swap_screen': 'KEY_F2',
            },
        }

    @property
    def execution_path(self) -> Path | None:
        return self.config_dir

    async def configure(self) -> Command:
        bin_path = self.config_dir / 'drastic'
        config_file = self.config_dir / 'config' / 'drastic.cfg'

        config_file.parent.mkdir(parents=True, exist_ok=True)

        if not bin_path.exists():
            shutil.copytree(_SHARE_DIR, self.config_dir, dirs_exist_ok=True)
            bin_path.chmod(0o0775)

        config = {
            'show_frame_counter': '0',
            'enable_sound': '1',
            'compress_savestates': '1',
            'savestate_snapshot': '1',
            'firmware.username': 'Batocera',
            'firmware.favorite_color': '11',
            'firmware.birthday_month': '11',
            'firmware.birthday_day': '25',
            'enable_cheats': '1',
            'rtc_system_time': '1',
            'use_rtc_custom_time': '0',
            'rtc_custom_time': '0',
            'frameskip_type': '0',
            'frameskip_value': '1',
            'safe_frameskip': '1',
            'disable_edge_marking': '1',
            'fix_main_2d_screen': '0',
            'hires_3d': '0',
            'threaded_3d': '0',
            'screen_orientation': '0',
            'screen_scaling': '0',
            'screen_swap': '0',
            'controls_a[CONTROL_INDEX_UP]': '338',
            'controls_a[CONTROL_INDEX_DOWN]': '337',
            'controls_a[CONTROL_INDEX_LEFT]': '336',
            'controls_a[CONTROL_INDEX_RIGHT]': '335',
            'controls_a[CONTROL_INDEX_A]': '32',
            'controls_a[CONTROL_INDEX_B]': '480',
            'controls_a[CONTROL_INDEX_X]': '122',
            'controls_a[CONTROL_INDEX_Y]': '120',
            'controls_a[CONTROL_INDEX_L]': '481',
            'controls_a[CONTROL_INDEX_R]': '99',
            'controls_a[CONTROL_INDEX_START]': '13',
            'controls_a[CONTROL_INDEX_SELECT]': '485',
            'controls_a[CONTROL_INDEX_HINGE]': '104',
            'controls_a[CONTROL_INDEX_TOUCH_CURSOR_UP]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_TOUCH_CURSOR_DOWN]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_TOUCH_CURSOR_LEFT]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_TOUCH_CURSOR_PRESS]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_MENU]': '109',
            'controls_a[CONTROL_INDEX_SAVE_STATE]': '318',
            'controls_a[CONTROL_INDEX_LOAD_STATE]': '320',
            'controls_a[CONTROL_INDEX_FAST_FORWARD]': '8',
            'controls_a[CONTROL_INDEX_SWAP_SCREENS]': '115',
            'controls_a[CONTROL_INDEX_SWAP_ORIENTATION_A]': '97',
            'controls_a[CONTROL_INDEX_SWAP_ORIENTATION_B]': '100',
            'controls_a[CONTROL_INDEX_LOAD_GAME]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_QUIT]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_FAKE_MICROPHONE]': _DEFAULT_CODE,
            'controls_a[CONTROL_INDEX_UI_UP]': '338',
            'controls_a[CONTROL_INDEX_UI_DOWN]': '337',
            'controls_a[CONTROL_INDEX_UI_LEFT]': '336',
            'controls_a[CONTROL_INDEX_UI_RIGHT]': '335',
            'controls_a[CONTROL_INDEX_UI_SELECT]': '13',
            'controls_a[CONTROL_INDEX_UI_BACK]': '8',
            'controls_a[CONTROL_INDEX_UI_EXIT]': '27',
            'controls_a[CONTROL_INDEX_UI_PAGE_UP]': '331',
            'controls_a[CONTROL_INDEX_UI_PAGE_DOWN]': '334',
            'controls_a[CONTROL_INDEX_UI_SWITCH]': '481',
            'firmware.language': str(_LANGUAGE_MAPPING.get(self.config.get_str('system.language', 'en_US'), 1)),
            **_read_existing_config(config_file),
        }

        # Safe parsing for screen orientation configuration
        orientation = self.config.get_str('drastic_screen_orientation', '0')
        if not orientation or orientation in {'auto', 'none'}:
            screen_orientation = '0'
        else:
            try:
                screen_orientation = str(int(orientation))
            except ValueError:
                screen_orientation = '0'

        # Enforce front-end menu settings
        config.update(
            {
                'frameskip_type': str(self.config.get_int('drastic_frameskip_type', 0)),
                'frameskip_value': str(self.config.get_int('drastic_frameskip_value', 1)),
                'fix_main_2d_screen': str(self.config.get_int('drastic_fix2d', 0)),
                'hires_3d': str(self.config.get_int('drastic_hires', 0)),
                'threaded_3d': str(self.config.get_int('drastic_threaded', 0)),
                'screen_orientation': screen_orientation,
            }
        )

        # Generate Slot B controller mappings
        config.update(_controls_b_from_inputs(self.controllers[0].inputs) if self.controllers else _CONTROLS_B_UNBOUND)

        with config_file.open('w', encoding='ascii') as conf_file:
            for key, value in config.items():
                conf_file.write(f'{key} = {value}\n')

        env: dict[str, str | Path] = {
            'LD_PRELOAD': '/usr/lib/libdrastouch.so',
            'SDL_TOUCH_MOUSE_EVENTS': '0',
        }

        if (shader := self.config.get_str('drastic_shader', 'none')) and shader != 'none':
            env['DSHOOK_SHADER'] = shader

        try:
            mic_threshold = float(self.config.get_str('drastic_mic_threshold', '0.0'))
        except TypeError, ValueError:
            mic_threshold = 0.0

        if mic_threshold > 0.0:
            env['DSHOOK_MIC_THRESH'] = str(mic_threshold)

        return Command([bin_path, self.rom], env=env)
