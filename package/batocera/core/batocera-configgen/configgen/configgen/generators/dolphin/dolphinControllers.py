from __future__ import annotations

import codecs
import logging
import re
from typing import TYPE_CHECKING

from ...utils.configparser import CaseSensitiveConfigParser
from .dolphinPaths import DOLPHIN_CONFIG

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from ...controller import Controller, ControllerMapping
    from ...Emulator import Emulator
    from ...types import DeviceInfoMapping, GunMapping

eslog = logging.getLogger(__name__)

# Create the controller configuration file
def generateControllerConfig(system: Emulator, playersControllers: ControllerMapping, metadata: Mapping[str, str], wheels: DeviceInfoMapping, rom: Path, guns: GunMapping) -> None:

    #generateHotkeys(playersControllers)
    if system.name == "wii":
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
            generateControllerConfig_guns("WiimoteNew.ini", "Wiimote", metadata, guns)
            generateControllerConfig_gamecube(system, playersControllers, {}, rom)           # You can use the gamecube pads on the wii together with wiimotes
        elif (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == False):
            # Generate if hardcoded
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(system, playersControllers, {}, rom)           # You can use the gamecube pads on the wii together with wiimotes
        elif (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True):
            # Generate if hardcoded
            generateControllerConfig_emulatedwiimotes(system, playersControllers, {}, rom)
            removeControllerConfig_gamecube()                                           # Because pads will already be used as emulated wiimotes
        elif (".cc." in rom.name or ".pro." in rom.name or ".side." in rom.name or ".is." in rom.name or ".it." in rom.name or ".in." in rom.name or ".ti." in rom.name or ".ts." in rom.name or ".tn." in rom.name or ".ni." in rom.name or ".ns." in rom.name or ".nt." in rom.name) or system.isOptSet("sideWiimote"):
            # Generate if auto and name extensions are present
            generateControllerConfig_emulatedwiimotes(system, playersControllers, {}, rom)
            removeControllerConfig_gamecube()                                           # Because pads will already be used as emulated wiimotes
        else:
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(system, playersControllers, {}, rom)           # You can use the gamecube pads on the wii together with wiimotes
    elif system.name == "gamecube":
        used_wheels = {}
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels') and len(wheels) > 0:
            if "wheel_type" in metadata:
                if metadata["wheel_type"] == "Steering Wheel":
                    used_wheels = wheels
            elif "dolphin_wheel_type" in system.config:
                if system.config["dolphin_wheel_type"] == "Steering Wheel":
                    used_wheels = wheels
        generateControllerConfig_gamecube(system, playersControllers, used_wheels, rom)               # Pass ROM name to allow for per ROM configuration
    else:
        raise ValueError("Invalid system name : '" + system.name + "'")

# https://docs.libretro.com/library/dolphin/

def generateControllerConfig_emulatedwiimotes(system: Emulator, playersControllers: ControllerMapping, wheels: DeviceInfoMapping, rom: Path) -> None:
    wiiMapping = {
        'x':             'Buttons/2',
        'b':             'Buttons/A',
        'y':             'Buttons/1',
        'a':             'Buttons/B',
        'pageup':        'Buttons/-',
        'pagedown':      'Buttons/+',
        'select':        'Buttons/Home',
        'up':            'D-Pad/Up',
        'down':          'D-Pad/Down',
        'left':          'D-Pad/Left',
        'right':         'D-Pad/Right',
        'joystick1up':   'IR/Up',
        'joystick1left': 'IR/Left',
        'joystick2up':   'Tilt/Forward',
        'joystick2left': 'Tilt/Left',
        'hotkey':        'Buttons/Hotkey'
    }
    wiiReverseAxes = {
        'IR/Up':                    'IR/Down',
        'IR/Left':                  'IR/Right',
        'Swing/Up':                 'Swing/Down',
        'Swing/Left':               'Swing/Right',
        'Tilt/Left':                'Tilt/Right',
        'Tilt/Forward':             'Tilt/Backward',
        'Nunchuk/Stick/Up':         'Nunchuk/Stick/Down',
        'Nunchuk/Stick/Left':       'Nunchuk/Stick/Right',
        'Classic/Right Stick/Up':   'Classic/Right Stick/Down',
        'Classic/Right Stick/Left': 'Classic/Right Stick/Right',
        'Classic/Left Stick/Up':    'Classic/Left Stick/Down',
        'Classic/Left Stick/Left':  'Classic/Left Stick/Right'
    }

    extraOptions: dict[str, str] = {}
    extraOptions["Source"] = "1"

    # Side wiimote
    # l2 for shaking actions
    if (".side." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] != 'disabled' and system.config['controller_mode'] != 'cc'):
        extraOptions["Options/Sideways Wiimote"] = "1"
        wiiMapping['x']  = 'Buttons/B'
        wiiMapping['y']  = 'Buttons/A'
        wiiMapping['a']  = 'Buttons/2'
        wiiMapping['b']  = 'Buttons/1'
        wiiMapping['l2'] = 'Shake/X'
        wiiMapping['l2'] = 'Shake/Y'
        wiiMapping['l2'] = 'Shake/Z'

    # i: infrared, s: swing, t: tilt, n: nunchuk
    # 12 possible combinations : is si / it ti / in ni / st ts / sn ns / tn nt

    # i
    if (".is." in rom.name or ".it." in rom.name or ".in." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] != 'disabled' and system.config['controller_mode'] != 'in' and system.config['controller_mode'] != 'cc'):
        wiiMapping['joystick1up']   = 'IR/Up'
        wiiMapping['joystick1left'] = 'IR/Left'
    if (".si." in rom.name or ".ti." in rom.name or ".ni." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'in' and system.config['controller_mode'] != 'cc'):
        wiiMapping['joystick2up']   = 'IR/Up'
        wiiMapping['joystick2left'] = 'IR/Left'

    # s
    if ".si." in rom.name or ".st." in rom.name or ".sn." in rom.name:
        wiiMapping['joystick1up']   = 'Swing/Up'
        wiiMapping['joystick1left'] = 'Swing/Left'
    if (".is." in rom.name or ".ts." in rom.name or ".ns." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'is'):
        wiiMapping['joystick2up']   = 'Swing/Up'
        wiiMapping['joystick2left'] = 'Swing/Left'

    # t
    if ".ti." in rom.name or ".ts." in rom.name or ".tn." in rom.name:
        wiiMapping['joystick1up']   = 'Tilt/Forward'
        wiiMapping['joystick1left'] = 'Tilt/Left'
    if (".it." in rom.name or ".st." in rom.name or ".nt." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'it'):
        wiiMapping['joystick2up']   = 'Tilt/Forward'
        wiiMapping['joystick2left'] = 'Tilt/Left'

    # n
    if (".ni." in rom.name or ".ns." in rom.name or ".nt." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'in') or (system.isOptSet("dsmotion") and system.getOptBoolean("dsmotion") == True):
        extraOptions['Extension']   = 'Nunchuk'
        wiiMapping['l2'] = 'Nunchuk/Buttons/C'
        wiiMapping['r2'] = 'Nunchuk/Buttons/Z'
        wiiMapping['joystick1up']   = 'Nunchuk/Stick/Up'
        wiiMapping['joystick1left'] = 'Nunchuk/Stick/Left'
    if ".in." in rom.name or ".sn." in rom.name or ".tn." in rom.name:
        extraOptions['Extension']   = 'Nunchuk'
        wiiMapping['l2'] = 'Nunchuk/Buttons/C'
        wiiMapping['r2'] = 'Nunchuk/Buttons/Z'
        wiiMapping['joystick2up']   = 'Nunchuk/Stick/Up'
        wiiMapping['joystick2left'] = 'Nunchuk/Stick/Left'

    # cc : Classic Controller Settings / pro : Classic Controller Pro Settings
    # Swap shoulder with triggers and vice versa if cc
    if (".cc." in rom.name or ".pro." in rom.name) or (system.isOptSet("controller_mode") and system.config['controller_mode'] in ('cc', 'pro')):
        extraOptions['Extension']   = 'Classic'
        wiiMapping['x'] = 'Classic/Buttons/X'
        wiiMapping['y'] = 'Classic/Buttons/Y'
        wiiMapping['b'] = 'Classic/Buttons/B'
        wiiMapping['a'] = 'Classic/Buttons/A'
        wiiMapping['select'] = 'Classic/Buttons/-'
        wiiMapping['start'] = 'Classic/Buttons/+'
        wiiMapping['up'] = 'Classic/D-Pad/Up'
        wiiMapping['down'] = 'Classic/D-Pad/Down'
        wiiMapping['left'] = 'Classic/D-Pad/Left'
        wiiMapping['right'] = 'Classic/D-Pad/Right'
        wiiMapping['joystick1up'] = 'Classic/Left Stick/Up'
        wiiMapping['joystick1left'] = 'Classic/Left Stick/Left'
        wiiMapping['joystick2up'] = 'Classic/Right Stick/Up'
        wiiMapping['joystick2left'] = 'Classic/Right Stick/Left'
        if (".cc." in rom.name or system.config['controller_mode'] == 'cc'):
            wiiMapping['pageup'] = 'Classic/Buttons/ZL'
            wiiMapping['pagedown'] = 'Classic/Buttons/ZR'
            wiiMapping['l2'] = 'Classic/Triggers/L'
            wiiMapping['r2'] = 'Classic/Triggers/R'
        else:
            wiiMapping['pageup'] = 'Classic/Triggers/L'
            wiiMapping['pagedown'] = 'Classic/Triggers/R'
            wiiMapping['l2'] = 'Classic/Buttons/ZL'
            wiiMapping['r2'] = 'Classic/Buttons/ZR'

    # This section allows a per ROM override of the default key options.
    configname = rom.with_name(rom.name + ".cfg")       # Define ROM configuration name
    if configname.is_file():  # File exists
        import ast
        with configname.open() as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                wiiMapping.update(res)
                line = cconfig.readline()

    eslog.debug(f"Extra Options: {extraOptions}")
    eslog.debug(f"Wii Mappings: {wiiMapping}")

    generateControllerConfig_any(system, playersControllers, wheels, "WiimoteNew.ini", "Wiimote", wiiMapping, wiiReverseAxes, None, extraOptions)

def generateControllerConfig_gamecube(system: Emulator, playersControllers: ControllerMapping, wheels: DeviceInfoMapping, rom: Path) -> None:
    gamecubeMapping = {
        'b':             'Buttons/B',
        'a':             'Buttons/A',
        'y':             'Buttons/Y',
        'x':             'Buttons/X',
        'pagedown':      'Buttons/Z',
        'pageup':        None,
        'start':         'Buttons/Start',
        'l2':            'Triggers/L',
        'r2':            'Triggers/R',
        'up':            'D-Pad/Up',
        'down':          'D-Pad/Down',
        'left':          'D-Pad/Left',
        'right':         'D-Pad/Right',
        'joystick1up':   'Main Stick/Up',
        'joystick1left': 'Main Stick/Left',
        'joystick2up':   'C-Stick/Up',
        'joystick2left': 'C-Stick/Left',
        'hotkey':        'Buttons/Hotkey'
    }
    gamecubeReverseAxes = {
        'Main Stick/Up':   'Main Stick/Down',
        'Main Stick/Left': 'Main Stick/Right',
        'C-Stick/Up':      'C-Stick/Down',
        'C-Stick/Left':    'C-Stick/Right'
    }
    # If joystick1up is missing on the pad, use up instead, and if l2/r2 is missing, use l1/r1
    gamecubeReplacements = {
        'joystick1up':    'up',
        'joystick1left':  'left',
        'joystick1down':  'down',
        'joystick1right': 'right',
        'l2':             'pageup',
        'r2':             'pagedown'
    }

    # This section allows a per ROM override of the default key options.
    configname = rom.with_name(rom.name + '.cfg')       # Define ROM configuration name
    if configname.is_file():  # File exists
        import ast
        with configname.open() as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                gamecubeMapping.update(res)
                line = cconfig.readline()

    generateControllerConfig_any(system, playersControllers, wheels, "GCPadNew.ini", "GCPad", gamecubeMapping, gamecubeReverseAxes, gamecubeReplacements)

def removeControllerConfig_gamecube() -> None:
    configFileName = DOLPHIN_CONFIG / "GCPadNew.ini"
    if configFileName.is_file():
        configFileName.unlink()

def generateControllerConfig_realwiimotes(filename: str, anyDefKey: str) -> None:
    configFileName = DOLPHIN_CONFIG / filename
    f = codecs.open(str(configFileName), "w", encoding="utf_8_sig")
    nplayer = 1
    while nplayer <= 4:
        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Source = 2\n")
        nplayer += 1
    f.write("[BalanceBoard]\nSource = 2\n")
    f.write
    f.close()

def generateControllerConfig_guns(filename: str, anyDefKey: str, metadata: Mapping[str, str], guns: GunMapping) -> None:
    configFileName = DOLPHIN_CONFIG / filename
    f = codecs.open(str(configFileName), "w", encoding="utf_8_sig")

    # In case of two pads having the same name, dolphin wants a number to handle this
    double_pads: dict[str, int] = {}

    nplayer = 1
    while nplayer <= 4:
        if len(guns) >= nplayer:
            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write("Source = 1\n")
            f.write("Extension = Nunchuk\n")

            dolphinMappingNames = {
                "a":             "Buttons/A",
                "b":             "Buttons/B",
                "home":          "Buttons/Home",
                "-":             "Buttons/-",
                "1":             "Buttons/1",
                "2":             "Buttons/2",
                "+":             "Buttons/+",
                "up":            "D-Pad/Up",
                "down":          "D-Pad/Down",
                "left":          "D-Pad/Left",
                "right":         "D-Pad/Right",
                "tiltforward":   "Tilt/Forward",
                "tiltbackward":  "Tilt/Backward",
                "tiltleft":      "Tilt/Left",
                "tiltright":     "Tilt/Right",
                "shake":         "Shake/Z",
                "c":             "Nunchuk/Buttons/C",
                "z":             "Nunchuk/Buttons/Z"
            }

            gunMapping = {
                "a":            "action",
                "b":            "trigger",
                "home":         "sub3",
                "-":            "select",
                "1":            "sub1",
                "2":            "sub2",
                "+":            "start",
                "up":           "up",
                "down":         "down",
                "left":         "left",
                "right":        "right",
                "tiltforward":  "",
                "tiltbackward": "",
                "tiltleft":     "",
                "tiltright":    "",
                "shake":        "",
                "c":            "",
                "z":            ""
            }

            gunButtons = {
                "trigger": { "code": "BTN_LEFT",   "button": "left"   },
                "action":  { "code": "BTN_RIGHT",  "button": "right"  },
                "start":   { "code": "BTN_MIDDLE", "button": "middle" },
                "select":  { "code": "BTN_1",      "button": "1"      },
                "sub1":    { "code": "BTN_2",      "button": "2"      },
                "sub2":    { "code": "BTN_3",      "button": "3"      },
                "sub3":    { "code": "BTN_4",      "button": "4"      },
                "up":      { "code": "BTN_5",      "button": "5"      },
                "down":    { "code": "BTN_6",      "button": "6"      },
                "left":    { "code": "BTN_7",      "button": "7"      },
                "right":   { "code": "BTN_8",      "button": "8"      }
            }

            gundevname = guns[nplayer-1]["name"]

            # Handle x pads having the same name
            nsamepad = 0
            if gundevname.strip() in double_pads:
                nsamepad = double_pads[gundevname.strip()]
            else:
                nsamepad = 0
                double_pads[gundevname.strip()] = nsamepad+1

            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write("Device = evdev/" + str(nsamepad).strip() + "/" + gundevname.strip() + "\n")

            buttons = guns[nplayer-1]["buttons"]
            eslog.debug(f"Gun : {buttons}")

            # custom remapping
            # erase values
            for btn in gunButtons:
                if "gun_"+btn in metadata:
                    for mval in metadata["gun_"+btn].split(","):
                        if mval in gunMapping:
                            for x in gunMapping:
                                if gunMapping[x] == btn:
                                    eslog.info("erasing {}".format(x))
                                    gunMapping[x] = ""
                        else:
                            eslog.info("custom gun mapping ignored for {} => {} (invalid value)".format(btn, mval))
            # setting values
            for btn in gunButtons:
                if "gun_"+btn in metadata:
                    for mval in metadata["gun_"+btn].split(","):
                        if mval in gunMapping:
                            gunMapping[mval] = btn
                            eslog.info("setting {} to {}".format(mval, btn))

            # write buttons
            for btn in dolphinMappingNames:
                val = ""
                if btn in gunMapping and gunMapping[btn] != "":
                    if gunMapping[btn] in gunButtons:
                        if gunButtons[gunMapping[btn]]["button"] in buttons:
                            val = gunButtons[gunMapping[btn]]["code"]
                        else:
                            eslog.debug("gun has not the button {}".format(gunButtons[gunMapping[btn]]["button"]))
                    else:
                        eslog.debug("cannot map the button {}".format(gunMapping[btn]))
                f.write(dolphinMappingNames[btn]+" = `"+val+"`\n")

            # map ir
            if "gun_"+"ir_up" not in metadata:
                f.write("IR/Up = `Axis 1-`\n")
            if "gun_"+"ir_down" not in metadata:
                f.write("IR/Down = `Axis 1+`\n")
            if "gun_"+"ir_left" not in metadata:
                f.write("IR/Left = `Axis 0-`\n")
            if "gun_"+"ir_right" not in metadata:
                f.write("IR/Right = `Axis 0+`\n")

            # specific games configurations
            specifics = {
                "vertical_offset": "IR/Vertical Offset",
                "yaw":             "IR/Total Yaw",
                "pitch":           "IR/Total Pitch",
                "ir_up":           "IR/Up",
                "ir_down":         "IR/Down",
                "ir_left":         "IR/Left",
                "ir_right":        "IR/Right",
            }
            for spe in specifics:
                if "gun_"+spe in metadata:
                    f.write("{} = {}\n".format(specifics[spe], metadata["gun_"+spe]))
        nplayer += 1
    f.write
    f.close()

def generateHotkeys(playersControllers: ControllerMapping) -> None:
    configFileName = DOLPHIN_CONFIG / "Hotkeys.ini"
    f = codecs.open(str(configFileName), "w", encoding="utf_8_sig")

    hotkeysMapping: dict[str, str | None] = {
        'a':             'Keys/Reset',
        'b':             'Keys/Toggle Pause',
        'x':             'Keys/Load from selected slot',
        'y':             'Keys/Save to selected slot',
        'r2':            None,
        'start':         'Keys/Exit',
        'pageup':        'Keys/Take Screenshot',
        'pagedown':      'Keys/Toggle 3D Side-by-side',
        'up':            'Keys/Increase Selected State Slot',
        'down':          'Keys/Decrease Selected State Slot',
        'left':          None,
        'right':         None,
        'joystick1up':   None,
        'joystick1left': None,
        'joystick2up':   None,
        'joystick2left': None
    }

    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer == 1:
            f.write("[Hotkeys1]" + "\n")
            f.write("Device = evdev/0/" + pad.real_name.strip() + "\n")

            # Search the hotkey button
            hotkey = None
            if "hotkey" not in pad.inputs:
                return
            hotkey = pad.inputs["hotkey"]
            if hotkey.type != "button":
                return

            for x in pad.inputs:
                input = pad.inputs[x]

                keyname = None
                if input.name in hotkeysMapping:
                    keyname = hotkeysMapping[input.name]

                # Write the configuration for this key
                if keyname is not None:
                    write_key(f, keyname, input.type, input.id, input.value, pad.axis_count, False, hotkey.id, None)

                #else:
                #    f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")

        nplayer += 1

    f.write
    f.close()

def get_AltMapping(system: Emulator, nplayer: int, anyMapping: Mapping[str, str]) -> dict[str, str]:
    mapping = dict(anyMapping)
    # Fixes default gamecube style controller mapping for ES from es_input (gc A confirm/gc B cancel)
    if system.isOptSet(f"dolphin_port_{nplayer}_type") and system.config[f'dolphin_port_{nplayer}_type'] == '6b':
        mapping['a'] = 'Buttons/B'
        mapping['b'] = 'Buttons/A'

    # Only rotate inputs for standard controller type so it doesn't effect other controller types.
    if not system.isOptSet(f"dolphin_port_{nplayer}_type") or system.config.get(f'dolphin_port_{nplayer}_type') == '6a':
        # Check for rotate mappings settings and adjust
        if system.isOptSet(f"alt_mappings_{nplayer}") and system.getOptBoolean(f"alt_mappings_{nplayer}") == True:

            mapping['a'] = 'Buttons/X'
            mapping['b'] = 'Buttons/A'
            mapping['y'] = 'Buttons/B'
            mapping['x'] = 'Buttons/Y'

    return mapping

def generateControllerConfig_any(system: Emulator, playersControllers: ControllerMapping, wheels: DeviceInfoMapping, filename: str, anyDefKey: str, anyMapping: Mapping[str, str], anyReverseAxes: Mapping[str, str], anyReplacements: Mapping[str, str] | None, extraOptions: Mapping[str, str] = {}) -> None:
    configFileName = DOLPHIN_CONFIG / filename
    f = codecs.open(str(configFileName), "w", encoding="utf_8_sig")
    nplayer = 1
    nsamepad = 0

    # In case of two pads having the same name, dolphin wants a number to handle this
    double_pads: dict[str, int] = {}

    for playercontroller, pad in sorted(playersControllers.items()):
        # Handle x pads having the same name
        if pad.real_name.strip() in double_pads:
            nsamepad = double_pads[pad.real_name.strip()]
        else:
            nsamepad = 0
        double_pads[pad.real_name.strip()] = nsamepad+1

        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Device = evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + "\n")

        if system.isOptSet("use_pad_profiles") and system.getOptBoolean("use_pad_profiles") == True:
            if not generateControllerConfig_any_from_profiles(f, pad, system):
                generateControllerConfig_any_auto(f, pad, anyMapping, anyReverseAxes, anyReplacements, extraOptions, system, nplayer, nsamepad)
        else:
            if pad.device_path in wheels:
                generateControllerConfig_wheel(f, pad, nplayer)
            else:
                generateControllerConfig_any_auto(f, pad, anyMapping, anyReverseAxes, anyReplacements, extraOptions, system, nplayer, nsamepad)

        nplayer += 1
    f.write
    f.close()

def generateControllerConfig_wheel(f: codecs.StreamReaderWriter, pad: Controller, nplayer: int) -> None:
    wheelMapping = {
        "select":         "Buttons/Z",
        "start":          "Buttons/Start",
        "up":             "D-Pad/Up",
        "down":           "D-Pad/Down",
        "left":           "D-Pad/Left",
        "right":          "D-Pad/Right",
        "a":              "Buttons/A",
        "b":              "Buttons/B",
        "x":              "Buttons/X",
        "y":              "Buttons/Y",
        "pageup":         "Triggers/L-Analog",
        "pagedown":       "Triggers/R-Analog",
        "r2":             "Main Stick/Up",
        "l2":             "Main Stick/Down",
        "joystick1left":  "Main Stick/Left",
        "joystick1right": "Main Stick/Right",
    }

    eslog.debug("configuring wheel for pad {}".format(pad.real_name))

    f.write(f"Rumble/Motor = Constant\n") # only Constant works on my wheel. maybe some other values could be good
    f.write(f"Rumble/Motor/Range = -100.\n") # value must be negative, otherwise the center is located in extremes (left/right)
    f.write(f"Main Stick/Dead Zone = 0.\n") # not really needed while this is the default

    for x in pad.inputs:
        input = pad.inputs[x]
        if input.name in wheelMapping:
            write_key(f, wheelMapping[input.name], input.type, input.id, input.value, pad.axis_count, False, None, None)
            if input.name == "joystick1left" and "joystick1right" in wheelMapping:
                write_key(f, wheelMapping["joystick1right"], input.type, input.id, input.value, pad.axis_count, True, None, None)


def generateControllerConfig_any_auto(f: codecs.StreamReaderWriter, pad: Controller, anyMapping: Mapping[str, str], anyReverseAxes: Mapping[str, str], anyReplacements: Mapping[str, str] | None, extraOptions: Mapping[str, str], system: Emulator, nplayer: int, nsamepad: int) -> None:
    for opt in extraOptions:
        f.write(opt + " = " + extraOptions[opt] + "\n")

    # Check for alt input mappings
    currentMapping = get_AltMapping(system, nplayer, anyMapping)
    # Apply replacements
    if anyReplacements is not None:
        for x in anyReplacements:
            if x not in pad.inputs and x in currentMapping:
                currentMapping[anyReplacements[x]] = currentMapping[x]
                if x == "joystick1up":
                    currentMapping[anyReplacements["joystick1down"]] = anyReverseAxes[currentMapping["joystick1up"]]
                if x == "joystick1left":
                    currentMapping[anyReplacements["joystick1right"]] = anyReverseAxes[currentMapping["joystick1left"]]
                if x == "joystick2up":
                    currentMapping[anyReplacements["joystick2down"]] = anyReverseAxes[currentMapping["joystick2up"]]
                if x == "joystick2left":
                    currentMapping[anyReplacements["joystick2right"]] = anyReverseAxes[currentMapping["joystick2left"]]

    for x in pad.inputs:
        input = pad.inputs[x]

        keyname = None
        if input.name in currentMapping:
            keyname = currentMapping[input.name]

        # Write the configuration for this key
        if keyname is not None:
            write_key(f, keyname, input.type, input.id, input.value, pad.axis_count, False, None, None)
            if 'Triggers' in keyname and input.type == 'axis':
                write_key(f, keyname + '-Analog', input.type, input.id, input.value, pad.axis_count, False, None, None)
            if 'Buttons/Z' in keyname and "pageup" in pad.inputs:
                # Create dictionary for both L1/R1 to pass to write_key
                gcz_ids = {
                    "pageup": pad.inputs["pageup"].id,
                    "pagedown": pad.inputs["pagedown"].id
                }
                write_key(f, keyname, input.type, input.id, input.value, pad.axis_count, False, None, gcz_ids)
        # Write the 2nd part
        if input.name in { "joystick1up", "joystick1left", "joystick2up", "joystick2left"} and keyname is not None:
            write_key(f, anyReverseAxes[keyname], input.type, input.id, input.value, pad.axis_count, True, None, None)
        # DualShock Motion control
        if system.isOptSet("dsmotion") and system.getOptBoolean("dsmotion") == True:
            f.write("IMUGyroscope/Pitch Up = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Gyro X-`\n")
            f.write("IMUGyroscope/Pitch Down = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Gyro X+`\n")
            f.write("IMUGyroscope/Roll Left = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Gyro Z-`\n")
            f.write("IMUGyroscope/Roll Right = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Gyro Z+`\n")
            f.write("IMUGyroscope/Yaw Left = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Gyro Y-`\n")
            f.write("IMUGyroscope/Yaw Right = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Gyro Y+`\n")
            f.write("IMUIR/Recenter = `Button 10`\n")
            f.write("IMUAccelerometer/Left = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Accel X-`\n")
            f.write("IMUAccelerometer/Right = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Accel X+`\n")
            f.write("IMUAccelerometer/Forward = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Accel Z-`\n")
            f.write("IMUAccelerometer/Backward = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Accel Z+`\n")
            f.write("IMUAccelerometer/Up = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Accel Y-`\n")
            f.write("IMUAccelerometer/Down = `evdev/" + str(nsamepad).strip() + "/" + pad.real_name.strip() + " Motion Sensors:Accel Y+`\n")
        # Mouse to emulate Wiimote
        if system.isOptSet("mouseir") and system.getOptBoolean("mouseir") == True:
            f.write("IR/Up = `Cursor Y-`\n")
            f.write("IR/Down = `Cursor Y+`\n")
            f.write("IR/Left = `Cursor X-`\n")
            f.write("IR/Right = `Cursor X+`\n")
        # Rumble option
        if system.isOptSet("rumble") and system.getOptBoolean("rumble") == True:
            f.write("Rumble/Motor = Weak\n")
        # Deadzone setting
        if system.isOptSet(f"deadzone_{nplayer}"):
            f.write(f"Main Stick/Dead Zone = {system.config['deadzone_' + str(nplayer)]}\n")
            f.write(f"C-Stick/Dead Zone = {system.config['deadzone_' + str(nplayer)]}\n")
        else:
            f.write(f"Main Stick/Dead Zone = 5.0\n")
            f.write(f"C-Stick/Dead Zone = 5.0\n")
        # JS gate size
        if system.isOptSet(f"jsgate_size_{nplayer}") and system.config[f'jsgate_size_{nplayer}'] != 'normal':
            if system.config[f'jsgate_size_{nplayer}'] == 'smaller':
                f.write(f"Main Stick/Gate Size = 64.0\n")
                f.write(f"C-Stick/Gate Size = 56.0\n")
            if system.config[f'jsgate_size_{nplayer}'] == 'larger':
                f.write(f"Main Stick/Gate Size = 95.0\n")
                f.write(f"C-Stick/Gate Size = 88.0\n")

def generateControllerConfig_any_from_profiles(f: codecs.StreamReaderWriter, pad: Controller, system: Emulator) -> bool:
    glob_path: Path | None = None
    if system.name == "gamecube":
        glob_path = DOLPHIN_CONFIG / "Profiles" / "GCPad"
    if system.name == "wii":
        glob_path = DOLPHIN_CONFIG / "Profiles" / "Wiimote"

    if glob_path is None:
        return False

    for profileFile in glob_path.glob("*.ini"):
        try:
            eslog.debug(f"Looking profile : {profileFile}")
            profileConfig = CaseSensitiveConfigParser(interpolation=None)
            profileConfig.read(profileFile)
            profileDevice = profileConfig.get("Profile","Device")
            eslog.debug(f"Profile device : {profileDevice}")

            deviceVals = re.match("^([^/]*)/[0-9]*/(.*)$", profileDevice)
            if deviceVals is not None:
                if deviceVals.group(1) == "evdev" and deviceVals.group(2).strip() == pad.real_name.strip():
                    eslog.debug("Eligible profile device found")
                    for key, val in profileConfig.items("Profile"):
                        if key != "Device":
                            f.write(f"{key} = {val}\n")
                    return True
        except:
            eslog.error(f"profile {profileFile} : FAILED")

    return False

def write_key(f: codecs.StreamReaderWriter, keyname: str, input_type: str, input_id: str, input_value: str, input_global_id: int | None, reverse: bool, hotkey_id: str | None, gcz_ids: Mapping[str, str] | None) -> None:
    f.write(keyname + " = ")
    if hotkey_id is not None:
        f.write("`Button " + str(hotkey_id) + "` & ")
    f.write("`")
    if input_type == "button":
        # Map L1 & R1 both to Z with OR operator
        if keyname == "Buttons/Z" and gcz_ids is not None:
            f.write(f"Button {gcz_ids['pageup']}`|`Button {gcz_ids['pagedown']}")
        else:
            f.write("Button " + str(input_id))
    elif input_type == "hat":
        if input_value == "1" or input_value == "4":        # up or down
            f.write("Axis " + str(int(input_global_id)+1+int(input_id)*2))
        else:
            f.write("Axis " + str(int(input_global_id)+int(input_id)*2))
        if input_value == "1" or input_value == "8":        # up or left
            f.write("-")
        else:
            f.write("+")
    elif input_type == "axis":
        # Ensure full values are used for analog triggers
        prefix = "Full " if keyname in {"Triggers/L-Analog", "Triggers/R-Analog"} else ""
        if (reverse and input_value == "-1") or (not reverse and input_value == "1"):
            f.write(f"{prefix}Axis " + str(input_id) + "+")
        else:
            f.write(f"{prefix}Axis " + str(input_id) + "-")
    f.write("`\n")
