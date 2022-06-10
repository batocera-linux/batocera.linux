#!/usr/bin/env python

from generators.Generator import Generator
import Command
import controllersConfig
from utils.logger import get_logger
import batoceraFiles
import os
import subprocess
import sys

eslog = get_logger(__name__)

class FpinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/fpinball"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        if not os.path.exists(wineprefix + "/wsh57.done"):
            cmd = ["/usr/wine/winetricks", "wsh57"]
            env = {"W_CACHE": "/userdata/bios", "LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX":"/userdata/saves/fpinball" }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/wsh57.done", "w") as f:
                f.write("done")

        commandArray = ["/usr/wine/lutris/bin/wine", "explorer", "/desktop=Wine,{}x{}".format(gameResolution["width"], gameResolution["height"]), "/usr/fpinball/Future Pinball.exe", "/open", "z:" + rom, "/play", "/exit" ]

        # config
        if not os.path.exists("/userdata/system/configs/fpinball"):
            os.makedirs("/userdata/system/configs/fpinball")
        
        with open("/userdata/system/configs/fpinball/batocera.confg.reg", "w") as f:
            f.write("Windows Registry Editor Version 5.00\r\n\r\n")
            f.write("[HKEY_CURRENT_USER\\Software\\Future Pinball\\GamePlayer]\r\n")
            f.write("\"AspectRatio\"=dword:{:08x}\r\n".format(FpinballGenerator.getGfxRatioFromConfig(system.config, gameResolution)))
            f.write("\"FullScreen\"=dword:00000001\r\n")
            f.write("\"Width\"=dword:{:08x}\r\n".format(gameResolution["width"]))
            f.write("\"Height\"=dword:{:08x}\r\n".format(gameResolution["height"]))
            f.write("\"JoypadNameNum\"=dword:00000001\r\n")
            f.write("\r\n")

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
                    joystickname = pad.realName
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

        cmd = ["wine", "regedit", "/userdata/system/configs/fpinball/batocera.confg.reg"]
        env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX":"/userdata/saves/fpinball" }
        env.update(os.environ)
        env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
        eslog.debug(f"command: {str(cmd)}")
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        eslog.debug(out.decode())
        eslog.error(err.decode())

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": wineprefix,
                "LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine",
                "LIBGL_DRIVERS_PATH": "/lib32/dri",
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
            })

    def getGfxRatioFromConfig(config, gameResolution):
        # 2: 4:3 ; 1: 16:9  ; 0: auto
        if "ratio" in config:
            if config["ratio"] == "4/3":
                return 43
            if config["ratio"] == "16/9":
                return 169
        return 43

    def executionDirectory(self, config, rom):
        return os.path.dirname(rom)
