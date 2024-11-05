from __future__ import annotations

from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
    from ...controller import ControllerMapping

cannonballJoystick = {
    "b": "acc",
    "a": "brake",
    "pageup": "gear1",
    "pagedown": "gear2",
    "start": "start",
    "select": "coin",
    "hotkey": "menu",
    "x": "view",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "r2": "accel",
    "l2": "brake"
}

# Create the controller configuration file
def generateControllerConfig(xml_controls: Element, playersControllers: ControllerMapping):
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        if nplayer == 1:
            # Set up controller-specific configurations
            ET.SubElement(xml_controls, "gear").text = "3"  # auto
            ET.SubElement(xml_controls, "rumble").text = "1"
            ET.SubElement(xml_controls, "steerspeed").text = "3"
            ET.SubElement(xml_controls, "pedalspeed").text = "4"
            padconfig = ET.SubElement(xml_controls, 'padconfig')

            # Iterate through cannonballJoystick to maintain the specified order
            for control_name, cannonball_mapping in cannonballJoystick.items():
                # Check if this control is in pad.inputs to maintain cannonballJoystick order
                if control_name in pad.inputs:
                    input = pad.inputs[control_name]
                    if input.type == "button":
                        button_element = ET.SubElement(padconfig, cannonball_mapping)
                        button_element.text = input.id
                    elif input.type == "hat":
                        hat_element = ET.SubElement(padconfig, cannonball_mapping)
                        hat_element.text = input.value

            # Enable analog and configure axis settings
            analog = ET.SubElement(xml_controls, "analog", attrib={"enabled": "1"})
            axisconfig = ET.SubElement(analog, 'axis')
            ET.SubElement(axisconfig, "wheel").text = "0"

            # Add axis controls in the specified order
            for control_name, cannonball_mapping in cannonballJoystick.items():
                if control_name in pad.inputs:
                    input = pad.inputs[control_name]
                    if input.type == "axis":
                        axis_element = ET.SubElement(axisconfig, cannonball_mapping)
                        axis_element.text = input.code

            break  # Exit after configuring the first player
        nplayer += 1
