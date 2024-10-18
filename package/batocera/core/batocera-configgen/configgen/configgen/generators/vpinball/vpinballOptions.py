from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...utils.configparser import CaseSensitiveConfigParser


def configureOptions(vpinballSettings: CaseSensitiveConfigParser, system: Emulator) -> None:
    # Tables are organised by folders containing the vpx file, and sub-folders with the roms, altcolor, altsound,...
    # We keep a switch to allow users with the old unique pinmame to be able to continue using vpinball (switchon)
    if system.isOptSet("vpinball_folders") and system.getOptBoolean("vpinball_folders") == False:
        vpinballSettings.set("Standalone", "PinMAMEPath", "")
    else:
        vpinballSettings.set("Standalone", "PinMAMEPath", "./")

    # Ball trail
    if system.isOptSet("vpinball_balltrail"):
        vpinballSettings.set("Player", "BallTrail", "1")
        vpinballSettings.set("Player", "BallTrailStrength", system.config["vpinball_balltrail"])
    else:
        vpinballSettings.set("Player", "BallTrail", "0")
        vpinballSettings.set("Player", "BallTrailStrength", "0")

    # Visual Nugde Strength
    if system.isOptSet("vpinball_nudgestrength"):
        vpinballSettings.set("Player", "NudgeStrength", system.config["vpinball_nudgestrength"])
    else:
        vpinballSettings.set("Player", "NudgeStrength", "")

    # Performance settings
    if system.isOptSet("vpinball_maxframerate"):
        vpinballSettings.set("Player", "MaxFramerate", system.config["vpinball_maxframerate"])
    else:
        vpinballSettings.set("Player", "MaxFramerate", "")

    # vsync
    if system.isOptSet("vpinball_vsync"):
        vpinballSettings.set("Player", "SyncMode", system.config["vpinball_vsync"])
    else:
        vpinballSettings.set("Player", "SyncMode", "2")

    # presets
    if system.isOptSet("vpinball_presets"):
        if system.config["vpinball_presets"]=="defaults":
            vpinballSettings.set("Player", "FXAA", "")
            vpinballSettings.set("Player", "Sharpen", "")
            vpinballSettings.set("Player", "DisableAO", "")
            vpinballSettings.set("Player", "DynamicAO", "")
            vpinballSettings.set("Player", "SSRefl", "")
            vpinballSettings.set("Player", "PFReflection", "")
            vpinballSettings.set("Player", "ForceAnisotropicFiltering", "")
            vpinballSettings.set("Player", "AlphaRampAccuracy", "")
        elif system.config["vpinball_presets"]=="highend":
            vpinballSettings.set("Player", "FXAA", "3")
            vpinballSettings.set("Player", "Sharpen", "2")
            vpinballSettings.set("Player", "DisableAO", "0")
            vpinballSettings.set("Player", "DynamicAO", "1")
            vpinballSettings.set("Player", "SSRefl", "1")
            vpinballSettings.set("Player", "PFReflection", "5")
            vpinballSettings.set("Player", "ForceAnisotropicFiltering", "1")
            vpinballSettings.set("Player", "AlphaRampAccuracy", "10")
        elif system.config["vpinball_presets"]=="lowend":
            vpinballSettings.set("Player", "FXAA", "0")
            vpinballSettings.set("Player", "Sharpen", "0")
            vpinballSettings.set("Player", "DisableAO", "1")
            vpinballSettings.set("Player", "DynamicAO", "0")
            vpinballSettings.set("Player", "SSRefl", "0")
            vpinballSettings.set("Player", "PFReflection", "3")
            vpinballSettings.set("Player", "ForceAnisotropicFiltering", "0")
            vpinballSettings.set("Player", "AlphaRampAccuracy", "5")
        elif system.config["vpinball_presets"]=="manual":
            pass
    else: # like defaults
        vpinballSettings.set("Player", "FXAA", "")
        vpinballSettings.set("Player", "Sharpen", "")
        vpinballSettings.set("Player", "DisableAO", "")
        vpinballSettings.set("Player", "DynamicAO", "")
        vpinballSettings.set("Player", "SSRefl", "")
        vpinballSettings.set("Player", "PFReflection", "")
        vpinballSettings.set("Player", "ForceAnisotropicFiltering", "")
        vpinballSettings.set("Player", "AlphaRampAccuracy", "")

    # custom display physical setup
    if system.isOptSet("vpinball_customphysicalsetup") and system.getOptBoolean("vpinball_customphysicalsetup"):
        # Width
        if system.isOptSet("vpinball_screenwidth"):
            vpinballSettings.set("Player", "ScreenWidth", system.config["vpinball_screenwidth"])
        else:
            vpinballSettings.set("Player", "ScreenWidth", "")
        # Height
        if system.isOptSet("vpinball_screenheight"):
            vpinballSettings.set("Player", "ScreenHeight", system.config["vpinball_screenheight"])
        else:
            vpinballSettings.set("Player", "ScreenHeight", "")
        # Inclination
        if system.isOptSet("vpinball_screeninclination"):
            vpinballSettings.set("Player", "ScreenInclination", system.config["vpinball_screeninclination"])
        else:
            vpinballSettings.set("Player", "ScreenInclination", "")
        # Y
        if system.isOptSet("vpinball_screenplayery"):
            vpinballSettings.set("Player", "ScreenPlayerY", system.config["vpinball_screenplayery"])
        else:
            vpinballSettings.set("Player", "ScreenPlayerY", "")
        # Z
        if system.isOptSet("vpinball_screenplayerz"):
            vpinballSettings.set("Player", "ScreenPlayerZ", system.config["vpinball_screenplayerz"])
        else:
            vpinballSettings.set("Player", "ScreenPlayerZ", "")
    else:
        vpinballSettings.set("Player", "ScreenWidth",       "")
        vpinballSettings.set("Player", "ScreenHeight",      "")
        vpinballSettings.set("Player", "ScreenInclination", "")
        vpinballSettings.set("Player", "ScreenPlayerY",     "")
        vpinballSettings.set("Player", "ScreenPlayerZ",     "")

    # Altcolor (switchon)
    if system.isOptSet("vpinball_altcolor") and system.getOptBoolean("vpinball_altcolor") == False:
        vpinballSettings.set("Standalone", "AltColor", "0")
    else:
        vpinballSettings.set("Standalone", "AltColor","1")

    # Sound balance
    if system.isOptSet("vpinball_musicvolume"):
        vpinballSettings.set("Player", "MusicVolume", system.config["vpinball_musicvolume"])
    else:
        vpinballSettings.set("Player", "MusicVolume", "")

    if system.isOptSet("vpinball_soundvolume"):
        vpinballSettings.set("Player", "SoundVolume", system.config["vpinball_soundvolume"])
    else:
        vpinballSettings.set("Player", "SoundVolume", "")

    # Altsound
    if system.isOptSet("vpinball_altsound") and system.getOptBoolean("vpinball_altsound") == False:
        vpinballSettings.set("Standalone", "AltSound", "0")
    else:
        vpinballSettings.set("Standalone", "AltSound","1")

    # select which ID for sounddevices by running:
    # /usr/bin/vpinball/VPinballX_GL -listsnd
    if system.isOptSet("vpinball_sounddevice"):
        vpinballSettings.set("Player", "SoundDevice", system.config["vpinball_sounddevice"])
    else:
        vpinballSettings.set("Player", "SoundDevice", "")
    if system.isOptSet("vpinball_sounddevicebg"):
        vpinballSettings.set("Player", "SoundDeviceBG", system.config["vpinball_sounddevicebg"])
    else:
        vpinballSettings.set("Player", "SoundDeviceBG", "")

    # Don't use SDL "Add credit" with the South button/plunger and pad2key default mapping
    if system.isOptSet("vpinball_pad_add_credit") and system.getOptBoolean("vpinball_pad_add_credit") == True:
        vpinballSettings.set("Player", "JoyAddCreditKey", "")
    else:
        vpinballSettings.set("Player", "JoyAddCreditKey", "0")
