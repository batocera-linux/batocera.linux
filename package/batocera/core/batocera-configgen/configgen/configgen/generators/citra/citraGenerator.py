#!/usr/bin/env python

import Command
import batoceraFiles # GLOBAL VARIABLES
from generators.Generator import Generator
import shutil
import os
from os import environ
import configparser

class CitraGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        CitraGenerator.writeCITRAConfig(batoceraFiles.CONF + "/citra-emu/qt-config.ini", system, playersControllers)

        commandArray = ['/usr/bin/citra-qt', rom]
        return Command.Command(array=commandArray, env={ \
        "XDG_CONFIG_HOME":batoceraFiles.CONF, \
        "XDG_DATA_HOME":batoceraFiles.SAVES + "/3ds", \
        "XDG_CACHE_HOME":batoceraFiles.CACHE, \
        "XDG_RUNTIME_DIR":batoceraFiles.SAVES + "/3ds/citra-emu", \
        "QT_QPA_PLATFORM":"xcb"})

    # Show mouse on screen
    def getMouseMode(self, config):
        return True

    @staticmethod
    def writeCITRAConfig(citraConfigFile, system, playersControllers):
        # Pads
        citraButtons = {
            "button_a":      "a",
            "button_b":      "b",
            "button_x":      "x",
            "button_y":      "y",
            "button_up":     "up",
            "button_down":   "down",
            "button_left":   "left",
            "button_right":  "right",
            "button_l":      "pageup",
            "button_r":      "pagedown",
            "button_start":  "start",
            "button_select": "select",
            "button_zl":     "l2",
            "button_zr":     "r2",
            "button_home":   "hotkey"
        }

        citraAxis = {
            "circle_pad":    "joystick1",
            "c_stick":       "joystick2"
        }

        # ini file
        citraConfig = configparser.RawConfigParser(strict=False)
        citraConfig.optionxform=str             # Add Case Sensitive comportement
        if os.path.exists(citraConfigFile):
            citraConfig.read(citraConfigFile)

        ## [LAYOUT]
        if not citraConfig.has_section("Layout"):
            citraConfig.add_section("Layout")
        # Screen Layout
        citraConfig.set("Layout", "custom_layout", "0")
        if system.isOptSet('citra_screen_layout'):
            tab = system.config["citra_screen_layout"].split('-')
            citraConfig.set("Layout", "swap_screen",   tab[1])
            citraConfig.set("Layout", "layout_option", tab[0])
        else:
            citraConfig.set("Layout", "swap_screen",   "false")
            citraConfig.set("Layout", "layout_option", "4")

        ## [SYSTEM]
        if not citraConfig.has_section("System"):
            citraConfig.add_section("System")
        # New 3DS Version
        if system.isOptSet('citra_is_new_3ds') and system.config["citra_is_new_3ds"] == '1':
            citraConfig.set("System", "is_new_3ds", "true")
        else:
            citraConfig.set("System", "is_new_3ds", "false")
        # Language
        citraConfig.set("System", "region_value", str(getCitraLangFromEnvironment()))

        ## [UI]
        if not citraConfig.has_section("UI"):
            citraConfig.add_section("UI")       
        # Start Fullscreen
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            citraConfig.set("UI", "fullscreen",       "false")
            citraConfig.set("UI", "showStatusBar",    "true")
        else:
            citraConfig.set("UI", "fullscreen",       "true")
        # Batocera - Defaults
        citraConfig.set("UI", "displayTitleBars", "false")
        citraConfig.set("UI", "displaytitlebars", "false") # Emulator Bug
        citraConfig.set("UI", "firstStart",       "false")
        citraConfig.set("UI", "hideInactiveMouse", "true")
        citraConfig.set("UI", "enable_discord_presence", "false")
        citraConfig.set("UI", "firstStart", "false")
        # Remove pop-up prompt on start
        citraConfig.set("UI", "calloutFlags", "1")
        # Close without confirmation
        citraConfig.set("UI", "confirmClose",     "false")
        citraConfig.set("UI", "confirmclose",     "false") # Emulator Bug

        ## [RENDERER]
        if not citraConfig.has_section("Renderer"):
            citraConfig.add_section("Renderer")
        # Force Hardware Rrendering / Shader or nothing works fine
        citraConfig.set("Renderer", "use_hw_renderer", "true")
        citraConfig.set("Renderer", "use_hw_shader",   "true")
        citraConfig.set("Renderer", "use_shader_jit",  "true")
        # Use VSYNC
        if system.isOptSet('citra_use_vsync_new') and system.config["citra_use_vsync_new"] == '0':
            citraConfig.set("Renderer", "use_vsync_new", "false")
        else:
            citraConfig.set("Renderer", "use_vsync_new", "true")
        # Resolution Factor
        if system.isOptSet('citra_resolution_factor'):
            citraConfig.set("Renderer", "resolution_factor", system.config["citra_resolution_factor"])
        else:
            citraConfig.set("Renderer", "resolution_factor", "1")
        # Use Frame Limit
        if system.isOptSet('citra_use_frame_limit') and system.config["citra_use_frame_limit"] == '0':
            citraConfig.set("Renderer", "use_frame_limit", "false")
        else:
            citraConfig.set("Renderer", "use_frame_limit", "true")
        
        ## [WEB SERVICE]
        if not citraConfig.has_section("WebService"):
            citraConfig.add_section("WebService")
        citraConfig.set("WebService", "enable_telemetry",  "false")

        ## [UTILITY]
        if not citraConfig.has_section("Utility"):
            citraConfig.add_section("Utility")
        # Disk Shader Cache
        if system.isOptSet('citra_use_disk_shader_cache') and system.config["citra_use_disk_shader_cache"] == '1':
            citraConfig.set("Utility", "use_disk_shader_cache", "true")
        else:
            citraConfig.set("Utility", "use_disk_shader_cache", "false")
        # Custom Textures
        if system.isOptSet('citra_custom_textures') and system.config["citra_custom_textures"] != '0':
            tab = system.config["citra_custom_textures"].split('-')
            citraConfig.set("Utility", "custom_textures",  "true")
            if tab[1] == 'normal':
                citraConfig.set("Utility", "preload_textures", "false")
            else:
                citraConfig.set("Utility", "preload_textures", "true") # It's not working from ES for now, only from the emulator menu
        else:
            citraConfig.set("Utility", "custom_textures",  "false")
            citraConfig.set("Utility", "preload_textures", "false")

        ## [CONTROLS]
        if not citraConfig.has_section("Controls"):
            citraConfig.add_section("Controls")

        # Options required to load the functions when the configuration file is created
        if not citraConfig.has_option("Controls", "profiles\\size"):
            citraConfig.set("Controls", "profile", 0)
            citraConfig.set("Controls", "profile\\default", "true")    
            citraConfig.set("Controls", "profiles\\1\\name", "default")
            citraConfig.set("Controls", "profiles\\1\\name\\default", "true")
            citraConfig.set("Controls", "profiles\\size", 1)

        for index in playersControllers :
            controller = playersControllers[index]
            # We only care about player 1
            if controller.player != "1":
                continue
            for x in citraButtons:
                citraConfig.set("Controls", "profiles\\1\\" + x, f'"{CitraGenerator.setButton(citraButtons[x], controller.guid, controller.inputs)}"')
            for x in citraAxis:
                citraConfig.set("Controls", "profiles\\1\\" + x, f'"{CitraGenerator.setAxis(citraAxis[x], controller.guid, controller.inputs)}"')
            break

        ## Update the configuration file
        if not os.path.exists(os.path.dirname(citraConfigFile)):
            os.makedirs(os.path.dirname(citraConfigFile))
        with open(citraConfigFile, 'w') as configfile:
            citraConfig.write(configfile)

    @staticmethod
    def setButton(key, padGuid, padInputs):
        # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("button:{},guid:{},engine:sdl").format(input.id, padGuid)
            elif input.type == "hat":
                return ("engine:sdl,guid:{},hat:{},direction:{}").format(padGuid, input.id, CitraGenerator.hatdirectionvalue(input.value))
            elif input.type == "axis":
                # Untested, need to configure an axis as button / triggers buttons to be tested too
                return ("engine:sdl,guid:{},axis:{},direction:{},threshold:{}").format(padGuid, input.id, "+", 0.5)

    @staticmethod
    def setAxis(key, padGuid, padInputs):
        inputx = -1
        inputy = -1

        if key == "joystick1":
            inputx = padInputs["joystick1left"]
        elif key == "joystick2":
            inputx = padInputs["joystick2left"]

        if key == "joystick1":
            inputy = padInputs["joystick1up"]
        elif key == "joystick2":
            inputy = padInputs["joystick2up"]

        return ("axis_x:{},guid:{},axis_y:{},engine:sdl").format(inputx.id, padGuid, inputy.id)

    @staticmethod
    def hatdirectionvalue(value):
        if int(value) == 1:
            return "up"
        if int(value) == 4:
            return "down"
        if int(value) == 2:
            return "right"
        if int(value) == 8:
            return "left"
        return "unknown"

# Lauguage auto setting
def getCitraLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "zh_CN": 6, "ko_KR": 7, "hu_HU": 8, "pt_PT": 9, "ru_RU": 10, "zh_TW": 11 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
