from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Final
from xml.dom import minidom

from ...batoceraPaths import HOME, ensure_parents_and_open, mkdir_if_not_exists

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import ControllerMapping

_KODI_USERDATA: Final = HOME / '.kodi' / 'userdata'


def writeKodiConfigs(kodiJoystick: Path, currentControllers: ControllerMapping, provider: str):
    kodihatspositions    = {1: 'up', 2: 'right', 4: 'down', 8: 'left'}
    kodireversepositions = {'joystick1up': 'joystick1down', 'joystick1left': 'joystick1right', 'joystick2up': 'joystick2down', 'joystick2left': 'joystick2right' }
    kodiaxes             = { 'joystick1up': True, 'joystick1down': True, 'joystick1left': True, 'joystick1right': True,
                             'joystick2up': True, 'joystick2down': True, 'joystick2left': True, 'joystick2right': True }

    kodimapping = {
        # buttons
        "a": "b", "b": "a", "x": "y", "y": "x",
        "hotkey": "guide", "select": "back", "start": "start",
        "pageup": "leftbumper", "l2": "lefttrigger", "pagedown": "rightbumper", "r2": "righttrigger",

        # hats or axis
        "up": "up", "down": "down", "left": "left", "right": "right",

        # axes
        "joystick1up":    { "name": "leftstick",  "sens": "up"    },
        "joystick1down":  { "name": "leftstick",  "sens": "down"  },
        "joystick1left":  { "name": "leftstick",  "sens": "left"  },
        "joystick1right": { "name": "leftstick",  "sens": "right" },
        "joystick2up":    { "name": "rightstick", "sens": "up"    },
        "joystick2down":  { "name": "rightstick", "sens": "down"  },
        "joystick2left":  { "name": "rightstick", "sens": "left"  },
        "joystick2right": { "name": "rightstick", "sens": "right" }
    }

    controllersDone = {}

    for controller in currentControllers:
        cur = currentControllers[controller]

        # skip duplicates
        if cur.real_name in controllersDone:
            continue
        controllersDone[cur.real_name] = True

        # initialized the file
        kodiJoy = kodiJoystick.with_name(kodiJoystick.name.format(cur.guid+"_"+hashlib.md5(cur.real_name.encode('utf-8')).hexdigest())).open("w") # because 2 pads with a different name have sometimes the same vid/pid...
        config = minidom.Document()
        xmlbuttonmap = config.createElement('buttonmap')
        config.appendChild(xmlbuttonmap)

        xmldevice = config.createElement('device')
        xmldevice.attributes["name"] = cur.real_name
        xmldevice.attributes["provider"] = provider

        if provider == "udev":
            xmldevice.attributes["vid"], xmldevice.attributes["pid"] = vidpid(cur.guid)

        xmldevice.attributes["buttoncount"] = str(cur.button_count)
        xmldevice.attributes["axiscount"] = str(2*cur.hat_count + cur.axis_count)
        xmlbuttonmap.appendChild(xmldevice)
        xmlcontroller = config.createElement('controller')
        xmlcontroller.attributes["id"] = "game.controller.default"

        sticksNode = {}

        alreadyset = {}
        for x in cur.inputs:
            input = cur.inputs[x]
            if input.name in kodimapping:
                    if input.type == 'button':
                        if "btn_" + str(int(input.id)) not in alreadyset:
                            xmlbutton = config.createElement('feature')
                            xmlbutton.attributes["name"] = kodimapping[input.name]
                            xmlbutton.attributes["button"] = str(int(input.id))
                            xmlcontroller.appendChild(xmlbutton)
                            alreadyset["btn_" + str(int(input.id))] = True

                    elif input.type == 'hat' and int(input.value) in kodihatspositions:
                        xmlhat = config.createElement('feature')
                        if kodihatspositions[int(input.value)] == "left" or kodihatspositions[int(input.value)] == "right":
                            val = str(cur.axis_count)
                        else:
                            val = str(cur.axis_count+1)
                        if kodihatspositions[int(input.value)] == "down" or kodihatspositions[int(input.value)] == "right":
                            xmlhat.attributes["axis"] = "+" + val
                        else:
                            xmlhat.attributes["axis"] = "-" + val
                        xmlhat.attributes["name"] = kodihatspositions[int(input.value)]
                        xmlcontroller.appendChild(xmlhat)

                    elif input.type == 'axis' and input.name in kodiaxes:
                        if kodimapping[input.name]["name"] not in sticksNode:
                            sticksNode[kodimapping[input.name]["name"]] = config.createElement('feature')
                            sticksNode[kodimapping[input.name]["name"]].attributes["name"] = kodimapping[input.name]["name"]
                        for sens in [input.name, kodireversepositions[input.name]]:
                            xmlsens = config.createElement(kodimapping[sens]["sens"])
                            val = input.id
                            if (int(input.value) >= 0 and sens == input.name) or (int(input.value) < 0 and sens != input.name):
                                val =  "+" + val
                            else:
                                val =  "-" + val
                            xmlsens.attributes["axis"] = val
                            sticksNode[kodimapping[sens]["name"]].appendChild(xmlsens)
                    elif input.type == 'axis' and input.name not in kodiaxes:
                        xmlaxis = config.createElement('feature')
                        val = input.id
                        if int(input.value) >= 0:
                            val =  "+" + val
                        else:
                            val =  "-" + val
                        xmlaxis.attributes["axis"] = val
                        xmlaxis.attributes["name"] = kodimapping[input.name]
                        xmlcontroller.appendChild(xmlaxis)

        for node in sticksNode:
            xmlcontroller.appendChild(sticksNode[node])
        xmldevice.appendChild(xmlcontroller)
        kodiJoy.write(config.toprettyxml())
        kodiJoy.close()

def writeKodiConfig(controllersFromES: ControllerMapping) -> None:
    # if there is no controller, don't remove the current generated one
    # it allows people to start kodi at startup when having only bluetooth joysticks
    # or this allows people to plug the last used joystick
    if len(controllersFromES) == 0:
        return
    #provider = "linux"
    provider = "udev"
    kodiJoystick = _KODI_USERDATA / 'addon_data' / 'peripheral.joystick' / 'resources' / 'buttonmaps' / 'xml' / provider / 'batocera_{}.xml'
    mkdir_if_not_exists(kodiJoystick.parent)
    writeKodiConfigs(kodiJoystick, controllersFromES, provider)

    # force the udev plugin
    with ensure_parents_and_open(_KODI_USERDATA / "addon_data" / "peripheral.joystick" / "settings.xml", "w") as f:
        f.write("<settings version=\"2\">")

        if provider == "linux":
            f.write("<setting id=\"driver_linux\">0</setting>")
        if provider == "udev":
            f.write("<setting id=\"driver_linux\">1</setting>")

        f.write("</settings>")

    # disable the kodi splash by default (nicer integration)
    advxml = _KODI_USERDATA / "advancedsettings.xml"
    if not advxml.exists():
        with ensure_parents_and_open(advxml, "w") as f:
            f.write("<advancedsettings><splash>false</splash></advancedsettings>")

def vidpid(guid: str) -> tuple[str, str]:
  return guid[10:12]+guid[8:10], guid[18:20]+guid[16:18]
