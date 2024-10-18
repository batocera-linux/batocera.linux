from __future__ import annotations

import filecmp
import json
import shutil
from os import environ
from typing import TYPE_CHECKING, Final

import evdev
from evdev import InputDevice

from ... import Command
from ...batoceraPaths import BIOS, CACHE, CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

ryujinxConf: Final = CONFIGS / "Ryujinx"
ryujinxConfFile: Final = ryujinxConf / "Config.json"
ryujinxKeys: Final = BIOS / "switch" / "prod.keys"
ryujinxExec: Final = ryujinxConf / "ryujinx"

ryujinxCtrl = {
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
        except:
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
        if system.isOptSet("ryujinx_language"):
            conf["system_language"] = system.config["ryujinx_language"]
        else:
            conf["system_language"] = "AmericanEnglish"

        if system.isOptSet("ryujinx_region"):
            conf["system_region"] = system.config["ryujinx_region"]
        else:
            conf["system_region"] = "USA"

        conf["system_time_zone"] = "UTC"
        if system.isOptSet("ryujinx_timeoffset"):
            conf["system_time_offset"] = int(system.config["ryujinx_timeoffset"])
        else:
            conf["system_time_offset"]= 0

        # Graphics
        if system.isOptSet("ryujinx_api"):
            conf["graphics_backend"] = system.config["ryujinx_api"]
        else:
            conf["graphics_backend"] = "Vulkan"

        if system.isOptSet("ryujinx_scale"):
            conf["res_scale"] = int(system.config["ryujinx_scale"])
        else:
            conf["res_scale"] = 1

        if system.isOptSet("ryujinx_ratio"):
            conf["aspect_ratio"] = system.config["ryujinx_ratio"]
        else:
            conf["aspect_ratio"] = "Fixed16x9"

        if system.isOptSet("ryujinx_filtering"):
            conf["max_anisotropy"] = int(system.config["ryujinx_filtering"])
        else:
            conf["max_anisotropy"] = -1

        conf["input_config"] = []

        # write / update the config file
        js_out = json.dumps(conf, indent=2)
        with ryujinxConfFile.open("w") as jout:
            jout.write(js_out)

        # Now add Controllers
        nplayer = 1
        for controller, pad in sorted(playersControllers.items()):
            if nplayer <= 8:
                ctrlConf = ryujinxCtrl
                # we need to get the uuid for ryujinx controllers
                # example xbox 360 - "id": "0-00000003-045e-0000-8e02-000014010000"
                devices = [InputDevice(fn) for fn in evdev.list_devices()]
                for dev in devices:
                    if dev.path == pad.device_path:
                        bustype = "%x" % dev.info.bustype
                        bustype = bustype.zfill(8)
                        vendor = "%x" % dev.info.vendor
                        vendor = vendor.zfill(4)
                        product = "%x" % dev.info.product
                        product = product.zfill(4)
                        # reverse the poduct id, so 028e becomes 8e02
                        product1 = (product)[-2::]
                        product2 = (product)[:-2]
                        product = product1 + product2
                        # reverse the version id also
                        version = "%x" % dev.info.version
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
            nplayer += 1

        if rom == "config":
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

def writeControllerIntoJson(new_controller, filename: Path = ryujinxConfFile):
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
    else:
        return availableLanguages["en_US"]
