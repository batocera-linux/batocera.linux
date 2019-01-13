#!/usr/bin/env python
import sys
import os
import recalboxFiles
import settings
from Emulator import Emulator
from settings.unixSettings import UnixSettings

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

ppssppSettings = UnixSettings(recalboxFiles.ppssppConfig, separator=' ')

def writePPSSPPConfig(system):
    writePPSSPPConfigDefault()
    writePPSSPPConfigToFile(createPPSSPPConfig(system))

def writePPSSPPConfigDefault():
    if not os.path.exists(recalboxFiles.ppssppConfig):
        # write default values template, so that the rest of the config can set values
        f = open(recalboxFiles.ppssppConfig, "w")
        f.write("[Graphics]\n")
        f.write("FrameSkip = 0\n")
        f.write("ShowFPSCounter = 0\n")
        f.close()

def createPPSSPPConfig(system):
    ppssppConfig = dict()

    # Display FPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
        ppssppConfig['ShowFPSCounter'] = '3' # 1 for Speed%, 2 for FPS, 3 for both
    else:
        ppssppConfig['ShowFPSCounter'] = '0'

    # Performances
    if system.isOptSet('frameskip') and system.getOptBoolean('frameskip') == True:
        ppssppConfig['FrameSkip'] = '1'
    else:
        ppssppConfig['FrameSkip'] = '0'

    return ppssppConfig


def writePPSSPPConfigToFile(config):
    for setting in config:
        ppssppSettings.save(setting, config[setting])
