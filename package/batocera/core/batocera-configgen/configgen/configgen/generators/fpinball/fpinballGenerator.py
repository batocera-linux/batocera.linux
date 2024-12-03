from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BIOS, CONFIGS, HOME, mkdir_if_not_exists
from ...utils import wine
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

_FPINBALL_CONFIG: Final = CONFIGS / "fpinball"
_FPINBALL_CONFIG_REG: Final = _FPINBALL_CONFIG / "batocera.confg.reg"

class FpinballGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "fpinball",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        wineprefix = HOME / "wine-bottles" / "fpinball"
        emupath = wineprefix / "fpinball"

        mkdir_if_not_exists(wineprefix)

        wine.install_wine_trick(wineprefix, 'wsh57', environment={'W_CACHE': BIOS})

        # create dir & copy fpinball files to wine bottle as necessary
        if not emupath.exists():
            shutil.copytree('/usr/fpinball', emupath)

        # copy updated folder if we have a new BAM FPLoader.exe file
        src_file = Path("/usr/fpinball/BAM/FPLoader.exe")
        dest_file = emupath / "BAM" / "FPLoader.exe"
        if src_file.stat().st_mtime > dest_file.stat().st_mtime:
            shutil.copytree('/usr/fpinball', emupath, dirs_exist_ok=True)

        # convert rom path
        rompath = PureWindowsPath(rom)

        if rom == 'config':
            commandArray = [
                wine.WINE,
                "explorer",
                "/desktop=Wine,{}x{}".format(gameResolution["width"],
                gameResolution["height"]),
                emupath / "BAM" / "FPLoader.exe" ]
        else:
            commandArray = [
                wine.WINE,
                "explorer",
                "/desktop=Wine,{}x{}".format(gameResolution["width"],
                gameResolution["height"]),
                emupath / "BAM" / "FPLoader.exe",
                "/open", f"Z:{rompath}", "/play", "/exit" ]

        # config
        mkdir_if_not_exists(_FPINBALL_CONFIG)

        with _FPINBALL_CONFIG_REG.open("w") as f:
            f.write("Windows Registry Editor Version 5.00\r\n\r\n")
            f.write("[HKEY_CURRENT_USER\\Software\\Future Pinball\\GamePlayer]\r\n")
            f.write("\"AspectRatio\"=dword:{:08x}\r\n".format(FpinballGenerator.getGfxRatioFromConfig(system.config, gameResolution)))
            f.write("\"FullScreen\"=dword:00000001\r\n")
            f.write("\"Width\"=dword:{:08x}\r\n".format(gameResolution["width"]))
            f.write("\"Height\"=dword:{:08x}\r\n".format(gameResolution["height"]))
            f.write("\"JoypadNameNum\"=dword:00000001\r\n")
            f.write("\r\n")

            if system.isOptSet("fpcontroller") and system.config["fpcontroller"] == "True":
                mapping = {
                    "a":        "JoypadBackbox",
                    "b":        "JoypadDigitalPlunger",
                    "x":        "JoypadPause",
                    "y":        "JoypadNextCamera",
                    "pageup":   "JoypadLeftFlipper",
                    "pagedown": "JoypadRightFlipper",
                    "start":    "JoypadStartGame",
                    "select":   "JoypadInsertCoin",
                    "r3":       "JoypadToggleHud"
                }

                nplayer = 1
                for playercontroller, pad in sorted(playersControllers.items()):
                    #only take controller 1
                    if nplayer <= 1:
                        joystickname = pad.real_name
                        unassigned_value = int("ffffffff", 16)
                        assigns = {
                            "JoypadBackbox":        unassigned_value,
                            "JoypadDigitalPlunger": unassigned_value,
                            "JoypadInsertCoin":     unassigned_value,
                            "JoypadNextCamera":     unassigned_value,
                            "JoypadLeftFlipper":    unassigned_value,
                            "JoypadRightFlipper":   unassigned_value,
                            "JoypadPause":          unassigned_value,
                            "JoypadStartGame":      unassigned_value,
                            "JoypadToggleHud":      unassigned_value
                        }
                        for x in pad.inputs:
                            if x in mapping:
                                if mapping[x] in assigns:
                                    if pad.inputs[x].type == "button":
                                        assigns[mapping[x]] = int(pad.inputs[x].id)

                        f.write(f"[HKEY_CURRENT_USER\\Software\\Future Pinball\\GamePlayer\\Joypads\\{joystickname}]\r\n")
                        f.write("\"JoypadBackbox\"=dword:{:08x}\r\n".format(assigns["JoypadBackbox"]))
                        f.write("\"JoypadDeadZone\"=dword:00000064\r\n")
                        f.write("\"JoypadDigitalPlunger\"=dword:{:08x}\r\n".format(assigns["JoypadDigitalPlunger"]))
                        f.write("\"JoypadExit\"=dword:ffffffff\r\n")
                        f.write("\"JoypadInsertCoin\"=dword:{:08x}\r\n".format(assigns["JoypadInsertCoin"]))
                        f.write("\"JoypadInsertCoin2\"=dword:ffffffff\r\n")
                        f.write("\"JoypadInsertCoin3\"=dword:ffffffff\r\n")
                        f.write("\"JoypadLeft2ndFlipper\"=dword:ffffffff\r\n")
                        f.write("\"JoypadLeftFlipper\"=dword:{:08x}\r\n".format(assigns["JoypadLeftFlipper"]))
                        f.write("\"JoypadMusicDown\"=dword:ffffffff\r\n")
                        f.write("\"JoypadMusicUp\"=dword:ffffffff\r\n")
                        f.write("\"JoypadNextCamera\"=dword:{:08x}\r\n".format(assigns["JoypadNextCamera"]))
                        f.write("\"JoypadNudgeAxisX\"=dword:ffffffff\r\n")
                        f.write("\"JoypadNudgeAxisY\"=dword:ffffffff\r\n")
                        f.write("\"JoypadNudgeGainX\"=dword:000003e8\r\n")
                        f.write("\"JoypadNudgeGainXMax\"=dword:00000002\r\n")
                        f.write("\"JoypadNudgeGainY\"=dword:000003e8\r\n")
                        f.write("\"JoypadNudgeGainYMax\"=dword:00000002\r\n")
                        f.write("\"JoypadPause\"=dword:{:08x}\r\n".format(assigns["JoypadPause"]))
                        f.write("\"JoypadPinballRoller\"=dword:ffffffff\r\n")
                        f.write("\"JoypadPinballRollerAxisX\"=dword:ffffffff\r\n")
                        f.write("\"JoypadPinballRollerAxisY\"=dword:ffffffff\r\n")
                        f.write("\"JoypadPinballRollerGainX\"=dword:000003e8\r\n")
                        f.write("\"JoypadPinballRollerGainXMax\"=dword:00000002\r\n")
                        f.write("\"JoypadPinballRollerGainY\"=dword:000003e8\r\n")
                        f.write("\"JoypadPinballRollerGainYMax\"=dword:00000002\r\n")
                        f.write("\"JoypadPlungerAxis\"=dword:00000001\r\n")
                        f.write("\"JoypadPlungerGain\"=dword:000003e8\r\n")
                        f.write("\"JoypadPlungerGainMax\"=dword:00000002\r\n")
                        f.write("\"JoypadRight2ndFlipper\"=dword:ffffffff\r\n")
                        f.write("\"JoypadRightFlipper\"=dword:{:08x}\r\n".format(assigns["JoypadRightFlipper"]))
                        f.write("\"JoypadService\"=dword:ffffffff\r\n")
                        f.write("\"JoypadSpecial1\"=dword:ffffffff\r\n")
                        f.write("\"JoypadSpecial2\"=dword:ffffffff\r\n")
                        f.write("\"JoypadStartGame\"=dword:{:08x}\r\n".format(assigns["JoypadStartGame"]))
                        f.write("\"JoypadSupport\"=dword:00000001\r\n") # enable joystick
                        f.write("\"JoypadTest\"=dword:ffffffff\r\n")
                        f.write("\"JoypadToggleHud\"=dword:{:08x}\r\n".format(assigns["JoypadToggleHud"]))
                        f.write("\"JoypadVolumeDown\"=dword:ffffffff\r\n")
                        f.write("\"JoypadVolumeUp\"=dword:ffffffff\r\n")
                        f.write("\r\n")
                    nplayer += 1

        wine.regedit(wineprefix, _FPINBALL_CONFIG_REG)

        environment = wine.get_wine_environment(wineprefix)

        # ensure nvidia driver used for vulkan
        if Path('/var/tmp/nvidia.prime').exists():
            variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
            for variable_name in variables_to_remove:
                if variable_name in os.environ:
                    del os.environ[variable_name]

            environment.update(
                {
                    'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                    'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d'
                }
            )

        return Command.Command(
            array=commandArray,
            env=environment
        )

    @staticmethod
    def getGfxRatioFromConfig(config, gameResolution):
        # 2: 4:3 ; 1: 16:9  ; 0: auto
        if "ratio" in config:
            if config["ratio"] == "4/3":
                return 43
            if config["ratio"] == "16/9":
                return 169
        return 43
