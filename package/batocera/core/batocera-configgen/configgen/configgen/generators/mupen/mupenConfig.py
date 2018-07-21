#!/usr/bin/env python
import os, sys
import recalboxFiles
import settings
from settings.unixSettings import UnixSettings
import subprocess
import json

mupenSettings = UnixSettings(recalboxFiles.mupenCustom, separator=' ')

def writeMupenConfig(system, controllers, gameResolution):
	setPaths()
	writeHotKeyConfig(controllers)

	# set resolution
	mupenSettings.save('ScreenWidth', "{}".format(gameResolution["width"]))
	mupenSettings.save('ScreenHeight', "{}".format(gameResolution["height"]))
	
	#Draw or not FPS
	if system.config['showFPS'] == 'true':
		mupenSettings.save('ShowFPS', 'True')
                # show_fps is used for Video-Glide64mk2
                mupenSettings.save('show_fps', '4')
	else:
		mupenSettings.save('ShowFPS', 'False')
                mupenSettings.save('show_fps', '8')

	
def writeHotKeyConfig(controllers):
	if '1' in controllers:
		if 'hotkey' in controllers['1'].inputs:
			if 'start' in controllers['1'].inputs:
				mupenSettings.save('Joy Mapping Stop', "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['start'])))
			if 'y' in controllers['1'].inputs:	
				mupenSettings.save('Joy Mapping Save State', "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['y'])))
			if 'x' in controllers['1'].inputs:	
				mupenSettings.save('Joy Mapping Load State', "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['x'])))
			if 'pageup' in controllers['1'].inputs:	
				mupenSettings.save('Joy Mapping Screenshot', "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['pageup'])))
			if 'up' in controllers['1'].inputs:	
				mupenSettings.save('Joy Mapping Increment Slot', "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['up'])))
			if 'right' in controllers['1'].inputs:	
				mupenSettings.save('Joy Mapping Fast Forward', "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['right'])))

			
def createButtonCode(button):
	if(button.type == 'axis'):
		if button.value == '-1':
			return 'A'+button.id+'-'
		else:
			return 'A'+button.id+'+'
	if(button.type == 'button'):
		return 'B'+button.id
	if(button.type == 'hat'):
		return 'H'+button.id+'V'+button.value

def setPaths():
	mupenSettings.save('ScreenshotPath', recalboxFiles.SCREENSHOTS)
	mupenSettings.save('SaveStatePath', recalboxFiles.mupenSaves)
	mupenSettings.save('SaveSRAMPath', recalboxFiles.mupenSaves)
