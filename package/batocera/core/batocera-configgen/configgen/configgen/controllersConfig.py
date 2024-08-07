#!/usr/bin/env python

import xml.etree.ElementTree as ET
import batoceraFiles
import os
import pyudev
import evdev
import re

from utils.logger import get_logger
eslog = get_logger(__name__)


"""Default mapping of Batocera keys to SDL_GAMECONTROLLERCONFIG keys."""
_DEFAULT_SDL_MAPPING = {
    'b':      'a',  'a':        'b',
    'x':      'y',  'y':        'x',
    'l2':     'lefttrigger',  'r2':    'righttrigger',
    'l3':     'leftstick',  'r3':    'rightstick',
    'pageup': 'leftshoulder', 'pagedown': 'rightshoulder',
    'start':     'start',  'select':    'back',
    'up': 'dpup', 'down': 'dpdown', 'left': 'dpleft', 'right': 'dpright',
    'joystick1up': 'lefty', 'joystick1left': 'leftx',
    'joystick2up': 'righty', 'joystick2left': 'rightx', 'hotkey': 'guide'
}

class Input:
    def __init__(self, name, type, id, value, code):
        self.name = name
        self.type = type
        self.id = id
        self.value = value
        self.code = code


class Controller:
    def __init__(self, configName, type, guid, player, index="-1", realName="", inputs=None, dev=None, nbbuttons=None, nbhats=None, nbaxes=None):
        self.type = type
        self.configName = configName
        self.index = index
        self.realName = realName
        self.guid = guid
        self.player = player
        self.dev = dev
        self.nbbuttons = nbbuttons
        self.nbhats = nbhats
        self.nbaxes = nbaxes
        if inputs == None:
            self.inputs = dict()
        else:
            self.inputs = inputs

    def generateSDLGameDBLine(self):
        return _generateSdlGameControllerConfig(self)

# Load all controllers from the es_input.cfg
def loadAllControllersConfig():
    controllers = dict()
    tree = ET.parse(batoceraFiles.esInputs)
    root = tree.getroot()
    for controller in root.findall(".//inputConfig"):
        controllerInstance = Controller(controller.get("deviceName"), controller.get("type"),
                                        controller.get("deviceGUID"), None, None)
        uidname = controller.get("deviceGUID") + controller.get("deviceName")
        controllers[uidname] = controllerInstance
        for input in controller.findall("input"):
            inputInstance = Input(input.get("name"), input.get("type"), input.get("id"), input.get("value"), input.get("code"))
            controllerInstance.inputs[input.get("name")] = inputInstance
    return controllers


# Load all controllers from the es_input.cfg
def loadAllControllersByNameConfig():
    controllers = dict()
    tree = ET.parse(batoceraFiles.esInputs)
    root = tree.getroot()
    for controller in root.findall(".//inputConfig"):
        controllerInstance = Controller(controller.get("deviceName"), controller.get("type"),
                                        controller.get("deviceGUID"), None, None)
        deviceName = controller.get("deviceName")
        controllers[deviceName] = controllerInstance
        for input in controller.findall("input"):
            inputInstance = Input(input.get("name"), input.get("type"), input.get("id"), input.get("value"), input.get("code"))
            controllerInstance.inputs[input.get("name")] = inputInstance
    return controllers


# Create a controller array with the player id as a key
def loadControllerConfig(controllersInput):
    playerControllers = dict()
    controllers = loadAllControllersConfig()

    for i, ci in enumerate(controllersInput):
        newController = findBestControllerConfig(controllers, str(i+1), ci["guid"], ci["index"], ci["name"], ci["devicepath"], ci["nbbuttons"], ci["nbhats"], ci["nbaxes"])
        if newController:
            playerControllers[str(i+1)] = newController
    return playerControllers

def findBestControllerConfig(controllers, x, pxguid, pxindex, pxname, pxdev, pxnbbuttons, pxnbhats, pxnbaxes):
    # when there will have more joysticks, use hash tables
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller.guid == pxguid and controller.configName == pxname:
            return Controller(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                              controller.inputs, pxdev, pxnbbuttons, pxnbhats, pxnbaxes)
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller.guid == pxguid:
            return Controller(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                              controller.inputs, pxdev, pxnbbuttons, pxnbhats, pxnbaxes)
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller.configName == pxname:
            return Controller(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                              controller.inputs, pxdev, pxnbbuttons, pxnbhats, pxnbaxes)
    return None


def _generateSdlGameControllerConfig(controller, sdlMapping=_DEFAULT_SDL_MAPPING):
    """Returns an SDL_GAMECONTROLLERCONFIG-formatted string for the given configuration."""
    config = []
    config.append(controller.guid)
    config.append(controller.realName)
    config.append("platform:Linux")

    def add_mapping(input):
        keyname = sdlMapping.get(input.name, None)
        if keyname is None:
            return
        sdlConf = _keyToSdlGameControllerConfig(
            keyname, input.name, input.type, input.id, input.value)
        if sdlConf is not None:
            config.append(sdlConf)

    # "hotkey" is often mapped to an existing button but such a duplicate mapping
    # confuses SDL apps. We add "hotkey" mapping only if its target isn't also mapped elsewhere.
    hotkey_input = None
    mapped_button_ids = set()
    for k in controller.inputs:
        input = controller.inputs[k]
        if input.name is None:
            continue
        if input.name == 'hotkey':
            hotkey_input = input
            continue
        if input.type == 'button':
            mapped_button_ids.add(input.id)
        add_mapping(input)

    if hotkey_input is not None and not hotkey_input.id in mapped_button_ids:
        add_mapping(hotkey_input)
    config.append('')
    return ','.join(config)


def _keyToSdlGameControllerConfig(keyname, name, type, id, value=None):
    """
    Converts a key mapping to the SDL_GAMECONTROLLER format.

    Arguments:
      keyname: (str) SDL_GAMECONTROLLERCONFIG input name.
      name: (str) `es_input.cfg` input name.
      type: (str) 'button', 'hat', or 'axis'
      id: (int) Numeric key id.
      value: (int) Hat value. Only used if type == 'hat' or type == 'axis' and 'joystick' in name.
    Returns:
      (str) SDL_GAMECONTROLLERCONFIG-formatted key mapping string.
    Examples:
      _keyToSdlGameControllerConfig('leftshoulder', 'l1', 'button', 6)
        'leftshoulder:b6'

      _keyToSdlGameControllerConfig('dpleft', 'left', 'hat', 0, 8)
        'dpleft:h0.8'

      _keyToSdlGameControllerConfig('lefty', 'joystick1up', 'axis', 1, -1)
        'lefty:a1'

      _keyToSdlGameControllerConfig('lefty', 'joystick1up', 'axis', 1, 1)
        'lefty:a1~'

      _keyToSdlGameControllerConfig('dpup', 'up', 'axis', 1, -1)
        'dpup:-a1'
    """
    if type == 'button':
        return f'{keyname}:b{id}'
    elif type == 'hat':
        return f'{keyname}:h{id}.{value}'
    elif type == 'axis':
        if 'joystick' in name:
            return '{}:a{}{}'.format(keyname, id, '~' if int(value) > 0 else '')
        elif keyname in ('dpup', 'dpdown', 'dpleft', 'dpright'):
            return '{}:{}a{}'.format(keyname, '-' if int(value) < 0 else '+', id)
        else:
            return f'{keyname}:a{id}'
    elif type == 'key':
        return None
    else:
        raise ValueError('unknown key type: {!r}'.format(type))


def generateSdlGameControllerConfig(controllers):
    configs = []
    for idx, controller in controllers.items():
        configs.append(controller.generateSDLGameDBLine())
    return "\n".join(configs)


def writeSDLGameDBAllControllers(controllers, outputFile = "/tmp/gamecontrollerdb.txt"):
    with open(outputFile, "w") as text_file:
        text_file.write(generateSdlGameControllerConfig(controllers))
    return outputFile

def generateSdlGameControllerPadsOrderConfig(controllers):
    res = ""
    for idx, controller in controllers.items():
        if res != "":
            res = res + ";"
        res = res + str(controller.index)
    return res

def gunsNeedCrosses(guns):
    # no gun, enable the cross for joysticks, mouses...
    if len(guns) == 0:
        return True

    for gun in guns:
        if guns[gun]["need_cross"]:
            return True
    return False

# returns None is no border is wanted
def gunsBordersSizeName(guns, config):
    bordersSize = "medium"
    if "controllers.guns.borderssize" in config and config["controllers.guns.borderssize"]:
        bordersSize = config["controllers.guns.borderssize"]

    # overriden by specific options
    bordersmode = "normal"
    if "controllers.guns.bordersmode" in config and config["controllers.guns.bordersmode"] and config["controllers.guns.bordersmode"] != "auto":
        bordersmode = config["controllers.guns.bordersmode"]
    if "bordersmode" in config and config["bordersmode"] and config["bordersmode"] != "auto":
        bordersmode = config["bordersmode"]

    # others are gameonly and normal
    if bordersmode == "hidden":
        return None
    if bordersmode == "force":
        return bordersSize

    for gun in guns:
        if guns[gun]["need_borders"]:
            return bordersSize
    return None

# returns None to follow the bezel overlay size by default
def gunsBorderRatioType(guns, config):
    # add emulator specific configs here
    if "m3_wideScreen" in config and config["m3_wideScreen"] == "1":
        eslog.debug("Model 3 set to widescreen")
        return None
    else:
        # check the display esolution is already 4:3
        eslog.debug("Setting gun border ratio to 4:3")
        return "4:3"
    return None

def getMouseButtons(device):
  caps = device.capabilities()
  caps_keys = caps[evdev.ecodes.EV_KEY]
  caps_filter = [evdev.ecodes.BTN_LEFT, evdev.ecodes.BTN_RIGHT, evdev.ecodes.BTN_MIDDLE, evdev.ecodes.BTN_1, evdev.ecodes.BTN_2, evdev.ecodes.BTN_3, evdev.ecodes.BTN_4, evdev.ecodes.BTN_5, evdev.ecodes.BTN_6, evdev.ecodes.BTN_7, evdev.ecodes.BTN_8]
  caps_intersection = list(set(caps_keys) & set(caps_filter))
  buttons = []
  if evdev.ecodes.BTN_LEFT in caps_intersection:
    buttons.append("left")
  if evdev.ecodes.BTN_RIGHT in caps_intersection:
    buttons.append("right")
  if evdev.ecodes.BTN_MIDDLE in caps_intersection:
    buttons.append("middle")
  if evdev.ecodes.BTN_1 in caps_intersection:
    buttons.append("1")
  if evdev.ecodes.BTN_2 in caps_intersection:
    buttons.append("2")
  if evdev.ecodes.BTN_3 in caps_intersection:
    buttons.append("3")
  if evdev.ecodes.BTN_4 in caps_intersection:
    buttons.append("4")
  if evdev.ecodes.BTN_5 in caps_intersection:
    buttons.append("5")
  if evdev.ecodes.BTN_6 in caps_intersection:
    buttons.append("6")
  if evdev.ecodes.BTN_7 in caps_intersection:
    buttons.append("7")
  if evdev.ecodes.BTN_8 in caps_intersection:
    buttons.append("8")
  return buttons

def mouseButtonToCode(button):
    if button == "left":
        return evdev.ecodes.BTN_LEFT
    if button == "right":
        return evdev.ecodes.BTN_RIGHT
    if button == "middle":
        return evdev.ecodes.BTN_MIDDLE
    if button == "1":
        return evdev.ecodes.BTN_1
    if button == "2":
        return evdev.ecodes.BTN_2
    if button == "3":
        return evdev.ecodes.BTN_3
    if button == "4":
        return evdev.ecodes.BTN_4
    if button == "5":
        return evdev.ecodes.BTN_5
    if button == "6":
        return evdev.ecodes.BTN_6
    if button == "7":
        return evdev.ecodes.BTN_7
    if button == "8":
        return evdev.ecodes.BTN_8
    return None

def getGuns():
    import pyudev
    import re

    guns = {}
    context = pyudev.Context()

    # guns are mouses, just filter on them
    mouses = context.list_devices(subsystem='input')

    # keep only mouses with /dev/iput/eventxx
    mouses_clean = {}
    for mouse in mouses:
        matches = re.match(r"^/dev/input/event([0-9]*)$", str(mouse.device_node))
        if matches != None:
            if ("ID_INPUT_MOUSE" in mouse.properties and mouse.properties["ID_INPUT_MOUSE"]) == '1':
                mouses_clean[int(matches.group(1))] = mouse
    mouses = mouses_clean

    nmouse = 0
    ngun   = 0
    for eventid in sorted(mouses):
        eslog.info("found mouse {} at {} with id_mouse={}".format(nmouse, mouses[eventid].device_node, nmouse))
        if "ID_INPUT_GUN" not in mouses[eventid].properties or mouses[eventid].properties["ID_INPUT_GUN"] != "1":
            nmouse = nmouse + 1
            continue

        device = evdev.InputDevice(mouses[eventid].device_node)
        buttons = getMouseButtons(device)

        # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE (TOUCHPAD are listed after mouses)
        need_cross   = "ID_INPUT_GUN_NEED_CROSS"   in mouses[eventid].properties and mouses[eventid].properties["ID_INPUT_GUN_NEED_CROSS"]   == '1'
        need_borders = "ID_INPUT_GUN_NEED_BORDERS" in mouses[eventid].properties and mouses[eventid].properties["ID_INPUT_GUN_NEED_BORDERS"] == '1'
        guns[ngun] = {"node": mouses[eventid].device_node, "id_mouse": nmouse, "need_cross": need_cross, "need_borders": need_borders, "name": device.name, "buttons": buttons}
        eslog.info("found gun {} at {} with id_mouse={} ({})".format(ngun, mouses[eventid].device_node, nmouse, guns[ngun]["name"]))
        nmouse = nmouse + 1
        ngun = ngun + 1

    if len(guns) == 0:
        eslog.info("no gun found")
    return guns

def shortNameFromPath(path):
    redname = os.path.splitext(os.path.basename(path))[0].lower()
    inpar   = False
    inblock = False
    ret = ""
    for c in redname:
        if not inpar and not inblock and ( (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') ):
            ret += c
        elif c == '(':
            inpar = True
        elif c == ')':
            inpar = False
        elif c == '[':
            inblock = True
        elif c == ']':
            inblock = True
    return ret

def getGamesMetaData(system, rom):
    # load the database
    tree = ET.parse(batoceraFiles.esGamesMetadata)
    root = tree.getroot()
    game = shortNameFromPath(rom)
    res = {}
    eslog.info("looking for game metadata ({}, {})".format(system, game))

    targetSystem = system
    # hardcoded list of system for arcade
    # this list can be found in es_system.yml
    # at this stage we don't know if arcade will be kept as one system only in metadata, so i hardcode this list for now
    if system in ['naomi', 'naomi2', 'atomiswave', 'fbneo', 'mame', 'neogeo', 'triforce', 'hypseus-singe', 'model2', 'model3', 'hikaru', 'gaelco', 'cave3rd', 'namco2x6']:
        targetSystem = 'arcade'

    for nodesystem in root.findall(".//system"):
        for sysname in nodesystem.get("name").split(','):
          if sysname == targetSystem:
              # search the game named default
              for nodegame in nodesystem.findall(".//game"):
                  if nodegame.get("name") == "default":
                      for child in nodegame:
                          for attribute in child.attrib:
                              key = "{}_{}".format(child.tag, attribute)
                              res[key] = child.get(attribute)
                              eslog.info("found game metadata {}={} (system level)".format(key, res[key]))
                      break
              for nodegame in nodesystem.findall(".//game"):
                  if nodegame.get("name") != "default" and nodegame.get("name") in game:
                      for child in nodegame:
                          for attribute in child.attrib:
                              key = "{}_{}".format(child.tag, attribute)
                              res[key] = child.get(attribute)
                              eslog.info("found game metadata {}={}".format(key, res[key]))
                      return res
    return res

def dev2int(dev):
    matches = re.match(r"^/dev/input/event([0-9]*)$", dev)
    if matches is None:
        return None
    return int(matches.group(1))

def getDevicesInformation():
  groups    = {}
  devices   = {}
  context   = pyudev.Context()
  events    = context.list_devices(subsystem='input')
  mouses    = []
  joysticks = []
  for ev in events:
    eventId = dev2int(str(ev.device_node))
    if eventId != None:
      isJoystick = ("ID_INPUT_JOYSTICK" in ev.properties and ev.properties["ID_INPUT_JOYSTICK"] == "1")
      isWheel    = ("ID_INPUT_WHEEL"    in ev.properties and ev.properties["ID_INPUT_WHEEL"] == "1")
      isMouse    = ("ID_INPUT_MOUSE"    in ev.properties and ev.properties["ID_INPUT_MOUSE"] == "1") or ("ID_INPUT_TOUCHPAD" in ev.properties and ev.properties["ID_INPUT_TOUCHPAD"] == "1")
      group = None
      if "ID_PATH" in ev.properties:
        group = ev.properties["ID_PATH"]
      if isJoystick or isMouse:
        if isJoystick:
          joysticks.append(eventId)
        if isMouse:
          mouses.append(eventId)
        devices[eventId] = { "node": ev.device_node, "group": group, "isJoystick": isJoystick, "isWheel": isWheel, "isMouse": isMouse }
        if "ID_PATH" in ev.properties:
          if isWheel and "WHEEL_ROTATION_ANGLE" in ev.properties:
              devices[eventId]["wheel_rotation"] = int(ev.properties["WHEEL_ROTATION_ANGLE"])
          if group not in groups:
            groups[group] = []
          groups[group].append(ev.device_node)
  mouses.sort()
  joysticks.sort()
  res = {}
  for device in devices:
    d = devices[device]
    dgroup = None
    if d["group"] is not None:
        dgroup = groups[d["group"]].copy()
        dgroup.remove(d["node"])
    nmouse    = None
    njoystick = None
    if d["isJoystick"]:
      njoystick = joysticks.index(device)
    nmouse = None
    if d["isMouse"]:
      nmouse = mouses.index(device)
    res[d["node"]] = { "eventId": device, "isJoystick": d["isJoystick"], "isWheel": d["isWheel"], "isMouse": d["isMouse"], "associatedDevices": dgroup, "joystick_index": njoystick, "mouse_index": nmouse }
    if "wheel_rotation" in d:
        res[d["node"]]["wheel_rotation"] = d["wheel_rotation"]
  return res

def getAssociatedMouse(devicesInformation, dev):
    if dev not in devicesInformation or devicesInformation[dev]["associatedDevices"] is None:
        return None
    for candidate in devicesInformation[dev]["associatedDevices"]:
        if devicesInformation[candidate]["isMouse"]:
            return candidate
    return None
