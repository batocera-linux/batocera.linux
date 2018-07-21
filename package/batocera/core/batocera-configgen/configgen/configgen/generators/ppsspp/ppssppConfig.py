#!/usr/bin/env python
import sys
import os
import recalboxFiles
import settings
from settings.unixSettings import UnixSettings

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

ppssppSettings = UnixSettings(recalboxFiles.ppssppConfig, separator=' ')

# return true if the option is considered enabled (for boolean options)
def enabled(key, dict):
    return key in dict and (dict[key] == '1' or dict[key] == 'true')


# return true if the option is considered defined
def defined(key, dict):
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0
    

def writePPSSPPConfig(system):
    writePPSSPPConfigToFile(createPPSSPPConfig(system))

def createPPSSPPConfig(system):
    ppssppConfig = dict()
    recalboxConfig = system.config
    # Display FPS
    if enabled('showFPS', recalboxConfig):
        ppssppConfig['ShowFPSCounter'] = '3' # 1 for Speed%, 2 for FPS, 3 for both
    else:
        ppssppConfig['ShowFPSCounter'] = '0'

    return ppssppConfig


def writePPSSPPConfigToFile(config):
    for setting in config:
        ppssppSettings.save(setting, config[setting])
