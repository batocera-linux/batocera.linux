#!/usr/bin/env python
import xml.etree.ElementTree as ET
import recalboxFiles

esInputs = recalboxFiles.esInputs


class Input:
    def __init__(self, name, type, id, value, code):
        self.name = name
        self.type = type
        self.id = id
        self.value = value
        self.code = code


class Controller:
    def __init__(self, configName, type, guid, player, index="-1", realName="", inputs=None, dev=None, nbaxes=None):
        self.type = type
        self.configName = configName
        self.index = index
        self.realName = realName
        self.guid = guid
        self.player = player
        self.dev = dev
        self.nbaxes = nbaxes
        if inputs == None:
            self.inputs = dict()
        else:
            self.inputs = inputs
            
    def generateSDLGameDBLine(self):
        # Making a dirty assumption here : if a dpad is an axis, then it shouldn't have any analog joystick
        nameMapping = {
            'a'             : { 'button' : 'b' },
            'b'             : { 'button' : 'a' },
            'x'             : { 'button' : 'y' },
            'y'             : { 'button' : 'x' },
            'start'         : { 'button' : 'start' },
            'select'        : { 'button' : 'back' },
            'pageup'        : { 'button' : 'leftshoulder' },
            'pagedown'      : { 'button' : 'rightshoulder' },
            'l2'            : { 'button' : 'lefttrigger', 'axis' : 'lefttrigger' },
            'r2'            : { 'button' : 'righttrigger', 'axis' : 'righttrigger' },
            'l3'            : { 'button' : 'leftstick' },
            'r3'            : { 'button' : 'rightstick' },
            'up'            : { 'button' : 'dpup',    'hat' : 'dpup', 'axis' : 'lefty' },
            'down'          : { 'button' : 'dpdown',  'hat' : 'dpdown' },
            'left'          : { 'button' : 'dpleft',  'hat' : 'dpleft', 'axis' : 'leftx' },
            'right'         : { 'button' : 'dpright', 'hat' : 'dpright' },
            'joystick1up'   : { 'axis' : 'lefty' },
            'joystick1left' : { 'axis' : 'leftx' },
            'joystick2up'   : { 'axis' : 'righty' },
            'joystick2left' : { 'axis' : 'rightx' },
            'hotkey'        : { 'button' : 'guide' }
        }
        typePrefix = {
            'axis'   : 'a',
            'button' : 'b',
            'hat'    : 'h0.' # Force dpad 0 until ES handles others
        }
        
        if not self.inputs:
            return None
            
        strOut = "{},{},platform:Linux,".format(self.guid, self.configName)
        
        for idx, input in self.inputs.iteritems():
            if input.name in nameMapping and input.type in typePrefix and input.type in nameMapping[input.name] :
                if input.type == 'hat':
                    strOut += "{}:{}{},".format(nameMapping[input.name][input.type], typePrefix[input.type], input.value)
                else:
                    strOut += "{}:{}{},".format(nameMapping[input.name][input.type], typePrefix[input.type], input.id)
        
        return strOut


# Load all controllers from the es_input.cfg
def loadAllControllersConfig():
    controllers = dict()
    tree = ET.parse(esInputs)
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
    tree = ET.parse(esInputs)
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
def loadControllerConfig(p1index, p1guid, p1name, p1dev, p1nbaxes, p2index, p2guid, p2name, p2dev, p2nbaxes, p3index, p3guid, p3name, p3dev, p3nbaxes,
                         p4index, p4guid, p4name, p4dev, p4nbaxes, p5index, p5guid, p5name, p5dev, p5nbaxes):
    playerControllers = dict()
    controllers = loadAllControllersConfig()

    newController = findBestControllerConfig(controllers, '1', p1guid, p1index, p1name, p1dev, p1nbaxes)
    if newController:
        playerControllers["1"] = newController
    newController = findBestControllerConfig(controllers, '2', p2guid, p2index, p2name, p2dev, p2nbaxes)
    if newController:
        playerControllers["2"] = newController
    newController = findBestControllerConfig(controllers, '3', p3guid, p3index, p3name, p3dev, p3nbaxes)
    if newController:
        playerControllers["3"] = newController
    newController = findBestControllerConfig(controllers, '4', p4guid, p4index, p4name, p4dev, p4nbaxes)
    if newController:
        playerControllers["4"] = newController
    newController = findBestControllerConfig(controllers, '5', p5guid, p5index, p5name, p5dev, p5nbaxes)
    if newController:
        playerControllers["5"] = newController
    return playerControllers

def loadControllerConfig2(**kwargs):
    playerControllers = dict()
    controllers = loadAllControllersConfig()
    
    for i in range(1, 6):
        num = str(i)
        pguid = kwargs.get('p{}guid'.format(num), None)
        pindex = kwargs.get('p{}index'.format(num), None)
        pname = kwargs.get('p{}name'.format(num), None)
        pdev = kwargs.get('p{}dev'.format(num), None)
        pnbaxes = kwargs.get('p{}nbaxes'.format(num), None)
        if pdev is None:
            pdev = kwargs.get('p{}devicepath'.format(num), None)
        newController = findBestControllerConfig(controllers, num, pguid, pindex, pname, pdev, pnbaxes)
        if newController:
            playerControllers[num] = newController
    return playerControllers

def findBestControllerConfig(controllers, x, pxguid, pxindex, pxname, pxdev, pxnbaxes):
    # when there will have more joysticks, use hash tables
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller.guid == pxguid and controller.configName == pxname:
            return Controller(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                              controller.inputs, pxdev, pxnbaxes)
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller.guid == pxguid:
            return Controller(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                              controller.inputs, pxdev, pxnbaxes)
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller.configName == pxname:
            return Controller(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                              controller.inputs, pxdev, pxnbaxes)
    return None

def generateSDLGameDBAllControllers(controllers, outputFile = "/tmp/gamecontrollerdb.txt"):
    finalData = []
    for idx, controller in controllers.iteritems():
        finalData.append(controller.generateSDLGameDBLine())
    sdlData = "\n".join(finalData)
    with open(outputFile, "w") as text_file:
        text_file.write(sdlData)
    return outputFile
