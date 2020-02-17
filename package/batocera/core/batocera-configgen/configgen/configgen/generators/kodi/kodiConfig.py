#!/usr/bin/env python

import controllersConfig as controllers
import signal
import os
import batoceraFiles
from xml.dom import minidom
# TODO: python3 - delete me!
import codecs

def writeKodiConfigs(currentControllers):
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

        # initialized the file
        kodiJoy = open(batoceraFiles.kodiJoystick.format(cur.guid), "w")
        # TODO: python 3 - workawround to encode files in utf-8
        kodiJoy = codecs.open(batoceraFiles.kodiJoystick.format(cur.guid), "w", "utf-8")
        config = minidom.Document()
        xmlbuttonmap = config.createElement('buttonmap')
        config.appendChild(xmlbuttonmap)

        # skip duplicates
        if cur.configName in controllersDone:
            break;
        else:
            controllersDone[cur.configName] = True

        xmldevice = config.createElement('device')
        xmldevice.attributes["name"] = cur.configName
        xmldevice.attributes["provider"] = "linux"
        xmldevice.attributes["buttoncount"] = cur.nbbuttons
        xmldevice.attributes["axiscount"] = str(2*int(cur.nbhats) + int(cur.nbaxes))
        xmlbuttonmap.appendChild(xmldevice)
        xmlcontroller = config.createElement('controller')
        xmlcontroller.attributes["id"] = "game.controller.default"

        sticksNode = {}

        for x in cur.inputs:
            input = cur.inputs[x]
            if input.name in kodimapping:
                    if input.type == 'button':
                        xmlbutton = config.createElement('feature')
                        xmlbutton.attributes["name"] = kodimapping[input.name]
                        xmlbutton.attributes["button"] = str(int(input.id))
                        xmlcontroller.appendChild(xmlbutton)

                    elif input.type == 'hat' and int(input.value) in kodihatspositions:
                        xmlhat = config.createElement('feature')
                        val = ""
                        if kodihatspositions[int(input.value)] == "left" or kodihatspositions[int(input.value)] == "right":
                            val = cur.nbaxes
                        else:
                            val = str(int(cur.nbaxes)+1)
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


def writeKodiConfig(controllersFromES):
    # if there is no controller, don't remove the current generated one
    # it allows people to start kodi at startup when having only bluetooth joysticks
    # or this allows people to plug the last used joystick
    if len(controllersFromES) == 0:
        return
    directory = os.path.dirname(batoceraFiles.kodiJoystick)
    if not os.path.exists(directory):
        os.makedirs(directory)
    writeKodiConfigs(controllersFromES)
