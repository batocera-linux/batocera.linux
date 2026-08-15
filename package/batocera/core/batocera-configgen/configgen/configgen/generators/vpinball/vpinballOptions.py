from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from batocera_common.configparser import CaseSensitiveConfigParser

    from ...Emulator import Emulator

def configureOptions(vpinballSettings: CaseSensitiveConfigParser, system: Emulator) -> None:
    # init sections
    for section in ["Player", "Plugin.AltSound"]:
        if not vpinballSettings.has_section(section):
            vpinballSettings.add_section(section)

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

    # Sound balance
    vpinballSettings.set("Player", "MusicVolume", system.config.get("vpinball_musicvolume", ""))
    vpinballSettings.set("Player", "SoundVolume", system.config.get("vpinball_soundvolume", ""))

    # select which ID for sounddevices by running:
    # /usr/bin/vpinball/VPinballX_BGFX -listsnd
    vpinballSettings.set("Player", "SoundDevice", system.config.get("vpinball_sounddevice", ""))
    vpinballSettings.set("Player", "SoundDeviceBG", system.config.get("vpinball_sounddevicebg", ""))
