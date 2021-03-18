#!/usr/bin/env python

from generators.Generator import Generator
import Command
import batoceraFiles
import configparser
import os.path
from os import environ

class DuckstationGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["duckstation", "-batch", "-fullscreen", "--", rom ]

        settings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        settings.optionxform = str
        settings_path = batoceraFiles.SAVES + "/duckstation/settings.ini"
        if os.path.exists(settings_path):
            settings.read(settings_path)

        # main
        if not settings.has_section("Main"):
            settings.add_section("Main")
        settings.set("Main", "SettingsVersion", "3") # probably to be updated in the future
        settings.set("Main", "Language", getLangFromEnvironment())
        settings.set("Main", "ConfirmPowerOff", "false")

        # controller backend
        settings.set("Main","ControllerBackend", "SDL")

        # bios
        if not settings.has_section("BIOS"):
            settings.add_section("BIOS")
        settings.set("BIOS", "SearchDirectory", "/userdata/bios")
        if system.isOptSet('fullboot') and system.getOptBoolean('fullboot') == False:
            settings.set("BIOS", "PatchFastBoot", "true")
        else:
            settings.set("BIOS", "PatchFastBoot", "false")

        # hotkeys
        if not settings.has_section("Hotkeys"):
            settings.add_section("Hotkeys")
        # force defaults to be aligned with evmapy
        settings.set("Hotkeys", "FastForward",                 "Keyboard/Tab")
        settings.set("Hotkeys", "TogglePause",                 "Keyboard/Pause")
        settings.set("Hotkeys", "PowerOff",                    "Keyboard/Escape")
        settings.set("Hotkeys", "LoadSelectedSaveState",       "Keyboard/F1")
        settings.set("Hotkeys", "SaveSelectedSaveState",       "Keyboard/F2")
        settings.set("Hotkeys", "SelectPreviousSaveStateSlot", "Keyboard/F3")
        settings.set("Hotkeys", "SelectNextSaveStateSlot",     "Keyboard/F4")
        settings.set("Hotkeys", "Screenshot",                  "Keyboard/F10")

        # controllers
        configurePads(settings, playersControllers)

        # Backend - Default OpenGL
        if not settings.has_section("GPU"):
            settings.add_section("GPU")
        if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == 'Vulkan':
            settings.set("GPU", "Renderer", "Vulkan")
        else:
            settings.set("GPU", "Renderer", "OpenGL")

        # console
        if not settings.has_section("Console"):
            settings.add_section("Console")
        settings.set("Console", "Region", "Auto")
            
        # internal resolution
        if system.isOptSet('internalresolution'):
            settings.set("GPU", "ResolutionScale", system.config["internalresolution"])
        else:
            settings.set("GPU", "ResolutionScale", "0") # 0 for auto

        # Show fps
        if not settings.has_section("UI"):
            settings.add_section("UI")
        settings.set("UI", "ShowOSDMessages", "true")
        if not settings.has_section("Display"):
            settings.add_section("Display")
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            settings.set("Display", "ShowFPS",        "true")
            settings.set("Display", "ShowSpeed",      "true")
            settings.set("Display", "ShowVPS",        "true")
            settings.set("Display", "ShowResolution", "true")
        else:
            settings.set("Display", "ShowFPS",        "false")
            settings.set("Display", "ShowSpeed",      "false")
            settings.set("Display", "ShowVPS",        "false")
            settings.set("Display", "ShowResolution", "false")

        settings.set("Display", "AspectRatio", getGfxRatioFromConfig(system.config, gameResolution))

        # Save config
        if not os.path.exists(os.path.dirname(settings_path)):
            os.makedirs(os.path.dirname(settings_path))

        with open(settings_path, 'w') as configfile:
            settings.write(configfile)

        env = {"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"}
        return Command.Command(array=commandArray, env=env)

def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9  ; 0: auto
    if "ratio" in config:
        if config["ratio"] == "4/3":
            return "4:3"
        elif config["ratio"] == "16/9":
            return "16:9"

    if ("ratio" not in config or ("ratio" in config and config["ratio"] == "auto")) and gameResolution["width"] / float(gameResolution["height"]) >= (16.0 / 9.0) - 0.1: # let a marge
            return "16:9"

    return "Auto (Game Native)"

def configurePads(settings, playersControllers):
    mappings = {
        "ButtonUp":       "up",
        "ButtonDown":     "down",
        "ButtonLeft":     "left",
        "ButtonRight":    "right",
        "ButtonSelect":   "select",
        "ButtonStart":    "start",
        "ButtonTriangle": "x",
        "ButtonCross":    "b",
        "ButtonSquare":   "y",
        "ButtonCircle":   "a",
        "ButtonL1":       "pageup",
        "ButtonL2":       "l2",
        "ButtonR1":       "pagedown",
        "ButtonR2":       "r2",
        "ButtonL3":       "l3",
        "ButtonR3":       "r3",
        "AxisLeftX":      "joystick1left",
        "AxisLeftY":      "joystick1up",
        "AxisRightX":     "joystick2left",
        "AxisRightY":     "joystick2up"
        }
    
    # clear existing config
    for i in range(1, 5):
        if settings.has_section("Controller" + str(i)):
            settings.remove_section("Controller" + str(i))
    
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        section = "Controller" + str(nplayer)
        settings.add_section(section)

        settings.set(section, "Type", "AnalogController")
        settings.set(section, "AnalogDPadInDigitalMode", "true")

        for mapping in mappings:
            if mappings[mapping] in pad.inputs:
                settings.set(section, mapping, "Controller" + str(pad.index) + "/" + input2definition(pad.inputs[mappings[mapping]]))
        nplayer = nplayer + 1

def input2definition(input):
    if input.type == "button":
        return "Button" + str(input.id)
    elif input.type == "hat":
        if input.value == "1":
            return "Hat0 Up"
        elif input.value == "2":
            return "Hat0 Right"
        elif input.value == "4":
            return "Hat0 Down"
        elif input.value == "8":
            return "Hat0 Left"
    elif input.type == "axis":
        return "Axis" + str(input.id)
    return "unknown"

def getLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": "",
                           "de_DE": "de",
                           "fr_FR": "fr",
                           "es_ES": "es",
                           "he_IL": "he",
                           "it_IT": "it",
                           "ja_JP": "ja",
                           "nl_NL": "nl",
                           "pl_PL": "pl",
                           "pt_BR": "pt-br",
                           "pt_PT": "pt-pt",
                           "ru_RU": "ru",
                           "zh_CN": "zh-cn"
    }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
