from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class DrasticGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "drastic",
            "keys": { 
                "exit": "KEY_ESC",
                "save_state": "KEY_F5",
                "restore_state": "KEY_F7",
                "menu": "KEY_F1",
                "fastforward": "KEY_TAB",
                "swap_screen": "KEY_F2"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        drastic_root = CONFIGS / "drastic"
        drastic_bin = drastic_root / "drastic"
        drastic_conf = drastic_root / "config" / "drastic.cfg"

        mkdir_if_not_exists(drastic_root)
        mkdir_if_not_exists(drastic_conf.parent)

        if not drastic_bin.exists():
            shutil.copytree("/usr/share/drastic", drastic_root, dirs_exist_ok=True)
            drastic_bin.chmod(0o0775)

        # Settings, Language and ConfirmPowerOff
        f = drastic_conf.open("w", encoding="ascii")

        esvaluedrastichires = system.config.get_int("drastic_hires", 0)
        esvaluedrasticthreaded = system.config.get_int("drastic_threaded", 0)
        esvaluedrasticfix2d = system.config.get_int("drastic_fix2d", 0)
        esvaluedrasticscreenorientation = system.config.get_int("drastic_screen_orientation", 0)
        esvaluedrasticframeskiptype = system.config.get_int("drastic_frameskip_type", 0)
        esvaluedrasticframeskipvalue = system.config.get_int("drastic_frameskip_value", 1)

        textList = [
            "show_frame_counter"           + " = 0",
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
            "safe_frameskip"               + " = 1",                                   #Needed for automatic frameskipping to actually work.
            "disable_edge_marking"         + " = 1",                                   #will prevent edge marking. It draws outlines around some 3D models to give a cel-shaded effect. Since DraStic doesn't emulate anti-aliasing, it'll cause edges to look harsher than they may on a real DS.
            "fix_main_2d_screen"           + f" = {esvaluedrasticfix2d}",              #Top Screen will always be the Action Screen (for 2d games like Sonic)
            "hires_3d"                     + f" = {esvaluedrastichires}",              #High Resolution 3D Rendering
            "threaded_3d"                  + f" = {esvaluedrasticthreaded}",           #MultiThreaded 3D Rendering - Improves perf in 3D - can cause glitch.
            "screen_orientation"           + f" = {esvaluedrasticscreenorientation}",  #Vertical/Horizontal/OneScreen
            "screen_scaling"               + " = 0",                                   #No Scaling/Stretch Aspect/1x2x/2x1x/TvSplit
            "screen_swap "                 + " = 0"
        ]

        # Write the cfg file
        for line in textList:
            f.write(line)
            f.write("\n")
        f.close()

        os.chdir(drastic_root)
        commandArray = [drastic_bin, rom]

        # Base environment setup
        cmd_env = {
            'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
            'LD_PRELOAD': '/usr/lib/libdrastouch.so',
            'SDL_TOUCH_MOUSE_EVENTS': '0',
        }

        # Apply screen shader if configured and not set to None/none
        drastic_shader = system.config.get("drastic_shader", "none")
        if drastic_shader and drastic_shader != "none":
            cmd_env['DSHOOK_SHADER'] = drastic_shader

        # Apply microphone threshold if configured and enabled
        drastic_mic = system.config.get("drastic_mic_threshold", "0.0")
        try:
            if float(drastic_mic) > 0.0:
                cmd_env['DSHOOK_MIC_THRESH'] = drastic_mic
        except (ValueError, TypeError):
            pass

        return Command.Command(
            array=commandArray,
            env=cmd_env
        )

# Language auto-setting
def getDrasticLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
