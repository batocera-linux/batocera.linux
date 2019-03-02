#!/usr/bin/env python
import sys
import os
import recalboxFiles
from controllersConfig import Input
from shutil import copyfile

advanceMapping = {
	'a' :              'p{}_button2',
	'b' :              [ 'p{}_button1', 'ui_select' ],
	'x' :              'p{}_button4',
	'y' :              'p{}_button3',
	'start' :          'start{}',
	'select':          'coin{}',
	#~ 'hotkey' :        '',
	'pageup' :         'p{}_button5',
	'pagedown' :       'p{}_button6',
	'up' :             [ 'p{}_up',    'ui_up' ],
	'down' :           [ 'p{}_down',  'ui_down' ],
	'left' :           [ 'p{}_left',  'ui_left' ],
	'right' :          [ 'p{}_right', 'ui_right' ],
	'joystick1up' :    [ 'p{}_up',    'p{}_doubleleft_up',    'ui_up'    ],
	'joystick1down' :  [ 'p{}_down',  'p{}_doubleleft_down',  'ui_down'  ],
	'joystick1left' :  [ 'p{}_left',  'p{}_doubleleft_left',  'ui_left'  ],
	'joystick1right' : [ 'p{}_right', 'p{}_doubleleft_right', 'ui_right' ],
	'joystick2up' :    'p{}_doubleright_up',
	'joystick2down' :  'p{}_doubleright_down',
	'joystick2left' :  'p{}_doubleright_left',
	'joystick2right' : 'p{}_doubleright_right',
	'l2' :             'p{}_button7',
	#~ 'r2' :            'p{}_button8',
	'r2' :             'ui_configure',
	'l3' :             'p{}_button9',
	'r3' :             'p{}_button10'
}

secondaryMapping = {
	'joystick1up' :  'joystick1down',
	'joystick1left' : 'joystick1right',
	'joystick2up' :  'joystick2down',
	'joystick2left' : 'joystick2right',
}

advanceCombo = {
	'a' : 'ui_soft_reset',
	'y' : 'ui_save_state',
	'x' : 'ui_load_state',
	'start' : 'ui_cancel',
	'right' : 'ui_turbo',
	#~ 'r2' : 'ui_mode_pred', # Comment this one for now as it needs a "not" on the ui_configure
	'l2' :'ui_mode_pred'
}

def writeControllersConfig(system, controllers):
	finalConfig = getDefaultConfig()
	
	# Looks like advmame sets the joystick order on the eventId from /dev/input/eventX or /dev/input/jsX, not using SDL. So we should reorder that
	orderedControllers = dict()
	for key, controller in controllers.iteritems():
		orderedControllers[controller.dev] = controller
	i = 0
	for key in sorted(orderedControllers):
		orderedControllers[key].index = i
		i = i+1
	for key, controller in orderedControllers.iteritems():
		# Add fake joystick directions
		for realStick, fakeStick in secondaryMapping.iteritems():
			if realStick in controller.inputs:
				inputVar =  Input(fakeStick
								, controller.inputs[realStick].type
								, controller.inputs[realStick].id
								, str(-int(controller.inputs[realStick].value))
								, controller.inputs[realStick].code)
				controller.inputs[fakeStick] = inputVar
		ctrlConfig = getControllerConfig(controller)
		finalConfig = intelligentExtend(finalConfig, ctrlConfig)
	
	with open(recalboxFiles.advancemameConfig,'w') as f:
		for key in sorted(finalConfig):
			try:
				line = "{} {}\n".format(key, finalConfig[key])
				f.write(line)
			except ValueError:
				break

def getDefaultConfig():
	# Open the default file
	with open(recalboxFiles.advancemameConfigOrigin) as f:
		# read the values
		content = f.readlines()
	
	returnValue = dict()
	# Reorder to a dict
	for line in content:
		# There may be some empty lines. Lazy method to handle errors on the split that would crash
		try:
			index, value = line.split(" ", 1)
			returnValue[index] = value.strip('\n')
			continue
		except ValueError:
			continue
		
	return returnValue

def getControllerConfig(controller):
	returnValue = dict()
	# Read the pad and configure
	for inpName, inp in controller.inputs.iteritems():
		if inpName in advanceMapping:
			if not isinstance(advanceMapping[inpName], list):
				index = "input_map[{}]".format(advanceMapping[inpName].format(controller.player))
				value = generateButton(controller.index, inp)
				returnValue = intelligentAppend(returnValue, index, value)
			else:
				for event in advanceMapping[inpName]:
					index = "input_map[{}]".format(event.format(controller.player))
					value = generateButton(controller.index, inp)
					returnValue = intelligentAppend(returnValue, index, value)

	# For player 1 only : add UI combos
	if controller.player == "1" and 'hotkey' in controller.inputs:
		hk = controller.inputs['hotkey']
		for key, event in advanceCombo.iteritems():
			if key in controller.inputs:
				buttonInput = controller.inputs[key]
				value = generateCombo(controller.index, buttonInput, hk)
				index = "input_map[{}]".format(event)
				returnValue = intelligentAppend(returnValue, index, value)

	return returnValue

def intelligentAppend(sourceDict, index, value):
	if index in sourceDict:
		sourceDict[index] += " or {}".format(value)
	else:
		sourceDict[index] = value
	return sourceDict

def intelligentExtend(sourceDict, mergeDict):
	for index, value in mergeDict.iteritems():
		sourceDict = intelligentAppend(sourceDict, index, value)
	return sourceDict
	
def generateButton(joyIndex, inputObject):
	#~ http://www.advancemame.it/doc-advmame#8.9.6
	if inputObject.type == 'button':
		return "joystick_button[{},{}]".format(joyIndex, inputObject.id)
	elif inputObject.type == 'axis':
		# NEED TO HANDLE JOY1 and 2 RIGHT AND DOWN !!!
		value = "1" if inputObject.value == "-1" else "0"
		# We suppose the CONTROL value is always 0 for analogue sticks
		return "joystick_digital[{},0,{},{}]".format(joyIndex, inputObject.id, value)
	elif inputObject.type == 'hat':
		# We suppose the CONTROL value is always 1 for hats, as well as up = 1,1, down = 1,0, left = 0,1 and right = 0,0
		if inputObject.name == 'up':
			return "joystick_digital[{},1,1,1]".format(joyIndex)
		elif inputObject.name == 'down':
			return "joystick_digital[{},1,1,0]".format(joyIndex)
		elif inputObject.name == 'left':
			return "joystick_digital[{},1,0,1]".format(joyIndex)
		elif inputObject.name == 'right':
			return "joystick_digital[{},1,0,0]".format(joyIndex)

def generateCombo(joyIndex, inputObject, hkInputObject):
	buttonKey = generateButton(joyIndex, inputObject)
	hotKey    = generateButton(joyIndex, hkInputObject)
	return "{} {}".format(hotKey, buttonKey)
