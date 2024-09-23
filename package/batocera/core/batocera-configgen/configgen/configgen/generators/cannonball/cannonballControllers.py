# -*- coding: utf-8 -*-

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
    from .cannonballGenerator import CannonballGenerator
    xml_controls = CannonballGenerator.getSection(config, xml_root, "controls")

    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer == 1:
            CannonballGenerator.setSectionConfig(config, xml_controls, "pad_id", str(pad.index))
            xml_padconfig = CannonballGenerator.getSection(config, xml_controls, "padconfig")

            for x in pad.inputs:
                input = pad.inputs[x]
                if input.type == "button":
                    if input.name in cannonballJoystick:
                        CannonballGenerator.setSectionConfig(config, xml_padconfig, cannonballJoystick[input.name], input.id)
        nplayer += 1
