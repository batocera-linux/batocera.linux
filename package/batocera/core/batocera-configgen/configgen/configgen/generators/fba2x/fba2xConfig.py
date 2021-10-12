#!/usr/bin/env python

# return true if the option is considered defined
def defined(key, dict):
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0

def updateFBAConfig(iniConfig, system):
    ratioIndexes = {'4/3': '0', '16/9': '1'}

    if not iniConfig.has_section("Graphics"):
        iniConfig.add_section("Graphics")

    if system.isOptSet("smooth") and system.getOptBoolean("smooth") == True:
        iniConfig.set("Graphics", "DisplaySmoothStretch", "1")
    else:
        iniConfig.set("Graphics", "DisplaySmoothStretch", "0")

    if defined("ratio", system.config) and system.config["ratio"] in ratioIndexes:
        iniConfig.set("Graphics", "MaintainAspectRatio", ratioIndexes[system.config["ratio"]])
    else:
        iniConfig.set("Graphics", "MaintainAspectRatio", "0")

    if defined("shaders", system.config) and system.config["shaders"] == 'scanlines':
        iniConfig.set("Graphics", "DisplayEffect", "1")
    else :
        iniConfig.set("Graphics", "DisplayEffect", "0")

    iniConfig.set("Graphics", "RotateScreen",  "0")
    iniConfig.set("Graphics", "DisplayBorder", "0")
