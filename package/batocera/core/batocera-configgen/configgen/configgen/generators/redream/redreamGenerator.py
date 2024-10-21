from __future__ import annotations

import codecs
import filecmp
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

redream_file: Final = Path("/usr/bin/redream")
redreamConfig: Final = CONFIGS / "redream"
redreamRoms: Final = ROMS / "dreamcast"

class RedreamGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "redream",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        redream_exec = redreamConfig / "redream"

        mkdir_if_not_exists(redreamConfig)

        if not redream_exec.exists() or not filecmp.cmp(redream_file, redream_exec):
            copyfile(redream_file, redream_exec)
            redream_exec.chmod(0o0775)

        configFileName = redreamConfig / "redream.cfg"
        f = codecs.open(str(configFileName), "w")
        # set the roms path
        f.write(f"gamedir={redreamRoms}\n")
        # force fullscreen
        f.write("mode=exclusive fullscreen\n")
        f.write("fullmode=exclusive fullscreen\n")
        # configure controller
        ButtonMap = {
            "a":      "b",
            "b":      "a",
            "x":      "y",
            "y":      "x",
            "start":  "start",
            "select": "menu",
            "pageup": "turbo"
        }
        HatMap = {
            "up":    0,
            "down":  1,
            "left":  2,
            "right": 3
        }
        AxisMap = {
            "joystick1left": 0,
            "joystick1up":   1,
            # use input.id for l2/r2
            "l2":            2,
            "r2":            3
        }
        nplayer = 1
        written_guids = set()
        for index in playersControllers:
            controller = playersControllers[index]
            if nplayer <= 4:
                ctrlport = f"port{controller.index}=dev:{4 + controller.index},desc:{controller.guid},type:controller"
                f.write((ctrlport)+ "\n")
                ctrlprofile = "profile{}=name:{},type:controller,deadzone:12,crosshair:1,".format(controller.index, controller.guid)
                fullprofile = ctrlprofile
                for index in controller.inputs:
                    input = controller.inputs[index]
                    # [buttons]
                    if input.type == "button" and input.name in ButtonMap:
                        buttonname = ButtonMap[input.name]
                        fullprofile = fullprofile + "{}:joy{},".format(buttonname, input.id)
                    # on rare occassions when triggers are buttons
                    if input.type == "button" and input.name == "l2":
                        fullprofile = fullprofile + "ltrig:joy{},".format(input.id)
                    if input.type == "button" and input.name == "r2":
                        fullprofile = fullprofile + "rtrig:joy{},".format(input.id)
                    # on occassions when dpad directions are buttons
                    if input.type == "button":
                        if input.name == "up" or input.name == "down" or input.name == "left" or input.name == "right":
                            fullprofile = fullprofile + "dpad_{}:joy{},".format(input.name, input.id)
                    # [hats]
                    if input.type == "hat" and input.name in HatMap:
                        hatid = HatMap[input.name]
                        fullprofile = fullprofile + "dpad_{}:hat{},".format(input.name, hatid)
                    # [axis]
                    if input.type == "axis" and input.name in AxisMap:
                        axisid = AxisMap[input.name]
                        # l2/r2 as axis triggers
                        if input.name == "l2":
                            fullprofile = fullprofile + "ltrig:+axis{},".format(input.id)
                        if input.name == "r2":
                            fullprofile = fullprofile + "rtrig:+axis{},".format(input.id)
                        # handle axis l,r,u,d
                        if input.name == "joystick1left":
                            fullprofile = fullprofile + "ljoy_left:-axis{},".format(axisid)
                            fullprofile = fullprofile + "ljoy_right:+axis{},".format(axisid)
                        if input.name == "joystick1up":
                            fullprofile = fullprofile + "ljoy_up:-axis{},".format(axisid)
                            fullprofile = fullprofile + "ljoy_down:+axis{},".format(axisid)

                # special nintendo workaround since redream makes no sense...
                if controller.guid == "030000007e0500000920000011810000":
                    fullprofile = ctrlprofile + "b:joy1,a:joy0,dpad_down:hat1,ljoy_left:-axis0,ljoy_right:+axis0,ljoy_up:-axis1,ljoy_down:+axis1,ltrig:joy6,dpad_left:hat2,rtrig:joy7,dpad_right:hat3,turbo:joy8,start:joy9,dpad_up:hat0,y:joy2,x:joy3,"
                # add key to exit for evmapy to the end
                fullprofile = fullprofile + "exit:f10"
                # check if we have already writtent the profile, if so, we don't save it
                if controller.guid not in written_guids:
                    written_guids.add(controller.guid)
                    f.write((fullprofile)+ "\n")
                nplayer = nplayer + 1

        # change settings as per users options
        # [video]
        f.write("width={}\n".format(gameResolution["width"]))
        f.write("height={}\n".format(gameResolution["height"]))
        f.write("fullwidth={}\n".format(gameResolution["width"]))
        f.write("fullheight={}\n".format(gameResolution["height"]))
        if system.isOptSet("redreamResolution"):
            f.write("res={}".format(system.config["redreamResolution"]) + "\n")
        else:
            f.write("res=2\n")
        if system.isOptSet("redreamRatio"):
            f.write("aspect={}".format(system.config["redreamRatio"]) + "\n")
        else:
            f.write("aspect=4:3\n")
        if system.isOptSet("redreamFrameSkip"):
            f.write("frameskip={}".format(system.config["redreamFrameSkip"]) + "\n")
        else:
            f.write("frameskip=0\n")
        if system.isOptSet("redreamVsync"):
            f.write("vysnc={}".format(system.config["redreamVsync"]) + "\n")
        else:
            f.write("vsync=0\n")
        if system.isOptSet("redreamRender"):
            f.write("renderer={}".format(system.config["redreamRender"]) + "\n")
        else:
            f.write("renderer=hle_perstrip\n")
        # [system]
        if system.isOptSet("redreamRegion"):
            f.write("region={}".format(system.config["redreamRegion"]) + "\n")
        else:
            f.write("region=usa\n")
        if system.isOptSet("redreamLanguage"):
            f.write("language={}".format(system.config["redreamLanguage"]) + "\n")
        else:
            f.write("language=english\n")
        if system.isOptSet("redreamBroadcast"):
            f.write("broadcast={}".format(system.config["redreamBroadcast"]) + "\n")
        else:
            f.write("broadcast=ntsc\n")
        if system.isOptSet("redreamCable"):
            f.write("cable={}".format(system.config["redreamCable"]) + "\n")
        else:
            f.write("cable=vga\n")

        f.write
        f.close()

        commandArray = [redream_exec, rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0'
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if 'redreamRatio' in config:
            if config['redreamRatio'] == "16:9" or config['redreamRatio'] == "stretch":
                return 16/9
            else:
                return 4/3
        else:
            return 4/3
