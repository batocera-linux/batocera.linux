#!/usr/bin/env python

import utils.videoMode as videoMode

def configureWindowing(vpinballSettings, system, gameResolution, hasDmd):
    screens = videoMode.getScreensInfos(system.config)

    # disable full screen to move the window if necessary
    vpinballSettings.set("Player", "FullScreen", "0")

    # disable any kind of automatic vpx rotation
    vpinballSettings.set("TableOverride", "ViewCabMode",     "2")
    vpinballSettings.set("TableOverride", "ViewCabRotation", "0")

    # Reasonable constants / default values
    Rscreen=16/9

    # which windows to display, and where ?
    flexdmd_config  = getFlexDmdConfiguration(system, screens, hasDmd)
    pinmame_config  = getPinmameConfiguration(system, screens)
    b2s_config      = getB2sConfiguration(system, screens)
    b2sdmd_config   = getB2sdmdConfiguration(system, screens, hasDmd)
    b2sgrill_config = getB2sgrillConfiguration(system, screens)

    # determine playField and backglass screens numbers
    reverse_playfield_and_b2s = False
    if system.isOptSet("vpinball_inverseplayfieldandb2s"):
        if system.getOptBoolean("vpinball_inverseplayfieldandb2s"):
            reverse_playfield_and_b2s = True
    else:
        # auto : if the screen 2 is vertical while the first screen is not, inverse
        if len(screens) >= 2 and screens[0]["width"] > screens[0]["height"] and screens[1]["width"] < screens[1]["height"]:
            reverse_playfield_and_b2s = True

    playFieldScreen = 0
    backglassScreen = 1
    if reverse_playfield_and_b2s and len(screens) > 1:
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

    # PinMame
    if pinmame_config != "manual":
        configurePinmame(vpinballSettings, pinmame_config, b2s_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize)

    # FlexDMD
    if flexdmd_config != "manual":
        configureFlexdmd(vpinballSettings, flexdmd_config, b2s_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize)

    # B2S and B2SDMD
    if b2s_config != "manual":
        configureB2s(vpinballSettings, flexdmd_config, pinmame_config, b2s_config, b2sdmd_config, b2sgrill_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize)

def getFlexDmdConfiguration(system, screens, hasDmd):
    val = ""
    if system.isOptSet("vpinball_flexdmd"):
        val = system.config["vpinball_flexdmd"]
    else:
        if hasDmd:
            val = "disabled"
    if val == "":
        if len(screens) > 2:
            val = "screen3"
        else:
            val = "disabled"
    if len(screens) <= 1 and val == "screen2":
        val = "disabled"
    if len(screens) <= 2 and val == "screen3":
        val = "disabled"
    return val

def getPinmameConfiguration(system, screens):
    # pinmame : same as flexdmd (and both should never be displayed at the same time)
    val = ""
    if system.isOptSet("vpinball_pinmame"):
        val = system.config["vpinball_pinmame"]
    if val == "":
        if len(screens) > 2:
            val = "screen3"
        else:
            val = "disabled"
    if len(screens) <= 1 and val == "screen2":
        val = "disabled"
    if len(screens) <= 2 and val == "screen3":
        val = "disabled"
    return val

def getB2sConfiguration(system, screens):
    val = ""
    if system.isOptSet("vpinball_b2s"):
        val = system.config["vpinball_b2s"]
    if val == "":
        if len(screens) > 1:
            val = "screen2"
        else:
            val = "disabled"
    if len(screens) <= 1 and val == "screen2":
        val = "disabled"
    return val

def getB2sdmdConfiguration(system, screens, hasDmd):
    if system.isOptSet("vpinball_b2sdmd") and system.getOptBoolean("vpinball_b2sdmd") == False: # switchon
        return False
    if hasDmd:
        return False
    return True

def getB2sgrillConfiguration(system, screens):
    if system.isOptSet("vpinball_b2sgrill") and system.getOptBoolean("vpinball_b2sgrill") == False: # switchon
        return False
    return True

def configurePlayfield(vpinballSettings, screens, playFieldScreen):
    vpinballSettings.set("Player", "WindowPosX", str(screens[playFieldScreen]["x"]))
    vpinballSettings.set("Player", "WindowPosY", str(screens[playFieldScreen]["y"]))
    vpinballSettings.set("Player", "Width",      str(screens[playFieldScreen]["width"]))
    vpinballSettings.set("Player", "Height",     str(screens[playFieldScreen]["height"]))

def configurePinmame(vpinballSettings, pinmame_config, b2s_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize):
    WindowName = "PinMAMEWindow"
    Rwindow    = 4/1   #Usual Ratio for this window
    small,medium,large=20,25,30
    x,y,width=0,0,medium

    if pinmame_config == "disabled":
        vpinballSettings.set("Standalone", WindowName, "0")
        return

    vpinballSettings.set("Standalone", WindowName, "1")

    if pinmame_config == "screen2":
        if b2s_config == "screen2": # share with b2s screen
            vpinballSettings.set("Standalone", WindowName+"X",      str(screens[backglassScreen]["x"]+(screens[backglassScreen]["width"]-dmdsize[0])//2))
            vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[backglassScreen]["y"]))
            vpinballSettings.set("Standalone", WindowName+"Width",  str(dmdsize[0]))
            vpinballSettings.set("Standalone", WindowName+"Height", str(dmdsize[1]))
        else:
            width  = screens[backglassScreen]["width"]
            height = (screens[backglassScreen]["width"] // dmdsize[0] * dmdsize[1])
            y = (screens[backglassScreen]["height"]-height)//2
            vpinballSettings.set("Standalone", WindowName,"1")
            vpinballSettings.set("Standalone", WindowName+"X",      str(screens[backglassScreen]["x"]))
            vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[backglassScreen]["y"]+y))
            vpinballSettings.set("Standalone", WindowName+"Width",  str(width))
            vpinballSettings.set("Standalone", WindowName+"Height", str(height))
    elif pinmame_config == "screen3":
        vpinballSettings.set("Standalone", WindowName+"X",      str(screens[2]["x"]))
        vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[2]["y"]))
        vpinballSettings.set("Standalone", WindowName+"Width",  str(screens[2]["width"]))
        vpinballSettings.set("Standalone", WindowName+"Height", str(screens[2]["height"]))
    else:
        if pinmame_config == "topright_small":
            width = small
            x     = 100-width
        if pinmame_config == "topright_medium":
            width = medium
            x     = 100-width
        if pinmame_config == "topright_large":
            width = large
            x     = 100-width
        if pinmame_config == "topleft_small":
            width = small
            x     = 0
        if pinmame_config == "topleft_medium":
            width = medium
            x     = 0
        if pinmame_config == "topleft_large":
            width = large
            x     = 0

        # apply settings
        height = RelativeHeightCalculate(Rscreen, Rwindow, width)
        vpinballSettings.set("Standalone", WindowName+"X",      ConvertToPixel(gameResolution["width"],  x))
        vpinballSettings.set("Standalone", WindowName+"Y",      ConvertToPixel(gameResolution["height"], y))
        vpinballSettings.set("Standalone", WindowName+"Width",  ConvertToPixel(gameResolution["width"],  width))
        vpinballSettings.set("Standalone", WindowName+"Height", ConvertToPixel(gameResolution["height"], height))

def getDMDWindowSize(system, gameResolution):
    if not system.isOptSet("vpinball_dmdsize"):
        return [1024, 256] # like 128x32
    if system.config["vpinball_dmdsize"] == "128x16":
        return [1024, 128]
    if system.config["vpinball_dmdsize"] == "192x64":
        return [1024, 341]
    if system.config["vpinball_dmdsize"] == "256x64":
        return [1024, 128]
    return [1024, 256] # like 128x32

def configureFlexdmd(vpinballSettings, flexdmd_config, b2s_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize):
    WindowName = "FlexDMDWindow"
    Rwindow    = 4/1  # Usual Ratio for this window
    small,medium,large=20,25,30
    x,y,width=0,0,medium

    if flexdmd_config=="disabled":
        vpinballSettings.set("Standalone", WindowName,"0")
        return

    vpinballSettings.set("Standalone", WindowName,"1")

    if flexdmd_config == "screen2":
        if b2s_config == "screen2": # share with b2s screen
            vpinballSettings.set("Standalone", WindowName,"1")
            vpinballSettings.set("Standalone", WindowName+"X",      str(screens[backglassScreen]["x"]+(screens[backglassScreen]["width"]-dmdsize[0])//2))
            vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[backglassScreen]["y"]))
            vpinballSettings.set("Standalone", WindowName+"Width",  str(dmdsize[0]))
            vpinballSettings.set("Standalone", WindowName+"Height", str(dmdsize[1]))
        else:
            width  = screens[backglassScreen]["width"]
            height = (screens[backglassScreen]["width"] // dmdsize[1] * dmdsize[0])
            y = (screens[backglassScreen]["height"]-height)//2
            vpinballSettings.set("Standalone", WindowName,"1")
            vpinballSettings.set("Standalone", WindowName+"X",      str(screens[backglassScreen]["x"]))
            vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[backglassScreen]["y"]+y))
            vpinballSettings.set("Standalone", WindowName+"Width",  str(width))
            vpinballSettings.set("Standalone", WindowName+"Height", str(height))
    elif flexdmd_config=="screen3":
        vpinballSettings.set("Standalone", WindowName+"X",      str(screens[2]["x"]))
        vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[2]["y"]))
        vpinballSettings.set("Standalone", WindowName+"Width",  str(screens[2]["width"]))
        vpinballSettings.set("Standalone", WindowName+"Height", str(screens[2]["height"]))
    else:
        if flexdmd_config == "topright_small":
            width = small
            x     = 100-width
        if flexdmd_config == "topright_medium":
            width = medium
            x     = 100-width
        if flexdmd_config == "topright_large":
            width = large
            x     = 100-width
        if flexdmd_config == "topleft_small":
            width = small
            x     = 0
        if flexdmd_config == "topleft_medium":
            width = medium
            x     = 0
        if flexdmd_config == "topleft_large":
            width = large
            x     = 0
        # apply settings
        height = RelativeHeightCalculate(Rscreen, Rwindow, width)
        vpinballSettings.set("Standalone", WindowName+"X",      ConvertToPixel(gameResolution["width"],  x))
        vpinballSettings.set("Standalone", WindowName+"Y",      ConvertToPixel(gameResolution["height"], y))
        vpinballSettings.set("Standalone", WindowName+"Width",  ConvertToPixel(gameResolution["width"],  width))
        vpinballSettings.set("Standalone", WindowName+"Height", ConvertToPixel(gameResolution["height"], height))

def configureB2s(vpinballSettings, flexdmd_config, pinmame_config, b2s_config, b2sdmd_config, b2sgrill_config, screens, backglassScreen, Rscreen, gameResolution, dmdsize):
    WindowName = "B2SBackglass"
    Rwindow    = 4/3 # Usual Ratio for this window
    small,medium,large=20,25,30
    x,y,width=0,0,medium

    if b2s_config=="disabled":
        vpinballSettings.set("Standalone", WindowName,     "0")
        vpinballSettings.set("Standalone", "B2SWindows",   "0")
        vpinballSettings.set("Standalone", "B2SHideGrill", "1")
        return

    vpinballSettings.set("Standalone", WindowName,     "1")
    vpinballSettings.set("Standalone", "B2SWindows",   "1")
    vpinballSettings.set("Standalone", "B2SHideGrill", "0")

    if b2s_config == "screen2":
        if flexdmd_config == "screen2" or pinmame_config == "screen2": # share with dmd screen
            vpinballSettings.set("Standalone", WindowName+"X",      str(screens[backglassScreen]["x"]))
            vpinballSettings.set("Standalone", WindowName+"Y",      str(dmdsize[1]))
            vpinballSettings.set("Standalone", WindowName+"Width",  str(screens[backglassScreen]["width"]))
            vpinballSettings.set("Standalone", WindowName+"Height", str(screens[backglassScreen]["height"]-dmdsize[1]))
        else:
            vpinballSettings.set("Standalone", WindowName+"X",      str(screens[backglassScreen]["x"]))
            vpinballSettings.set("Standalone", WindowName+"Y",      str(screens[backglassScreen]["y"]))
            vpinballSettings.set("Standalone", WindowName+"Width",  str(screens[backglassScreen]["width"]))
            vpinballSettings.set("Standalone", WindowName+"Height", str(screens[backglassScreen]["height"]))
    else:
        if b2s_config == "topright_small":
            width = small
            x     = 100-width
        if b2s_config == "topright_medium":
            width = medium
            x     = 100-width
        if b2s_config == "topright_large":
            width = large
            x     = 100-width
        if b2s_config == "topleft_small":
            width = small
            x     = 0
        if b2s_config == "topleft_medium":
            width = medium
            x     = 0
        if b2s_config == "topleft_large":
            width = large
            x     = 0
        # apply settings
        height = RelativeHeightCalculate(Rscreen, Rwindow, width)
        vpinballSettings.set("Standalone",WindowName+"X",      ConvertToPixel(gameResolution["width"],  x))
        vpinballSettings.set("Standalone",WindowName+"Y",      ConvertToPixel(gameResolution["height"], y))
        vpinballSettings.set("Standalone",WindowName+"Width",  ConvertToPixel(gameResolution["width"],  width))
        vpinballSettings.set("Standalone",WindowName+"Height", ConvertToPixel(gameResolution["height"], height))

        # B2SDMD
        WindowName = "B2SDMD"
        y          = height
        Rwindow    = 3   #Usual Ratio for this window
        height     = RelativeHeightCalculate(Rscreen, Rwindow, width)
        vpinballSettings.set("Standalone",WindowName+"X",      ConvertToPixel(gameResolution["width"],  x))
        vpinballSettings.set("Standalone",WindowName+"Y",      ConvertToPixel(gameResolution["height"], y))
        vpinballSettings.set("Standalone",WindowName+"Width",  ConvertToPixel(gameResolution["width"],  width))
        vpinballSettings.set("Standalone",WindowName+"Height", ConvertToPixel(gameResolution["height"], height))

    # B2S DMD: not displayed if B2S is hidden
    if b2sdmd_config:
        vpinballSettings.set("Standalone", "B2SHideB2SDMD", "0")
    else:
        vpinballSettings.set("Standalone", "B2SHideB2SDMD", "1")

    if b2sgrill_config:
        vpinballSettings.set("Standalone", "B2SHideGrill", "0")
    else:
        vpinballSettings.set("Standalone", "B2SHideGrill", "1")

# Extra_windows (pinmamedmd, flexdmd, b2s,b2sdmd)
# VideogetCurrentResolution to convert from percentage to pixel value
# necessary trick because people can plug their 1080p laptop on a 4k TV
# (and because VPinballX.ini uses absolute pixel coordinates)
def ConvertToPixel(total_size, percentage):
    pixel_value = str(int(int(total_size)*float(percentage)*1e-2))
    return pixel_value

# Calculates the relative height, depending on the screen ratio
# (normaly 16/9), the element ratio (4/3 for the b2s) and the relative width
def RelativeHeightCalculate(Rscreen, Relement, RelativeWidth):
    return int(Rscreen*RelativeWidth/Relement)
