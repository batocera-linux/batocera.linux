#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import shutil
from shutil import copyfile
import subprocess
from subprocess import Popen
import filecmp
import configparser
import os
import sys
import settings
from os import environ

class DrasticGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        drastic_root = "/userdata/system/configs/drastic"
        drastic_bin = "/userdata/system/configs/drastic/drastic"
        drastic_conf = "/userdata/system/configs/drastic/config/drastic.cfg"
        if not os.path.exists(drastic_root):
            shutil.copytree("/usr/share/drastic", drastic_root)

        if not os.path.exists(drastic_bin) or not filecmp.cmp("/usr/bin/drastic", drastic_bin):
            shutil.copyfile("/usr/bin/drastic", drastic_bin)
            os.chmod(drastic_bin, 0o0775)

        # Settings, Language and ConfirmPowerOff
        f = open(drastic_conf, "w", encoding="ascii")

        #Getting Values from ES
        if system.isOptSet("drastic_hires") and system.config["drastic_hires"] == '1':
            esvaluedrastichires = 1
        else:
            esvaluedrastichires = 0
        
        if system.isOptSet("drastic_threaded") and system.config["drastic_threaded"] == '1':
            esvaluedrasticthreaded = 1
        else:
            esvaluedrasticthreaded = 0    
        
        if system.isOptSet("drastic_fix2d") and system.config["drastic_fix2d"] == '1':
            esvaluedrasticfix2d = 1
        else:
            esvaluedrasticfix2d = 0 
        
        if system.isOptSet("drastic_screen_orientation"):
            esvaluedrasticscreenorientation = system.config["drastic_screen_orientation"]
        else:
            esvaluedrasticscreenorientation = 0

        # Default to none as auto seems to be bugged (just reduces framerate by half, even when the system is otherwise capable of running at 60fps, even the rpi3 can do this).
        if system.isOptSet("drastic_frameskip_type"):
            esvaluedrasticframeskiptype = system.config["drastic_frameskip_type"]
        else:
            esvaluedrasticframeskiptype = 0

        if system.isOptSet("drastic_frameskip_value"):
            esvaluedrasticframeskipvalue = system.config["drastic_frameskip_value"]
        else:
            esvaluedrasticframeskipvalue = 1

        textList = [                             # 0,1,2,3 ...
        "enable_sound"                 + " = 1",
        "compress_savestates"          + " = 1",
        "savestate_snapshot"           + " = 1",
        "firmware.username"            + " = Batocera",
        "firmware.language"            + " = " + str(getDrasticLangFromEnvironment()),
        "firmware.favorite_color"      + " = 11",
        "firmware.birthday_month"      + " = 11",
        "firmware.birthday_day"        + " = 25",
        "enable_cheats"                + " = 1",
        "rtc_system_time"              + " = 1",
        "use_rtc_custom_time"          + " = 0",
        "rtc_custom_time"              + " = 0",
        "frameskip_type"               + " = " + str(esvaluedrasticframeskiptype),      #None/Manual/Auto
        "frameskip_value"              + " = " + str(esvaluedrasticframeskipvalue),     #1-9
        "safe_frameskip"               + " = 1",                                        #Needed for automatic frameskipping to actually work.
        "disable_edge_marking"         + " = 1",                                        #will prevent edge marking. It draws outlines around some 3D models to give a cel-shaded effect. Since DraStic doesn't emulate anti-aliasing, it'll cause edges to look harsher than they may on a real DS.
        "fix_main_2d_screen"           + " = " + str(esvaluedrasticfix2d),              #Top Screen will always be the Action Screen (for 2d games like Sonic)
        "hires_3d"                     + " = " + str(esvaluedrastichires),              #High Resolution 3D Rendering
        "threaded_3d"                  + " = " + str(esvaluedrasticthreaded),           #MultiThreaded 3D Rendering - Improves perf in 3D - can cause glitch.
        "screen_orientation"           + " = " + str(esvaluedrasticscreenorientation),  #Vertical/Horizontal/OneScreen
        "screen_scaling"               + " = 0",                                        #No Scaling/Stretch Aspect/1x2x/2x1x/TvSplit
        "screen_swap "                 + " = 0"
        ]
        
        # Write the cfg file
        for line in textList:
            f.write(line)
            f.write("\n")
        f.close()

        #Configuring Pad in the cfg
        configurePads(settings, system, drastic_conf)

        os.chdir(drastic_root)
        commandArray = [drastic_bin, rom]
        #subprocess.Popen(commandArray, cwd=drastic_root) # Launched two times if activated
        return Command.Command(
            array=commandArray,
            env={
                'DISPLAY': '0.0',
                'LIB_FB': '3',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })

# Language auto-setting
def getDrasticLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]

def configurePads(settings, system, drastic_conf):
    keyboardpart =''.join((
    "controls_a[CONTROL_INDEX_UP]                           = 338          # Arrow Up        \n",
    "controls_a[CONTROL_INDEX_DOWN]                         = 337          # Arrow Down      \n",
    "controls_a[CONTROL_INDEX_LEFT]                         = 336          # Arrow Left      \n",
    "controls_a[CONTROL_INDEX_RIGHT]                        = 335          # Arrow Right     \n",
    "controls_a[CONTROL_INDEX_A]                            = 101          # E               \n",
    "controls_a[CONTROL_INDEX_B]                            = 114          # R               \n",
    "controls_a[CONTROL_INDEX_X]                            = 100          # D               \n",
    "controls_a[CONTROL_INDEX_Y]                            = 102          # F               \n",
    "controls_a[CONTROL_INDEX_L]                            = 99           # C               \n",
    "controls_a[CONTROL_INDEX_R]                            = 118          # V               \n",
    "controls_a[CONTROL_INDEX_START]                        = 13           # Return          \n",
    "controls_a[CONTROL_INDEX_SELECT]                       = 32           # Space           \n",
    "controls_a[CONTROL_INDEX_HINGE]                        = 104          # H               \n",
    "controls_a[CONTROL_INDEX_TOUCH_CURSOR_UP]              = 65535        # PAD2KEY MOUSE   \n",
    "controls_a[CONTROL_INDEX_TOUCH_CURSOR_DOWN]            = 65535        # PAD2KEY MOUSE   \n",
    "controls_a[CONTROL_INDEX_TOUCH_CURSOR_LEFT]            = 65535        # PAD2KEY MOUSE   \n",
    "controls_a[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]           = 65535        # PAD2KEY MOUSE   \n",
    "controls_a[CONTROL_INDEX_TOUCH_CURSOR_PRESS]           = 360          # Left Click      \n", 
    "controls_a[CONTROL_INDEX_MENU]                         = 314          # F1              \n",
    "controls_a[CONTROL_INDEX_SAVE_STATE]                   = 318          # F5              \n",
    "controls_a[CONTROL_INDEX_LOAD_STATE]                   = 320          # F7              \n",
    "controls_a[CONTROL_INDEX_FAST_FORWARD]                 = 9            # Tab             \n",
    "controls_a[CONTROL_INDEX_SWAP_SCREENS]                 = 315          # F2              \n",
    "controls_a[CONTROL_INDEX_SWAP_ORIENTATION_A]           = 316          # F3              \n",
    "controls_a[CONTROL_INDEX_SWAP_ORIENTATION_B]           = 317          # F4              \n",
    "controls_a[CONTROL_INDEX_LOAD_GAME]                    = 65535        # DISABLED        \n",
    "controls_a[CONTROL_INDEX_QUIT]                         = 325          # F12             \n",
    "controls_a[CONTROL_INDEX_FAKE_MICROPHONE]              = 121          # Y               \n",
    #"controls_a[CONTROL_INDEX_UI_UP]                       = 105          # I               \n",  Let Drastic Choose Default
    #"controls_a[CONTROL_INDEX_UI_DOWN]                     = 107          # K               \n",  Let Drastic Choose Default
    #"controls_a[CONTROL_INDEX_UI_LEFT]                     = 106          # J               \n",  Let Drastic Choose Default
    #"controls_a[CONTROL_INDEX_UI_RIGHT]                    = 108          # L               \n",  Let Drastic Choose Default
    #"controls_a[CONTROL_INDEX_UI_SELECT]                   = 13           # Return          \n",  Let Drastic Choose Default
    #"controls_a[CONTROL_INDEX_UI_BACK]                     = 8            # BackSpace       \n",  Let Drastic Choose Default
    #"controls_a[CONTROL_INDEX_UI_EXIT]                     = 27           # Escape          \n",  Let Drastic Choose Default
    "controls_a[CONTROL_INDEX_UI_PAGE_UP]                   = 331          # PageUp          \n",
    "controls_a[CONTROL_INDEX_UI_PAGE_DOWN]                 = 334          # PageDown        \n",
    "controls_a[CONTROL_INDEX_UI_SWITCH]                    = 117          # U                 "))

    padpart =''.join((
    "controls_b[CONTROL_INDEX_UP]                           = 65535   \n",
    "controls_b[CONTROL_INDEX_DOWN]                         = 65535   \n",
    "controls_b[CONTROL_INDEX_LEFT]                         = 65535   \n",
    "controls_b[CONTROL_INDEX_RIGHT]                        = 65535   \n",
    "controls_b[CONTROL_INDEX_A]                            = 65535   \n",
    "controls_b[CONTROL_INDEX_B]                            = 65535   \n",
    "controls_b[CONTROL_INDEX_X]                            = 65535   \n",
    "controls_b[CONTROL_INDEX_Y]                            = 65535   \n",
    "controls_b[CONTROL_INDEX_L]                            = 65535   \n",
    "controls_b[CONTROL_INDEX_R]                            = 65535   \n",
    "controls_b[CONTROL_INDEX_START]                        = 65535   \n",
    "controls_b[CONTROL_INDEX_SELECT]                       = 65535   \n",
    "controls_b[CONTROL_INDEX_HINGE]                        = 65535   \n",
    "controls_b[CONTROL_INDEX_TOUCH_CURSOR_UP]              = 65535   \n",
    "controls_b[CONTROL_INDEX_TOUCH_CURSOR_DOWN]            = 65535   \n",
    "controls_b[CONTROL_INDEX_TOUCH_CURSOR_LEFT]            = 65535   \n",
    "controls_b[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]           = 65535   \n",
    "controls_b[CONTROL_INDEX_TOUCH_CURSOR_PRESS]           = 65535   \n", 
    "controls_b[CONTROL_INDEX_MENU]                         = 65535   \n",
    "controls_b[CONTROL_INDEX_SAVE_STATE]                   = 65535   \n",
    "controls_b[CONTROL_INDEX_LOAD_STATE]                   = 65535   \n",
    "controls_b[CONTROL_INDEX_FAST_FORWARD]                 = 65535   \n",
    "controls_b[CONTROL_INDEX_SWAP_SCREENS]                 = 65535   \n",
    "controls_b[CONTROL_INDEX_SWAP_ORIENTATION_A]           = 65535   \n",
    "controls_b[CONTROL_INDEX_SWAP_ORIENTATION_B]           = 65535   \n",
    "controls_b[CONTROL_INDEX_LOAD_GAME]                    = 65535   \n",
    "controls_b[CONTROL_INDEX_QUIT]                         = 65535   \n",
    "controls_b[CONTROL_INDEX_FAKE_MICROPHONE]              = 65535   \n",
    #"controls_b[CONTROL_INDEX_UI_UP]                       = 65535   \n", Let Drastic Generate for Pad
    #"controls_b[CONTROL_INDEX_UI_DOWN]                     = 65535   \n", Let Drastic Generate for Pad
    #"controls_b[CONTROL_INDEX_UI_LEFT]                     = 65535   \n", Let Drastic Generate for Pad
    #"controls_b[CONTROL_INDEX_UI_RIGHT]                    = 65535   \n", Let Drastic Generate for Pad
    #"controls_b[CONTROL_INDEX_UI_SELECT]                   = 65535   \n", Let Drastic Generate for Pad
    #"controls_b[CONTROL_INDEX_UI_BACK]                     = 65535   \n", Let Drastic Generate for Pad
    #"controls_b[CONTROL_INDEX_UI_EXIT]                     = 65535   \n", Let Drastic Generate for Pad
    "controls_b[CONTROL_INDEX_UI_PAGE_UP]                   = 65535   \n",
    "controls_b[CONTROL_INDEX_UI_PAGE_DOWN]                 = 65535   \n",
    "controls_b[CONTROL_INDEX_UI_SWITCH]                    = 65535     "))

    f = open(drastic_conf, "a", encoding="ascii")
    f.write(keyboardpart)
    f.write("\n")    
    f.write("\n")    
    f.write(padpart)
    f.close()

#    def executionDirectory(self, config, rom):
#        return os.path.dirname(drastic_root)
