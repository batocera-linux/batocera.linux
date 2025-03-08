from __future__ import annotations

import filecmp
import json
import shutil
from os import environ
from typing import TYPE_CHECKING, Any, Final

import evdev

from ... import Command
from ...batoceraPaths import BIOS, CACHE, CONFIGS, ROMS, SAVES, configure_emulator, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

ryujinxConf: Final = CONFIGS / "Ryujinx"
ryujinxConfFile: Final = ryujinxConf / "Config.json"
ryujinxKeys: Final = BIOS / "switch" / "prod.keys"
ryujinxExec: Final = ryujinxConf / "ryujinx"

ryujinxCtrl: dict[str, Any] = {
        "left_joycon_stick": {
        "joystick": "Left",
        "invert_stick_x": False,
        "invert_stick_y": False,
        "rotate90_cw": False,
        "stick_button": "LeftStick"
      },
      "right_joycon_stick": {
        "joystick": "Right",
        "invert_stick_x": False,
        "invert_stick_y": False,
        "rotate90_cw": False,
        "stick_button": "RightStick"
      },
      "deadzone_left": 0,
      "deadzone_right": 0,
      "range_left": 1,
      "range_right": 1,
      "trigger_threshold": 0,
      "motion": {
        "motion_backend": "GamepadDriver",
        "sensitivity": 100,
        "gyro_deadzone": 1,
        "enable_motion": True
      },
      "rumble": {
        "strong_rumble": 8,
        "weak_rumble": 2,
        "enable_rumble": True
      },
      "left_joycon": {
        "button_minus": "Minus",
        "button_l": "LeftShoulder",
        "button_zl": "LeftTrigger",
        "button_sl": "Unbound",
        "button_sr": "Unbound",
        "dpad_up": "DpadUp",
        "dpad_down": "DpadDown",
        "dpad_left": "DpadLeft",
        "dpad_right": "DpadRight"
      },
      "right_joycon": {
        "button_plus": "Plus",
        "button_r": "RightShoulder",
        "button_zr": "RightTrigger",
        "button_sl": "Unbound",
        "button_sr": "Unbound",
        "button_x": "Y",
        "button_b": "A",
        "button_y": "X",
        "button_a": "B"
    },
    "version": 1,
    "backend": "GamepadSDL2",
}

class RyujinxGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ryujinx",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(ryujinxConf / "system")

        # Copy file & make executable (workaround)
        files_to_copy = [
            ("/usr/ryujinx/Ryujinx", ryujinxExec, 0o0775),
            ("/usr/ryujinx/libSkiaSharp.so", ryujinxConf / "libSkiaSharp.so", 0o0644),
            ("/usr/ryujinx/libHarfBuzzSharp.so", ryujinxConf / "libHarfBuzzSharp.so", 0o0644)
        ]

        for src, dest, mode in files_to_copy:
            if not dest.exists() or not filecmp.cmp(src, dest):
                shutil.copyfile(src, dest)
                dest.chmod(mode)

        # Copy the prod.keys file to where ryujinx reads it
        if ryujinxKeys.exists():
            shutil.copyfile(ryujinxKeys, ryujinxConf / "system" / "prod.keys")

        # [Configuration]
        mkdir_if_not_exists(ryujinxConfFile.parent)
        try:
            conf = json.load(ryujinxConfFile.open("r"))
        except Exception:
            conf = {}

        # Set defaults
        conf["enable_discord_integration"] = False
        conf["check_updates_on_start"] = False
        conf["show_confirm_exit"] = False
        conf["hide_cursor_on_idle"] = True
        conf["game_dirs"] = [str(ROMS / "switch")]
        conf["start_fullscreen"] = True
        conf["docked_mode"] = True
        conf["audio_backend"] = "OpenAl"
        conf["audio_volume"] = 1
        # set ryujinx app language
        conf["language_code"] = str(getLangFromEnvironment())

        # Console language, time & date
        conf["system_language"] = system.config.get("ryujinx_language", "AmericanEnglish")
        conf["system_region"] = system.config.get("ryujinx_region", "USA")

        conf["system_time_zone"] = "UTC"
        conf["system_time_offset"] = system.config.get_int("ryujinx_timeoffset", 0)

        # Graphics
        conf["graphics_backend"] = system.config.get("ryujinx_api", "Vulkan")
        conf["res_scale"] = system.config.get_int("ryujinx_scale", 1)
        conf["aspect_ratio"] = system.config.get("ryujinx_ratio", "Fixed16x9")
        conf["max_anisotropy"] = system.config.get_int("ryujinx_filtering", -1)

        conf["input_config"] = []

        # write / update the config file
        js_out = json.dumps(conf, indent=2)
        with ryujinxConfFile.open("w") as jout:
            jout.write(js_out)

        # Now add Controllers
        for nplayer, pad in enumerate(playersControllers[:8], start=1):
            ctrlConf = ryujinxCtrl
            # we need to get the uuid for ryujinx controllers
            # example xbox 360 - "id": "0-00000003-045e-0000-8e02-000014010000"
            devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
            for dev in devices:
                if dev.path == pad.device_path:
                    bustype = f"{dev.info.bustype:x}"
                    bustype = bustype.zfill(8)
                    vendor = f"{dev.info.vendor:x}"
                    vendor = vendor.zfill(4)
                    product = f"{dev.info.product:x}"
                    product = product.zfill(4)
                    # reverse the poduct id, so 028e becomes 8e02
                    product1 = (product)[-2::]
                    product2 = (product)[:-2]
                    product = product1 + product2
                    # reverse the version id also
                    version = f"{dev.info.version:x}"
                    version = version.zfill(4)
                    version1 = (version)[-2::]
                    version2 = (version)[:-2]
                    version = version1 + version2
                    ctrlUUID = (f"{pad.index}-{bustype}-{vendor}-0000-{product}-0000{version}0000")
                    ctrlConf["id"] = ctrlUUID
                    # always configure a pro controller for now
                    ctrlConf["controller_type"] = "ProController"
                    playerNum = (f"Player{nplayer}")
                    ctrlConf["player_index"] = playerNum
                    # write the controller to the file
                    writeControllerIntoJson(ctrlConf)
                    break

        if configure_emulator(rom):
            commandArray = [ryujinxExec]
        else:
            commandArray = [ryujinxExec, rom]

        return Command.Command(
            array=commandArray,
            env={"XDG_CONFIG_HOME":CONFIGS, \
            "XDG_DATA_HOME":SAVES / "switch", \
            "XDG_CACHE_HOME":CACHE, \
            "QT_QPA_PLATFORM":"xcb", \
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)})

def writeControllerIntoJson(new_controller: dict[str, Any], filename: Path = ryujinxConfFile):
    with filename.open('r+') as file:
        file_data = json.load(file)
        file_data["input_config"].append(new_controller)
        file.seek(0)
        json.dump(file_data, file, indent=2)

def getLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "jp_JP": 0, "en_US": 1, "de_DE": 2,
                           "fr_FR": 3, "es_ES": 4, "it_IT": 5,
                           "nl_NL": 6, "zh_CN": 7, "zh_TW": 8, "ko_KR": 9 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
