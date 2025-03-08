from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...utils.configparser import CaseSensitiveConfigParser


def configureOptions(vpinballSettings: CaseSensitiveConfigParser, system: Emulator) -> None:
    # Tables are organised by folders containing the vpx file, and sub-folders with the roms, altcolor, altsound,...
    # We keep a switch to allow users with the old unique pinmame to be able to continue using vpinball (switchon)
    vpinballSettings.set("Standalone", "PinMAMEPath", system.config.get_bool("vpinball_folders", True, return_values=("./", "")))

    # Ball trail
    balltrail = system.config.get("vpinball_balltrail", "0")
    vpinballSettings.set("Player", "BallTrail", "0" if balltrail == "0" else "1")
    vpinballSettings.set("Player", "BallTrailStrength", balltrail)

    # Visual Nugde Strength
    vpinballSettings.set("Player", "NudgeStrength", system.config.get("vpinball_nudgestrength", ""))

    # Performance settings
    vpinballSettings.set("Player", "MaxFramerate", system.config.get("vpinball_maxframerate", ""))

    # vsync
    vpinballSettings.set("Player", "SyncMode", system.config.get("vpinball_vsync", "2"))

    # avoid default keys like q while it differs depending on the keyboard mapping (making hotkeys fail)
    # 62 = F4 : https://github.com/vpinball/vpinball/tree/standalone/standalone#keyboard
    vpinballSettings.set("Player", "ExitGameKey", "62")

    # presets
    if (presets := system.config.get("vpinball_presets")) != "manual":
        match presets:
            case "highend":
                fxaa = "3"
                sharpen = "2"
                disable_ao = "0"
                dynamic_ao = "1"
                ssrefl = "1"
                pfreflection = "5"
                force_filtering = "1"
                alpha_accuracy = "10"
            case "lowend":
                fxaa = "0"
                sharpen = "0"
                disable_ao = "1"
                dynamic_ao = "0"
                ssrefl = "0"
                pfreflection = "3"
                force_filtering = "0"
                alpha_accuracy = "5"
            case _:
                fxaa = ""
                sharpen = ""
                disable_ao = ""
                dynamic_ao = ""
                ssrefl = ""
                pfreflection = ""
                force_filtering = ""
                alpha_accuracy = ""

        vpinballSettings.set("Player", "FXAA", fxaa)
        vpinballSettings.set("Player", "Sharpen", sharpen)
        vpinballSettings.set("Player", "DisableAO", disable_ao)
        vpinballSettings.set("Player", "DynamicAO", dynamic_ao)
        vpinballSettings.set("Player", "SSRefl", ssrefl)
        vpinballSettings.set("Player", "PFReflection", pfreflection)
        vpinballSettings.set("Player", "ForceAnisotropicFiltering", force_filtering)
        vpinballSettings.set("Player", "AlphaRampAccuracy", alpha_accuracy)

    # custom display physical setup
    if system.config.get_bool("vpinball_customphysicalsetup"):
        # Width
        screen_width = system.config.get("vpinball_screenwidth", "")
        # Height
        screen_height = system.config.get("vpinball_screenheight", "")
        # Inclination
        inclination = system.config.get("vpinball_screeninclination", "")
        # Y
        screen_y = system.config.get("vpinball_screenplayery", "")
        # Z
        screen_z = system.config.get("vpinball_screenplayerz", "")
    else:
        screen_width = ""
        screen_height = ""
        inclination = ""
        screen_y = ""
        screen_z = ""

    vpinballSettings.set("Player", "ScreenWidth",       screen_width)
    vpinballSettings.set("Player", "ScreenHeight",      screen_height)
    vpinballSettings.set("Player", "ScreenInclination", inclination)
    vpinballSettings.set("Player", "ScreenPlayerY",     screen_y)
    vpinballSettings.set("Player", "ScreenPlayerZ",     screen_z)

    # Altcolor (switchon)
    vpinballSettings.set("Standalone", "AltColor", system.config.get_bool("vpinball_altcolor", True, return_values=("1", "0")))

    # Sound balance
    vpinballSettings.set("Player", "MusicVolume", system.config.get("vpinball_musicvolume", ""))
    vpinballSettings.set("Player", "SoundVolume", system.config.get("vpinball_soundvolume", ""))

    # Altsound
    vpinballSettings.set("Standalone", "AltSound", system.config.get_bool("vpinball_altsound", True, return_values=("1", "0")))

    # select which ID for sounddevices by running:
    # /usr/bin/vpinball/VPinballX_GL -listsnd
    vpinballSettings.set("Player", "SoundDevice", system.config.get("vpinball_sounddevice", ""))
    vpinballSettings.set("Player", "SoundDeviceBG", system.config.get("vpinball_sounddevicebg", ""))

    # Don't use SDL "Add credit" with the South button/plunger and pad2key default mapping
    vpinballSettings.set("Player", "JoyAddCreditKey", system.config.get_bool("vpinball_pad_add_credit", return_values=("", "0")))
