from __future__ import annotations

from typing import TYPE_CHECKING

from ...utils import videoMode

if TYPE_CHECKING:
    from batocera_common.configparser import CaseSensitiveConfigParser

    from ...Emulator import Emulator
    from ...types import Resolution, ScreenInfo

def configureWindowing(vpinballSettings: CaseSensitiveConfigParser, system: Emulator, gameResolution: Resolution, hasDmd: bool) -> None:
    screens = videoMode.getScreensInfos(system.config)

    # init sections
    for section in ["Player", "TableOverride", "Backglass"]:
        if not vpinballSettings.has_section(section):
            vpinballSettings.add_section(section)

    # disable full screen to move the window if necessary (and bcc won't full screen windows)
    vpinballSettings.set("Player", "PlayfieldFullScreen", "0")

    # disable any kind of automatic vpx rotation
    vpinballSettings.set("TableOverride", "ViewCabMode",     "2")

    # Reasonable constants / default values
    Rscreen=16/9

    # which windows to display, and where ?
    backglass_config = getBackglassConfiguration(system, screens)

    # determine playField and backglass screens numbers
    reverse_playfield_and_backglass = False
    if system.isOptSet("vpinball_inverseplayfieldandbackglass"):
        if system.getOptBoolean("vpinball_inverseplayfieldandbackglass"):
            reverse_playfield_and_backglass = True
    else:
        # auto : if the screen 2 is vertical while the first screen is not, inverse
        if len(screens) >= 2 and screens[0]["width"] > screens[0]["height"] and screens[1]["width"] < screens[1]["height"]:
            reverse_playfield_and_backglass = True

    playFieldScreen = 0
    backglassScreen = 1
    if reverse_playfield_and_backglass and len(screens) > 1:
        playFieldScreen = 1
        backglassScreen = 0

    dmdsize = getDMDWindowSize(system, gameResolution)

    # Playfield
    if not (system.isOptSet("vpinball_playfield") and system.config["vpinball_playfield"] == "manual"):
        configurePlayfield(vpinballSettings, screens, playFieldScreen)

    # playfiled mode
    if system.isOptSet("vpinball_playfieldmode"):
        vpinballSettings.set("Player", "BGSet", system.config["vpinball_playfieldmode"])
    else:
        if screens[playFieldScreen]["width"] < screens[playFieldScreen]["height"]:
            vpinballSettings.set("Player", "BGSet", "1") # pincab / cabinet
        else:
            vpinballSettings.set("Player", "BGSet", "0") # desktop mode

    # backglass
    if backglass_config != "manual":
        configureBackglass(vpinballSettings, backglass_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize)

def getBackglassConfiguration(system: Emulator, screens: list[ScreenInfo]):
    val = ""
    if system.isOptSet("vpinball_backglass"):
        val = system.config["vpinball_backglass"]
    if val == "":
        if len(screens) > 1:
            val = "screen2"
        else:
            val = "disabled"
    if len(screens) <= 1 and val == "screen2":
        val = "disabled"
    return val

def configurePlayfield(vpinballSettings: CaseSensitiveConfigParser, screens: list[ScreenInfo], playFieldScreen: int):
    vpinballSettings.set("Player", "PlayfieldDisplay", "absolute")
    vpinballSettings.set("Player", "PlayfieldWndX",    str(screens[playFieldScreen]["x"]))
    vpinballSettings.set("Player", "PlayfieldWndY",    str(screens[playFieldScreen]["y"]))
    vpinballSettings.set("Player", "PlayfieldWidth",   str(screens[playFieldScreen]["width"]))
    vpinballSettings.set("Player", "PlayfieldHeight",  str(screens[playFieldScreen]["height"]))

def getDMDWindowSize(system: Emulator, gameResolution: Resolution):
    if not system.isOptSet("vpinball_dmdsize"):
        return [1024, 256] # like 128x32
    if system.config["vpinball_dmdsize"] == "128x16":
        return [1024, 128]
    if system.config["vpinball_dmdsize"] == "192x64":
        return [1024, 341]
    if system.config["vpinball_dmdsize"] == "256x64":
        return [1024, 128]
    return [1024, 256] # like 128x32

def configureBackglass(vpinballSettings: CaseSensitiveConfigParser, backglass_config: str, screens: list[ScreenInfo], backglassScreen: int, Rscreen: float, gameResolution: Resolution, dmdsize: list[int]):
    Rwindow    = 4/3 # Usual Ratio for this window
    small,medium,large=20,25,30
    x,y,width=0,0,medium

    if backglass_config=="disabled":
        vpinballSettings.set("Backglass", "BackglassOutput", "0")
        return

    vpinballSettings.set("Backglass", "BackglassOutput", "1")
    # disable full screen to move the window if necessary (and bcc wants no fullscreen)
    vpinballSettings.set("Backglass", "BackglassFullScreen", "0")

    vpinballSettings.set("Backglass", "BackglassDisplay", "absolute")
    if backglass_config == "screen2":
        vpinballSettings.set("Backglass", "BackglassWndX",   str(screens[backglassScreen]["x"]))
        vpinballSettings.set("Backglass", "BackglassWndY",   str(screens[backglassScreen]["y"]))
        vpinballSettings.set("Backglass", "BackglassWidth",  str(screens[backglassScreen]["width"]))
        vpinballSettings.set("Backglass", "BackglassHeight", str(screens[backglassScreen]["height"]))
    else:
        if backglass_config == "topright_small":
            width = small
            x     = 100-width
        if backglass_config == "topright_medium":
            width = medium
            x     = 100-width
        if backglass_config == "topright_large":
            width = large
            x     = 100-width
        if backglass_config == "topleft_small":
            width = small
            x     = 0
        if backglass_config == "topleft_medium":
            width = medium
            x     = 0
        if backglass_config == "topleft_large":
            width = large
            x     = 0
        # apply settings
        height = RelativeHeightCalculate(Rscreen, Rwindow, width)
        vpinballSettings.set("Backglass", "BackglassWndX",    ConvertToPixel(gameResolution["width"],  x))
        vpinballSettings.set("Backglass", "BackglassWndY",    ConvertToPixel(gameResolution["height"], y))
        vpinballSettings.set("Backglass", "BackglassWidth",   ConvertToPixel(gameResolution["width"],  width))
        vpinballSettings.set("Backglass", "BackglassHeight",  ConvertToPixel(gameResolution["height"], height))

# Extra_windows (backglass)
# VideogetCurrentResolution to convert from percentage to pixel value
# necessary trick because people can plug their 1080p laptop on a 4k TV
# (and because VPinballX.ini uses absolute pixel coordinates)
def ConvertToPixel(total_size: int, percentage: float):
    return str(int(int(total_size)*float(percentage)*1e-2))

# Calculates the relative height, depending on the screen ratio
# (normaly 16/9), the element ratio (4/3 for the backglass) and the relative width
def RelativeHeightCalculate(Rscreen: float, Relement: float, RelativeWidth: float):
    return int(Rscreen*RelativeWidth/Relement)
