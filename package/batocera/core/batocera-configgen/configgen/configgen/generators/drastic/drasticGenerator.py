from __future__ import annotations

import os
import shutil
from os import environ
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class DrasticGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "drastic",
            "keys": {
                "exit": "KEY_ESC",
                "save_state": "KEY_F5",
                "restore_state": "KEY_F7",
                "menu": "KEY_F1",
                "fastforward": "KEY_TAB",
                "swap_screen": "KEY_F2"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        drastic_root = CONFIGS / "drastic"
        drastic_bin = drastic_root / "drastic"
        drastic_conf = drastic_root / "config" / "drastic.cfg"

        mkdir_if_not_exists(drastic_root)
        mkdir_if_not_exists(drastic_conf.parent)

        if not drastic_bin.exists():
            shutil.copytree("/usr/share/drastic", drastic_root, dirs_exist_ok=True)
            drastic_bin.chmod(0o0775)

        # Base template defaults
        config_dict = {
            "show_frame_counter": "0",
            "enable_sound": "1",
            "compress_savestates": "1",
            "savestate_snapshot": "1",
            "firmware.username": "Batocera",
            "firmware.language": str(getDrasticLangFromEnvironment()),
            "firmware.favorite_color": "11",
            "firmware.birthday_month": "11",
            "firmware.birthday_day": "25",
            "enable_cheats": "1",
            "rtc_system_time": "1",
            "use_rtc_custom_time": "0",
            "rtc_custom_time": "0",
            "frameskip_type": "0",
            "frameskip_value": "1",
            "safe_frameskip": "1",
            "disable_edge_marking": "1",
            "fix_main_2d_screen": "0",
            "hires_3d": "0",
            "threaded_3d": "0",
            "screen_orientation": "0",  # default to vertical (0)
            "screen_scaling": "0",
            "screen_swap": "0"
        }

        # Base Slot A default mappings (Keyboard/System)
        controls_a_defaults = {
            "controls_a[CONTROL_INDEX_UP]": "338",
            "controls_a[CONTROL_INDEX_DOWN]": "337",
            "controls_a[CONTROL_INDEX_LEFT]": "336",
            "controls_a[CONTROL_INDEX_RIGHT]": "335",
            "controls_a[CONTROL_INDEX_A]": "32",
            "controls_a[CONTROL_INDEX_B]": "480",
            "controls_a[CONTROL_INDEX_X]": "122",
            "controls_a[CONTROL_INDEX_Y]": "120",
            "controls_a[CONTROL_INDEX_L]": "481",
            "controls_a[CONTROL_INDEX_R]": "99",
            "controls_a[CONTROL_INDEX_START]": "13",
            "controls_a[CONTROL_INDEX_SELECT]": "485",
            "controls_a[CONTROL_INDEX_HINGE]": "104",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_UP]": "65535",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_DOWN]": "65535",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_LEFT]": "65535",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]": "65535",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_PRESS]": "65535",
            "controls_a[CONTROL_INDEX_MENU]": "109",
            "controls_a[CONTROL_INDEX_SAVE_STATE]": "318",
            "controls_a[CONTROL_INDEX_LOAD_STATE]": "320",
            "controls_a[CONTROL_INDEX_FAST_FORWARD]": "8",
            "controls_a[CONTROL_INDEX_SWAP_SCREENS]": "115",
            "controls_a[CONTROL_INDEX_SWAP_ORIENTATION_A]": "97",
            "controls_a[CONTROL_INDEX_SWAP_ORIENTATION_B]": "100",
            "controls_a[CONTROL_INDEX_LOAD_GAME]": "65535",
            "controls_a[CONTROL_INDEX_QUIT]": "65535",
            "controls_a[CONTROL_INDEX_FAKE_MICROPHONE]": "65535",
            "controls_a[CONTROL_INDEX_UI_UP]": "338",
            "controls_a[CONTROL_INDEX_UI_DOWN]": "337",
            "controls_a[CONTROL_INDEX_UI_LEFT]": "336",
            "controls_a[CONTROL_INDEX_UI_RIGHT]": "335",
            "controls_a[CONTROL_INDEX_UI_SELECT]": "13",
            "controls_a[CONTROL_INDEX_UI_BACK]": "8",
            "controls_a[CONTROL_INDEX_UI_EXIT]": "27",
            "controls_a[CONTROL_INDEX_UI_PAGE_UP]": "331",
            "controls_a[CONTROL_INDEX_UI_PAGE_DOWN]": "334",
            "controls_a[CONTROL_INDEX_UI_SWITCH]": "481"
        }
        config_dict.update(controls_a_defaults)

        # Merge existing cfg file contents if it exists to preserve user values
        if drastic_conf.exists():
            try:
                with drastic_conf.open("r", encoding="ascii", errors="ignore") as conf_file:
                    for line in conf_file:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            config_dict[k.strip()] = v.strip()
            except Exception:
                pass

        # Safe parsing for screen orientation configuration
        drastic_orient = system.config.get("drastic_screen_orientation", "0")
        if not drastic_orient or drastic_orient == "auto" or drastic_orient == "none":
            esvaluedrasticscreenorientation = "0"
        else:
            try:
                esvaluedrasticscreenorientation = str(int(drastic_orient))
            except ValueError:
                esvaluedrasticscreenorientation = "0"

        # Enforce Front-End menu settings
        config_dict["frameskip_type"] = str(system.config.get_int("drastic_frameskip_type", 0))
        config_dict["frameskip_value"] = str(system.config.get_int("drastic_frameskip_value", 1))
        config_dict["fix_main_2d_screen"] = str(system.config.get_int("drastic_fix2d", 0))
        config_dict["hires_3d"] = str(system.config.get_int("drastic_hires", 0))
        config_dict["threaded_3d"] = str(system.config.get_int("drastic_threaded", 0))
        config_dict["screen_orientation"] = esvaluedrasticscreenorientation

        # Generate Slot B controller mappings
        mappings_b = {
            "controls_b[CONTROL_INDEX_UP]": "65535",
            "controls_b[CONTROL_INDEX_DOWN]": "65535",
            "controls_b[CONTROL_INDEX_LEFT]": "65535",
            "controls_b[CONTROL_INDEX_RIGHT]": "65535",
            "controls_b[CONTROL_INDEX_A]": "65535",
            "controls_b[CONTROL_INDEX_B]": "65535",
            "controls_b[CONTROL_INDEX_X]": "65535",
            "controls_b[CONTROL_INDEX_Y]": "65535",
            "controls_b[CONTROL_INDEX_L]": "65535",
            "controls_b[CONTROL_INDEX_R]": "65535",
            "controls_b[CONTROL_INDEX_START]": "65535",
            "controls_b[CONTROL_INDEX_SELECT]": "65535",
            "controls_b[CONTROL_INDEX_HINGE]": "65535",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_UP]": "65535",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_DOWN]": "65535",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_LEFT]": "65535",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]": "65535",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_PRESS]": "65535",
            "controls_b[CONTROL_INDEX_MENU]": "65535",
            "controls_b[CONTROL_INDEX_SAVE_STATE]": "65535",
            "controls_b[CONTROL_INDEX_LOAD_STATE]": "65535",
            "controls_b[CONTROL_INDEX_FAST_FORWARD]": "65535",
            "controls_b[CONTROL_INDEX_SWAP_SCREENS]": "65535",
            "controls_b[CONTROL_INDEX_SWAP_ORIENTATION_A]": "65535",
            "controls_b[CONTROL_INDEX_SWAP_ORIENTATION_B]": "65535",
            "controls_b[CONTROL_INDEX_LOAD_GAME]": "65535",
            "controls_b[CONTROL_INDEX_QUIT]": "65535",
            "controls_b[CONTROL_INDEX_FAKE_MICROPHONE]": "65535",
            "controls_b[CONTROL_INDEX_UI_UP]": "65535",
            "controls_b[CONTROL_INDEX_UI_DOWN]": "65535",
            "controls_b[CONTROL_INDEX_UI_LEFT]": "65535",
            "controls_b[CONTROL_INDEX_UI_RIGHT]": "65535",
            "controls_b[CONTROL_INDEX_UI_SELECT]": "65535",
            "controls_b[CONTROL_INDEX_UI_BACK]": "65535",
            "controls_b[CONTROL_INDEX_UI_EXIT]": "65535",
            "controls_b[CONTROL_INDEX_UI_PAGE_UP]": "65535",
            "controls_b[CONTROL_INDEX_UI_PAGE_DOWN]": "65535",
            "controls_b[CONTROL_INDEX_UI_SWITCH]": "65535"
        }

        # Extract Player 1's controller config safely
        controller = None
        if isinstance(playersControllers, dict):
            if "1" in playersControllers:
                controller = playersControllers["1"]  # pyright: ignore[reportArgumentType, reportCallIssue]
            elif playersControllers:
                controller = playersControllers[sorted(playersControllers.keys())[0]]
        elif isinstance(playersControllers, list) and playersControllers:
            controller = playersControllers[0]

        if controller:
            inputs = controller.inputs

            def get_btn_or_hat_val(input_name: str) -> str:
                if input_name not in inputs:
                    return "65535"
                inp = inputs[input_name]
                if inp.type == "button":
                    return str(1024 + int(inp.id))
                if inp.type == "hat":
                    hat_masks = {"up": 1, "right": 2, "down": 4, "left": 8}
                    return str(1088 + hat_masks.get(inp.name, 0))
                return "65535"

            # D-pad Directions
            mappings_b["controls_b[CONTROL_INDEX_UP]"] = get_btn_or_hat_val("up")
            mappings_b["controls_b[CONTROL_INDEX_DOWN]"] = get_btn_or_hat_val("down")
            mappings_b["controls_b[CONTROL_INDEX_LEFT]"] = get_btn_or_hat_val("left")
            mappings_b["controls_b[CONTROL_INDEX_RIGHT]"] = get_btn_or_hat_val("right")
            # Face Buttons
            mappings_b["controls_b[CONTROL_INDEX_A]"] = get_btn_or_hat_val("a")
            mappings_b["controls_b[CONTROL_INDEX_B]"] = get_btn_or_hat_val("b")
            mappings_b["controls_b[CONTROL_INDEX_X]"] = get_btn_or_hat_val("x")
            mappings_b["controls_b[CONTROL_INDEX_Y]"] = get_btn_or_hat_val("y")
            # Shoulder/Trigger mappings (L2 / R2)
            mappings_b["controls_b[CONTROL_INDEX_L]"] = get_btn_or_hat_val("l2")
            mappings_b["controls_b[CONTROL_INDEX_R]"] = get_btn_or_hat_val("r2")
            # Start and Select
            mappings_b["controls_b[CONTROL_INDEX_START]"] = get_btn_or_hat_val("start")
            mappings_b["controls_b[CONTROL_INDEX_SELECT]"] = get_btn_or_hat_val("select")
            # Hotkeys: Swap Screen (pageup/L1), Fast Forward (pagedown/R1)
            mappings_b["controls_b[CONTROL_INDEX_SWAP_SCREENS]"] = get_btn_or_hat_val("pageup")
            mappings_b["controls_b[CONTROL_INDEX_FAST_FORWARD]"] = get_btn_or_hat_val("pagedown")
            # Stylus Tracking (Always Left Analog Stick)
            if "joystick1left" in inputs and "joystick1up" in inputs:
                x_inp = inputs["joystick1left"]
                y_inp = inputs["joystick1up"]
                x_axis_id = int(x_inp.id)
                y_axis_id = int(y_inp.id)

                mappings_b["controls_b[CONTROL_INDEX_TOUCH_CURSOR_LEFT]"] = str(1216 + x_axis_id)
                mappings_b["controls_b[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]"] = str(1152 + x_axis_id)
                mappings_b["controls_b[CONTROL_INDEX_TOUCH_CURSOR_UP]"] = str(1216 + y_axis_id)
                mappings_b["controls_b[CONTROL_INDEX_TOUCH_CURSOR_DOWN]"] = str(1152 + y_axis_id)
            # Stylus press mapped to L3 (Left Stick)
            mappings_b["controls_b[CONTROL_INDEX_TOUCH_CURSOR_PRESS]"] = get_btn_or_hat_val("l3")
            # Menu mapped to R3 (Right Stick). If not some fallbacks
            menu_val = get_btn_or_hat_val("r3")
            if menu_val == "65535":
                menu_val = get_btn_or_hat_val("hotkey")
            if menu_val == "65535":
                menu_val = get_btn_or_hat_val("select")
            mappings_b["controls_b[CONTROL_INDEX_MENU]"] = menu_val
            # UI Navigation Mirror mappings
            mappings_b["controls_b[CONTROL_INDEX_UI_UP]"] = mappings_b["controls_b[CONTROL_INDEX_UP]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_DOWN]"] = mappings_b["controls_b[CONTROL_INDEX_DOWN]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_LEFT]"] = mappings_b["controls_b[CONTROL_INDEX_LEFT]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_RIGHT]"] = mappings_b["controls_b[CONTROL_INDEX_RIGHT]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_SELECT]"] = mappings_b["controls_b[CONTROL_INDEX_A]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_BACK]"] = mappings_b["controls_b[CONTROL_INDEX_X]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_EXIT]"] = mappings_b["controls_b[CONTROL_INDEX_B]"]
            mappings_b["controls_b[CONTROL_INDEX_UI_PAGE_UP]"] = get_btn_or_hat_val("pagedown")  # R1 to page down
            mappings_b["controls_b[CONTROL_INDEX_UI_PAGE_DOWN]"] = get_btn_or_hat_val("pageup")  # L1 to page up
            mappings_b["controls_b[CONTROL_INDEX_UI_SWITCH]"] = mappings_b["controls_b[CONTROL_INDEX_Y]"]

        # Overwrite/merge calculations into config dictionary
        config_dict.update(mappings_b)

        # Write final key-value pairs back to config file
        with drastic_conf.open("w", encoding="ascii") as f:
            for k, v in config_dict.items():
                f.write(f"{k} = {v}\n")

        os.chdir(drastic_root)
        commandArray = [drastic_bin, rom]

        # Base environment setup
        cmd_env = {
            'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
            'LD_PRELOAD': '/usr/lib/libdrastouch.so',
            'SDL_TOUCH_MOUSE_EVENTS': '0',
        }

        # Apply screen shader if configured and not set to None/none
        drastic_shader = system.config.get("drastic_shader", "none")
        if drastic_shader and drastic_shader != "none":
            cmd_env['DSHOOK_SHADER'] = drastic_shader

        # Apply microphone threshold if configured and enabled
        drastic_mic = system.config.get("drastic_mic_threshold", "0.0")
        try:
            if float(drastic_mic) > 0.0:
                cmd_env['DSHOOK_MIC_THRESH'] = drastic_mic
        except (ValueError, TypeError):
            pass

        return Command.Command(
            array=commandArray,
            env=cmd_env
        )

# Language auto-setting
def getDrasticLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
