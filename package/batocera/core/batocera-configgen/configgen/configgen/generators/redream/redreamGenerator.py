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
        with codecs.open(str(configFileName), "w") as f:
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
            written_guids: set[str] = set()
            for controller in playersControllers[:4]:
                ctrlport = f"port{controller.index}=dev:{4 + controller.index},desc:{controller.guid},type:controller"
                f.write((ctrlport)+ "\n")
                ctrlprofile = f"profile{controller.index}=name:{controller.guid},type:controller,deadzone:12,crosshair:1,"
                fullprofile = ctrlprofile
                for input in controller.inputs.values():
                    # [buttons]
                    if input.type == "button" and input.name in ButtonMap:
                        buttonname = ButtonMap[input.name]
                        fullprofile = fullprofile + f"{buttonname}:joy{input.id},"
                    # on rare occassions when triggers are buttons
                    if input.type == "button" and input.name == "l2":
                        fullprofile = f"{fullprofile}ltrig:joy{input.id},"
                    if input.type == "button" and input.name == "r2":
                        fullprofile = f"{fullprofile}rtrig:joy{input.id},"
                    # on occassions when dpad directions are buttons
                    if (
                        input.type == "button"
                        and (input.name == "up" or input.name == "down" or input.name == "left" or input.name == "right")
                    ):
                            fullprofile = f"{fullprofile}dpad_{input.name}:joy{input.id},"
                    # [hats]
                    if input.type == "hat" and input.name in HatMap:
                        hatid = HatMap[input.name]
                        fullprofile = f"{fullprofile}dpad_{input.name}:hat{hatid},"
                    # [axis]
                    if input.type == "axis" and input.name in AxisMap:
                        axisid = AxisMap[input.name]
                        # l2/r2 as axis triggers
                        if input.name == "l2":
                            fullprofile = f"{fullprofile}ltrig:+axis{input.id},"
                        if input.name == "r2":
                            fullprofile = f"{fullprofile}rtrig:+axis{input.id},"
                        # handle axis l,r,u,d
                        if input.name == "joystick1left":
                            fullprofile = f"{fullprofile}ljoy_left:-axis{axisid},"
                            fullprofile = f"{fullprofile}ljoy_right:+axis{axisid},"
                        if input.name == "joystick1up":
                            fullprofile = f"{fullprofile}ljoy_up:-axis{axisid},"
                            fullprofile = f"{fullprofile}ljoy_down:+axis{axisid},"

                # special nintendo workaround since redream makes no sense...
                if controller.guid == "030000007e0500000920000011810000":
                    fullprofile = ctrlprofile + "b:joy1,a:joy0,dpad_down:hat1,ljoy_left:-axis0,ljoy_right:+axis0,ljoy_up:-axis1,ljoy_down:+axis1,ltrig:joy6,dpad_left:hat2,rtrig:joy7,dpad_right:hat3,turbo:joy8,start:joy9,dpad_up:hat0,y:joy2,x:joy3,"
                # add key to exit for evmapy to the end
                fullprofile = fullprofile + "exit:f10"
                # check if we have already writtent the profile, if so, we don't save it
                if controller.guid not in written_guids:
                    written_guids.add(controller.guid)
                    f.write((fullprofile)+ "\n")

            # change settings as per users options
            # [video]
            f.write(f"width={gameResolution['width']}\n")
            f.write(f"height={gameResolution['height']}\n")
            f.write(f"fullwidth={gameResolution['width']}\n")
            f.write(f"fullheight={gameResolution['height']}\n")
            if system.isOptSet("redreamResolution"):
                f.write(f"res={system.config['redreamResolution']}\n")
            else:
                f.write("res=2\n")
            if system.isOptSet("redreamRatio"):
                f.write(f"aspect={system.config['redreamRatio']}\n")
            else:
                f.write("aspect=4:3\n")
            if system.isOptSet("redreamFrameSkip"):
                f.write(f"frameskip={system.config['redreamFrameSkip']}\n")
            else:
                f.write("frameskip=0\n")
            if system.isOptSet("redreamVsync"):
                f.write(f"vysnc={system.config['redreamVsync']}\n")
            else:
                f.write("vsync=0\n")
            if system.isOptSet("redreamRender"):
                f.write(f"renderer={system.config['redreamRender']}\n")
            else:
                f.write("renderer=hle_perstrip\n")
            # [system]
            if system.isOptSet("redreamRegion"):
                f.write(f"region={system.config['redreamRegion']}\n")
            else:
                f.write("region=usa\n")
            if system.isOptSet("redreamLanguage"):
                f.write(f"language={system.config['redreamLanguage']}\n")
            else:
                f.write("language=english\n")
            if system.isOptSet("redreamBroadcast"):
                f.write(f"broadcast={system.config['redreamBroadcast']}\n")
            else:
                f.write("broadcast=ntsc\n")
            if system.isOptSet("redreamCable"):
                f.write(f"cable={system.config['redreamCable']}\n")
            else:
                f.write("cable=vga\n")

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
            return 4/3
        return 4/3
