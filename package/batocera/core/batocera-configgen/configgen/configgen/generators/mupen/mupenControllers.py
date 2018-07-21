#!/usr/bin/env python
import sys
import os
import ConfigParser
from controllersConfig import Input
from xml.dom import minidom

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from settings.unixSettings import UnixSettings
import recalboxFiles

# Must read :
# http://mupen64plus.org/wiki/index.php?title=Mupen64Plus_Plugin_Parameters

mupenSettings = UnixSettings(recalboxFiles.mupenCustom, separator=' ')
Config = ConfigParser.ConfigParser()
# To prevent ConfigParser from converting to lower case
Config.optionxform = str

# Mupen doesn't like to have 2 buttons mapped for N64 pad entry. That's why r2 is commented for now. 1 axis and 1 button is ok
mupenHatToAxis = {'1': 'Up', '2': 'Right', '4': 'Down', '8': 'Left'}
mupenDoubleAxis = {0:'X Axis', 1:'Y Axis'}

def getMupenMappingFile():
    if os.path.exists(recalboxFiles.mupenMappingUser):
        return recalboxFiles.mupenMappingUser
    else:
        return recalboxFiles.mupenMappingSystem

def getMupenMapping():
    dom = minidom.parse(getMupenMappingFile())
    map = dict()
    for inputs in dom.getElementsByTagName('inputList'):
        for input in inputs.childNodes:
            if input.attributes:
                if input.attributes['name']:
                        if input.attributes['value']:
                                map[input.attributes['name'].value] = input.attributes['value'].value
    return map

# Write a configuration for a specified controller
def writeControllersConfig(controllers):
	if os.path.isfile(recalboxFiles.mupenInput):
		os.remove(recalboxFiles.mupenInput)

	for controller in controllers:
		player = controllers[controller]
		# Dynamic controller bindings
		config = defineControllerKeys(player)
		# Write to file
		writeToIni(player, config)


def defineControllerKeys(controller):
        mupenmapping = getMupenMapping()

	# config holds the final pad configuration in the mupen style
	# ex: config['DPad U'] = "button(1)"
	config = dict()
	config['AnalogDeadzone'] = mupenmapping['AnalogDeadzone']
	
	# Dirty hack : the input.xml adds 2 directions per joystick, ES handles just 1
	fakeSticks = { 'joystick2up' : 'joystick2down'
			, 'joystick2left' : 'joystick2right'}
	print "Banzaiiiii"
	# Cheat on the controller
	for realStick, fakeStick in fakeSticks.iteritems():
		if realStick in controller.inputs:
			print fakeStick + "-> " + realStick
			inputVar =  Input(fakeStick
					, controller.inputs[realStick].type
					, controller.inputs[realStick].id
					, str(-int(controller.inputs[realStick].value))
					, controller.inputs[realStick].code)
			controller.inputs[fakeStick] = inputVar
	
	for inputIdx in controller.inputs:
		input = controller.inputs[inputIdx]
		if input.name in mupenmapping and mupenmapping[input.name] != "":
                        value=setControllerLine(mupenmapping, input, mupenmapping[input.name])
                        # Handle multiple inputs for a single N64 Pad input
                        if mupenmapping[input.name] not in config :
                                config[mupenmapping[input.name]] = value
                        else:
                                config[mupenmapping[input.name]] += " " + value

	# Big dirty hack : handle when the pad has no analog sticks. Only Start A, B L and R survive from the previous configuration
	if "X Axis" not in config and "Y Axis" not in config:
		# remap Z Trig
		config['Z Trig'] = setControllerLine(mupenmapping, controller.inputs['x'], "Z Trig")
		# remove C Button U and R
		if 'C Button U' in config: del config['C Button U']
		if 'C Button R' in config: del config['C Button R']
		# remove DPad
		if 'DPad U' in config:del config['DPad U']
		if 'DPad D' in config:del config['DPad D']
		if 'DPad L' in config:del config['DPad L']
		if 'DPad R' in config:del config['DPad R']
		# Remap up/down/left/right to  X and Y Axis
		if controller.inputs['left'].type == 'hat':
			config['X Axis'] = "hat({} {} {})".format(controller.inputs['left'].id, mupenHatToAxis[controller.inputs['left'].value], mupenHatToAxis[controller.inputs['right'].value])
			config['Y Axis'] = "hat({} {} {})".format(controller.inputs['up'].id, mupenHatToAxis[controller.inputs['up'].value], mupenHatToAxis[controller.inputs['down'].value])
		elif controller.inputs['left'].type == 'axis':
			config['X Axis'] = setControllerLine(mupenmapping, controller.inputs['left'], "X Axis")
			config['Y Axis'] = setControllerLine(mupenmapping, controller.inputs['up'], "Y Axis")
		elif controller.inputs['left'].type == 'button':
			config['X Axis'] = "button({},{})".format(controller.inputs['left'].id, controller.inputs['right'].id)
			config['Y Axis'] = "button({},{})".format(controller.inputs['up'].id, controller.inputs['down'].id)
	return config


def setControllerLine(mupenmapping, input, mupenSettingName):
	value = ''
	inputType = input.type
	if inputType == 'button':
		value = "button({})".format(input.id)
	elif inputType == 'hat':
		value = "hat({} {})".format(input.id, mupenHatToAxis[input.value])
	elif inputType == 'axis':
		# Generic case for joystick1up and joystick1left
		if mupenSettingName in mupenDoubleAxis.values():
			# X axis : value = -1 for left, +1 for right
			# Y axis : value = -1 for up, +1 for down
			if input.value == "-1":				
				value = "axis({}-,{}+)".format(input.id, input.id)
			else:
				value = "axis({}+,{}-)".format(input.id, input.id)
		else:
                        if input.value == "1":
                                value = "axis({}+)".format(input.id)
                        else:
                                value = "axis({}-)".format(input.id)
	return value


def writeToIni(controller, config):
	Config.read(recalboxFiles.mupenInput)
	section = controller.realName

	# Avoid a crash when writing twice a same section
	if Config.has_section(section):
		return None

	# Open file
	cfgfile = open(recalboxFiles.mupenInput,'w+')

	# Write static config
	Config.add_section(section)
	Config.set(section, 'plugged', True)
	Config.set(section, 'plugin', 2)
	Config.set(section, 'AnalogDeadzone', config['AnalogDeadzone'])
	Config.set(section, 'AnalogPeak', "32768,32768")
	Config.set(section, 'Mempak switch', "")
	Config.set(section, 'Rumblepak switch', "")
	Config.set(section, 'mouse', "False")
	#Config.set(section, 'name', controller.realName)
	#Config.set(section, 'device', controller.index)

	# Write dynamic config
	for inputName in sorted(config):
		Config.set(section, inputName, config[inputName])

	Config.write(cfgfile)
	cfgfile.close()
