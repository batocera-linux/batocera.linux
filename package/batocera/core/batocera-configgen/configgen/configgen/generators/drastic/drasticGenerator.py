from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class DrasticGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "drastic",
            "keys": { "exit": "KEY_ESC", "save_state": "KEY_F5", "restore_state": "KEY_F7", "menu": "KEY_F1", "fastforward": "KEY_TAB" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        drastic_root = CONFIGS / "drastic"
        drastic_bin = drastic_root / "drastic"
        drastic_conf = drastic_root / "config" / "drastic.cfg"

        if not drastic_root.exists():
            shutil.copytree("/usr/share/drastic", drastic_root)

        if not drastic_bin.exists() or not filecmp.cmp("/usr/bin/drastic", drastic_bin):
            shutil.copyfile("/usr/bin/drastic", drastic_bin)
            drastic_bin.chmod(0o0775)

        # Settings, Language and ConfirmPowerOff
        f = drastic_conf.open("w", encoding="ascii")

        #Getting Values from ES
        if system.config.get("drastic_scaling") == 'nearest':
            subprocess.run(f"xxd {drastic_bin} > drastic.txt", shell=True)
            if subprocess.run("grep -q '6c69 6e65 6172' drastic.txt", shell=True).returncode == 0:
                # Swap to nearest neighbor
                subprocess.run("sed -i 's/6c69 6e65 6172/3000 0000 0000/g' drastic.txt", shell=True)
                subprocess.run(f"xxd -r drastic.txt > {drastic_bin}", shell=True)
                Path("drastic.txt").unlink()
        else:
            subprocess.run(f"xxd {drastic_bin} > drastic.txt", shell=True)
            if subprocess.run("grep -q '3000 0000 0000' drastic.txt", shell=True).returncode == 0:
                # Swap to bilinear
                subprocess.run("sed -i 's/3000 0000 0000/6c69 6e65 6172/g' drastic.txt", shell=True)
                subprocess.run(f"xxd -r drastic.txt > {drastic_bin}", shell=True)
                Path("drastic.txt").unlink()

        esvaluedrastichires = system.config.get_int("drastic_hires", 0)
        esvaluedrasticthreaded = system.config.get_int("drastic_threaded", 0)
        esvaluedrasticfix2d = system.config.get_int("drastic_fix2d", 0)
        esvaluedrasticscreenorientation = system.config.get_int("drastic_screen_orientation", 0)

        # Default to none as auto seems to be bugged (just reduces framerate by half, even when the system is otherwise capable of running at 60fps, even the rpi3 can do this).
        esvaluedrasticframeskiptype = system.config.get_int("drastic_frameskip_type", 0)
        esvaluedrasticframeskipvalue = system.config.get_int("drastic_frameskip_value", 1)

        textList = [                             # 0,1,2,3 ...
        "enable_sound"                 + " = 1",
        "compress_savestates"          + " = 1",
        "savestate_snapshot"           + " = 1",
        "firmware.username"            + " = Batocera",
        "firmware.language"            + f" = {getDrasticLangFromEnvironment()}",
        "firmware.favorite_color"      + " = 11",
        "firmware.birthday_month"      + " = 11",
        "firmware.birthday_day"        + " = 25",
        "enable_cheats"                + " = 1",
        "rtc_system_time"              + " = 1",
        "use_rtc_custom_time"          + " = 0",
        "rtc_custom_time"              + " = 0",
        "frameskip_type"               + f" = {esvaluedrasticframeskiptype}",      #None/Manual/Auto
        "frameskip_value"              + f" = {esvaluedrasticframeskipvalue}",     #1-9
        "safe_frameskip"               + " = 1",                                        #Needed for automatic frameskipping to actually work.
        "disable_edge_marking"         + " = 1",                                        #will prevent edge marking. It draws outlines around some 3D models to give a cel-shaded effect. Since DraStic doesn't emulate anti-aliasing, it'll cause edges to look harsher than they may on a real DS.
        "fix_main_2d_screen"           + f" = {esvaluedrasticfix2d}",              #Top Screen will always be the Action Screen (for 2d games like Sonic)
        "hires_3d"                     + f" = {esvaluedrastichires}",              #High Resolution 3D Rendering
        "threaded_3d"                  + f" = {esvaluedrasticthreaded}",           #MultiThreaded 3D Rendering - Improves perf in 3D - can cause glitch.
        "screen_orientation"           + f" = {esvaluedrasticscreenorientation}",  #Vertical/Horizontal/OneScreen
        "screen_scaling"               + " = 0",                                        #No Scaling/Stretch Aspect/1x2x/2x1x/TvSplit
        "screen_swap "                 + " = 0"
        ]

        # Write the cfg file
        for line in textList:
            f.write(line)
            f.write("\n")
        f.close()

        #Configuring Pad in the cfg
        configurePads(drastic_conf)

        os.chdir(drastic_root)
        commandArray = [drastic_bin, rom]
        #subprocess.Popen(commandArray, cwd=drastic_root) # Launched two times if activated
        return Command.Command(
            array=commandArray,
            env={
                'DISPLAY': '0.0',
                'LIB_FB': '3',
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })

# Language auto-setting
def getDrasticLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]

def configurePads(drastic_conf: Path):
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

    with drastic_conf.open("a", encoding="ascii") as f:
        f.write(keyboardpart)
        f.write("\n")
        f.write("\n")
        f.write(padpart)

#    def executionDirectory(self, config, rom):
#        return os.path.dirname(drastic_root)
