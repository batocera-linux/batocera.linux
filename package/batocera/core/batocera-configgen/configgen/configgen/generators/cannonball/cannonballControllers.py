#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cannonballGenerator

cannonballJoystick = {
    "b": "acc",
    "y": "brake",
    "a": "gear1",
    "x": "gear2",
    "start":  "start",
    "select": "coin",
    "l1": "menu",
    "l2": "view",
    "hotkey": "hotkey"
}

# Create the controller configuration file
def generateControllerConfig(config, xml_root, playersControllers):
    xml_controls = cannonballGenerator.CannonballGenerator.getSection(config, xml_root, "controls")
    
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer == 1:
            cannonballGenerator.CannonballGenerator.setSectionConfig(config, xml_controls, "pad_id", str(pad.index))
            xml_padconfig = cannonballGenerator.CannonballGenerator.getSection(config, xml_controls, "padconfig")

            for x in pad.inputs:
                input = pad.inputs[x]
                if input.type == "button":
                    if input.name in cannonballJoystick:
                        cannonballGenerator.CannonballGenerator.setSectionConfig(config, xml_padconfig, cannonballJoystick[input.name], input.id)
        nplayer += 1
