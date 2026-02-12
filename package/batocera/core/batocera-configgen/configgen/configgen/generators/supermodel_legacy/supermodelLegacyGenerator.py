from __future__ import annotations

import re
import shutil
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import Controller, generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ...gun import Guns, guns_need_crosses
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...types import HotkeysContext


SUPERMODEL_SHARE: Final = Path('/usr/share/supermodel')
SUPERMODEL_CONFIG: Final = CONFIGS / 'supermodel'
SUPERMODEL_SAVES: Final = SAVES / 'supermodel'


class SupermodelLegacyGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "supermodel",
            "keys": { "exit": "KEY_ESC", "menu": ["KEY_LEFTALT", "KEY_P"], "pause": ["KEY_LEFTALT", "KEY_P"], "reset": ["KEY_LEFTALT", "KEY_R"],
                      "save_state": "KEY_F5", "restore_state": "KEY_F7", "next_state": "KEY_F6"
                     }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray: list[str | Path] = ["supermodel", "-fullscreen", "-channels=2"]

        # legacy3d
        if system.config.get("engine3D") == "new3d":
            commandArray.append("-new3d")
        else:
            commandArray.extend(["-multi-texture", "-legacy-scsp", "-legacy3d"])

        # widescreen
        if system.config.get_bool("m3_wideScreen"):
            commandArray.append("-wide-screen")
            commandArray.append("-wide-bg")
            system.config["bezel"] == "none"

        # quad rendering
        if system.config.get_bool("quadRendering"):
            commandArray.append("-quad-rendering")

        # crosshairs
        if crosshairs := system.config.get("crosshairs"):
            commandArray.append(f"-crosshairs={crosshairs}")
        else:
            if guns_need_crosses(guns):
                if len(guns) == 1:
                    commandArray.append("-crosshairs=1")
                else:
                    commandArray.append("-crosshairs=3")

        # force feedback
        if system.config.get_bool("forceFeedback"):
            commandArray.append("-force-feedback")

        # powerpc frequesncy
        if freq := system.config.get("ppcFreq"):
            commandArray.append(f"-ppc-frequency={freq}")

        # crt colour
        if color := system.config.get("crt_colour"):
            commandArray.append(f"-crtcolors={color}")

        # upscale mode
        if upscale_mode := system.config.get("upscale_mode"):
            commandArray.append(f"-upscalemode={upscale_mode}")

        #driving controls
        drivingGame = system.config.get_bool("pedalSwap")

        #driving sensitivity
        sensitivity = system.config.get_str("joystickSensitivity", "100")

        # resolution
        commandArray.append(f"-res={gameResolution['width']},{gameResolution['height']}")

        # logs
        commandArray.extend(["-log-output=/userdata/system/logs/Supermodel.log", rom])

        # copy nvram files
        copy_nvram_files()

        # copy gun asset files
        copy_asset_files()

        # copy xml
        copy_xml()

        # controller config
        configPadsIni(system, rom, playersControllers, guns, drivingGame, sensitivity)

        return Command.Command(
            array=commandArray,
            env={
                "SDL_VIDEODRIVER": "x11",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get('m3_wideScreen') == "1":
            return 16 / 9
        return 4 / 3

def copy_nvram_files():
    sourceDir = SUPERMODEL_SHARE / "NVRAM"
    targetDir = SUPERMODEL_SAVES / "NVRAM"

    mkdir_if_not_exists(targetDir)

    # create nv files which are in source and have a newer modification time than in target
    for sourceFile in sourceDir.iterdir():
        if sourceFile.suffix == ".nv":
            targetFile = targetDir / sourceFile.name
            if not targetFile.exists():
                # if the target file doesn't exist, just copy the source file
                copyfile(sourceFile, targetFile)
            else:
                # if the target file exists and has an older modification time than the source file, create a backup and copy the new file
                if sourceFile.stat().st_mtime > targetFile.stat().st_mtime:
                    backupFile = targetFile.with_suffix(f"{targetFile.suffix}.bak")
                    if backupFile.exists():
                        backupFile.unlink()
                    targetFile.rename(backupFile)
                    copyfile(sourceFile, targetFile)

def copy_asset_files():
    sourceDir = SUPERMODEL_SHARE / "Assets"
    targetDir = SUPERMODEL_CONFIG / "Assets"
    if not sourceDir.exists():
        return
    mkdir_if_not_exists(targetDir)

    # create asset files which are in source and have a newer modification time than in target
    for sourceFile in sourceDir.iterdir():
        targetFile = targetDir / sourceFile.name
        if not targetFile.exists() or sourceFile.stat().st_mtime > targetFile.stat().st_mtime:
            copyfile(sourceFile, targetFile)

def copy_xml():
    source_path = SUPERMODEL_SHARE / 'Games.xml'
    dest_path = SUPERMODEL_CONFIG / 'Games.xml'
    mkdir_if_not_exists(dest_path.parent)
    if not dest_path.exists() or source_path.stat().st_mtime > dest_path.stat().st_mtime:
        shutil.copy2(source_path, dest_path)

def configPadsIni(system: Emulator, rom: Path, playersControllers: Controllers, guns: Guns, altControl: bool, sensitivity: str) -> None:
    if altControl:
        templateFile = SUPERMODEL_SHARE / "Supermodel-Driving.ini.template"
        mapping: dict[str, str | None] = {
            "button1": "y",
            "button2": "b",
            "button3": "a",
            "button4": "x",
            "button5": "pageup",
            "button6": "pagedown",
            "button7": None,
            "button8": None,
            "button9": "start", # start
            "button10": "select", # coins
            "axisX": "joystick1left",
            "axisY": "joystick1up",
            "axisZ": "r2",
            "axisRX": "joystick2left",
            "axisRY": "joystick2up",
            "axisRZ": "l2",
            "left": "joystick1left",
            "right": "joystick1right",
            "up": "joystick1up",
            "down": "joystick1down"
        }
    else:
        templateFile = SUPERMODEL_SHARE / "Supermodel.ini.template"
        mapping = {
            "button1": "y",
            "button2": "b",
            "button3": "a",
            "button4": "x",
            "button5": "pageup",
            "button6": "pagedown",
            "button7": "l2",
            "button8": "r2",
            "button9": "start", # start
            "button10": "select", # coins
            "axisX": "joystick1left",
            "axisY": "joystick1up",
            "axisZ": None,
            "axisRX": "joystick2left",
            "axisRY": "joystick2up",
            "axisRZ": None,
            "left": "joystick1left",
            "right": "joystick1right",
            "up": "joystick1up",
            "down": "joystick1down"
        }
    targetFile = SUPERMODEL_CONFIG / "Supermodel.ini"

    mapping_fallback = {
        "axisX": "left",
        "axisY": "up",
        "right": "right",
        "down": "down",
        "left": "left",
        "up": "up"
    }

    # template
    templateConfig = CaseSensitiveConfigParser(interpolation=None)
    templateConfig.read(templateFile, encoding='utf_8_sig')

    # target
    targetConfig = CaseSensitiveConfigParser(interpolation=None)

    for section in templateConfig.sections():
        targetConfig.add_section(section)
        for key, value in templateConfig.items(section):
            targetConfig.set(section, key, transformValue(value, playersControllers, mapping, mapping_fallback))

    # apply guns
    for section in targetConfig.sections():
        if section.strip() in [ "Global", rom.stem ]:
            # for an input sytem
            if section.strip() != "Global":
                targetConfig.set(section, "InputSystem", "to be defined")
            for key, _ in targetConfig.items(section):
                if system.config.use_guns and guns:
                    if key == "InputSystem":
                        targetConfig.set(section, key, "evdev")
                    elif key == "InputAnalogJoyX":
                        targetConfig.set(section, key, "MOUSE1_XAXIS_INV")
                    elif key == "InputAnalogJoyY":
                        targetConfig.set(section, key, "MOUSE1_YAXIS_INV")
                    elif key == "InputGunX" or key == "InputAnalogGunX":
                        targetConfig.set(section, key, "MOUSE1_XAXIS")
                    elif key == "InputGunY" or key == "InputAnalogGunY":
                        targetConfig.set(section, key, "MOUSE1_YAXIS")
                    elif key == "InputTrigger" or key == "InputAnalogTriggerLeft" or key == "InputAnalogJoyTrigger":
                        targetConfig.set(section, key, "MOUSE1_LEFT_BUTTON")
                    elif key == "InputOffscreen" or key == "InputAnalogTriggerRight":
                        targetConfig.set(section, key, "MOUSE1_RIGHT_BUTTON")
                    elif key == "InputStart1":
                        val = transformElement("JOY1_BUTTON9", playersControllers, mapping, mapping_fallback)
                        if val is not None:
                            val = f",{val}"
                        else:
                            val = ""
                        targetConfig.set(section, key, f"MOUSE1_BUTTONX1{val}")
                    elif key == "InputCoin1":
                        val = transformElement("JOY1_BUTTON10", playersControllers, mapping, mapping_fallback)
                        if val is not None:
                            val = f",{val}"
                        else:
                            val = ""
                        targetConfig.set(section, key, f"MOUSE1_BUTTONX2{val}")
                    elif key == "InputAnalogJoyEvent":
                        val = transformElement("JOY1_BUTTON2", playersControllers, mapping, mapping_fallback)
                        if val is not None:
                            val = f",{val}"
                        else:
                            val = ""
                        targetConfig.set(section, key, f"KEY_S,MOUSE1_MIDDLE_BUTTON{val}")
                    elif len(guns) >= 2:
                        if key == "InputAnalogJoyX2":
                            targetConfig.set(section, key, "MOUSE2_XAXIS_INV")
                        elif key == "InputAnalogJoyY2":
                            targetConfig.set(section, key, "MOUSE2_YAXIS_INV")
                        elif key == "InputGunX2" or key == "InputAnalogGunX2":
                            targetConfig.set(section, key, "MOUSE2_XAXIS")
                        elif key == "InputGunY2" or key == "InputAnalogGunY2":
                            targetConfig.set(section, key, "MOUSE2_YAXIS")
                        elif key == "InputTrigger2" or key == "InputAnalogTriggerLeft2" or key == "InputAnalogJoyTrigger2":
                            targetConfig.set(section, key, "MOUSE2_LEFT_BUTTON")
                        elif key == "InputOffscreen2" or key == "InputAnalogTriggerRight2":
                            targetConfig.set(section, key, "MOUSE2_RIGHT_BUTTON")
                        elif key == "InputStart2":
                            val = transformElement("JOY2_BUTTON9", playersControllers, mapping, mapping_fallback)
                            if val is not None:
                                val = f",{val}"
                            else:
                                val = ""
                            targetConfig.set(section, key, f"MOUSE2_BUTTONX1{val}")
                        elif key == "InputCoin1":
                            val = transformElement("JOY2_BUTTON10", playersControllers, mapping, mapping_fallback)
                            if val is not None:
                                val = f",{val}"
                            else:
                                val = ""
                            targetConfig.set(section, key,  f"MOUSE2_BUTTONX2{val}")
                        elif key == "InputAnalogJoyEvent2":
                            val = transformElement("JOY2_BUTTON2", playersControllers, mapping, mapping_fallback)
                            if val is not None:
                                val = f",{val}"
                            else:
                                val = ""
                            targetConfig.set(section, key, f"MOUSE2_MIDDLE_BUTTON{val}")
                else:
                    if key == "InputSystem":
                        targetConfig.set(section, key, "sdl")

    # Update InputJoy1XSaturation key with the given sensitivity value
    sensitivity = str(int(float(sensitivity)))
    for section in targetConfig.sections():
        if targetConfig.has_option(section, "InputJoy1XSaturation"):
            targetConfig.set(section, "InputJoy1XSaturation", sensitivity)

    # save the ini file
    with ensure_parents_and_open(targetFile, 'w') as configfile:
        targetConfig.write(configfile)

def transformValue(value: str, playersControllers: Controllers, mapping: dict[str, str | None], mapping_fallback: dict[str, str]):
    # remove comments
    cleanValue = value
    matches = re.search("^([^;]*[^ ])[ ]*;.*$", value)
    if matches:
        cleanValue = matches.group(1)

    if cleanValue[0] == '"' and cleanValue[-1] == '"':
        newvalue = ""
        for elt in cleanValue[1:-1].split(","):
            newelt = transformElement(elt, playersControllers, mapping, mapping_fallback)
            if newelt is not None:
                if newvalue != "":
                    newvalue = f"{newvalue},"
                newvalue = f"{newvalue}{newelt}"
        return f'"{newvalue}"'

    # integers
    return cleanValue

def transformElement(elt: str, playersControllers: Controllers, mapping: dict[str, str | None], mapping_fallback: dict[str, str]):
    # Docs/README.txt
    # JOY1_LEFT  is the same as JOY1_XAXIS_NEG
    # JOY1_RIGHT is the same as JOY1_XAXIS_POS
    # JOY1_UP    is the same as JOY1_YAXIS_NEG
    # JOY1_DOWN  is the same as JOY1_YAXIS_POS

    matches = re.search("^JOY([12])_BUTTON([0-9]*)$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), mapping[f"button{matches.group(2)}"])
    matches = re.search("^JOY([12])_UP$", elt)
    if matches:
        # check joystick type if it's hat or axis
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_up = "up"
        else:
            key_up = "axisY"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_up, mapping, mapping_fallback)
        print(mp)
        return input2input(playersControllers, matches.group(1), mp, -1)
    matches = re.search("^JOY([12])_DOWN$", elt)
    if matches:
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_down = "down"
        else:
            key_down = "axisY"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_down, mapping, mapping_fallback)
        return input2input(playersControllers, matches.group(1), mp, 1)
    matches = re.search("^JOY([12])_LEFT$", elt)
    if matches:
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_left = "left"
        else:
            key_left = "axisX"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_left, mapping, mapping_fallback)
        return input2input(playersControllers, matches.group(1), mp, -1)
    matches = re.search("^JOY([12])_RIGHT$", elt)
    if matches:
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_right = "right"
        else:
            key_right = "axisX"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_right, mapping, mapping_fallback)
        return input2input(playersControllers, matches.group(1), mp, 1)

    matches = re.search("^JOY([12])_(R?[XY])AXIS$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), mapping[f"axis{matches.group(2)}"])
    matches = re.search("^JOY([12])_(R?[XYZ])AXIS_NEG$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), mapping[f"axis{matches.group(2)}"], -1)
    matches = re.search("^JOY([12])_(R?[XYZ])AXIS_POS$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), mapping[f"axis{matches.group(2)}"], 1)
    if matches:
        return None
    return elt

def getMappingKeyIncludingFallback(playersControllers: Controllers, padnum: str, key: str, mapping: dict[str, str | None], mapping_fallback: dict[str, str]):
    pad_number = int(padnum)
    if (
        (pad := Controller.find_player_number(playersControllers, pad_number))
        and (key not in mapping or mapping[key] not in pad.inputs)
        and (key in mapping_fallback and mapping_fallback[key] in pad.inputs)
    ):
        return mapping_fallback[key]
    return mapping[key]

def joy2realjoyid(playersControllers: Controllers, joy: str):
    joy_number = int(joy)
    if pad := Controller.find_player_number(playersControllers, joy_number):
        return pad.index

    raise BatoceraException(f'Cannot find joystick {joy}')

def hatOrAxis(playersControllers: Controllers, player: str):
    player_number = int(player)
    #default to axis
    type = "axis"
    if pad := Controller.find_player_number(playersControllers, player_number):
        for button in pad.inputs:
            input = pad.inputs[button]
            if input.type == "hat":
                type = "hat"
            elif input.type == "axis":
                type = "axis"
    return type

def input2input(playersControllers: Controllers, player: str, button: str | None, axisside: int | None = None):
    player_number = int(player)
    if (pad := Controller.find_player_number(playersControllers, player_number)) and button in pad.inputs:
        joynum = joy2realjoyid(playersControllers, player)
        input = pad.inputs[button]
        if input.type == "button":
            return f"JOY{joynum+1}_BUTTON{int(input.id)+1}"
        if input.type == "hat":
            if input.value == "1":
                return f"JOY{joynum+1}_UP,JOY{joynum+1}_POV1_UP"
            if input.value == "2":
                return f"JOY{joynum+1}_RIGHT,JOY{joynum+1}_POV1_RIGHT"
            if input.value == "4":
                return f"JOY{joynum+1}_DOWN,JOY{joynum+1}_POV1_DOWN"
            if input.value == "8":
                return f"JOY{joynum+1}_LEFT,JOY{joynum+1}_POV1_LEFT"
        elif input.type == "axis":
            sidestr = ""
            if axisside is not None:
                if axisside == 1:
                    if input.value == "1":
                        sidestr = "_NEG"
                    else:
                        sidestr = "_POS"
                else:
                    if input.value == "1":
                        sidestr = "_POS"
                    else:
                        sidestr = "_NEG"

            if button == "joystick1left" or button == "left":
                return f"JOY{joynum+1}_XAXIS{sidestr}"
            if button == "joystick1up" or button == "up":
                return f"JOY{joynum+1}_YAXIS{sidestr}"
            if button == "joystick2left":
                return f"JOY{joynum+1}_RXAXIS{sidestr}"
            if button == "joystick2up":
                return f"JOY{joynum+1}_RYAXIS{sidestr}"
            if button == "l2":
                return f"JOY{joynum+1}_ZAXIS{sidestr}"
            if button == "r2":
                return f"JOY{joynum+1}_RZAXIS{sidestr}"

    return None
