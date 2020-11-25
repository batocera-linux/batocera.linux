#!/usr/bin/env python
import os, sys
import batoceraFiles
import settings
import subprocess
import json

def setMupenConfig(iniConfig, system, controllers, gameResolution):

	# hotkeys
	setHotKeyConfig(iniConfig, controllers)

	# paths
	if not iniConfig.has_section("Core"):
		iniConfig.add_section("Core")
	iniConfig.set("Core", "Version", "1.01") # version is important for the .ini creation otherwise, mupen remove the section
	iniConfig.set("Core", "ScreenshotPath", batoceraFiles.SCREENSHOTS)
	iniConfig.set("Core", "SaveStatePath",  batoceraFiles.mupenSaves)
	iniConfig.set("Core", "SaveSRAMPath",   batoceraFiles.mupenSaves)
	iniConfig.set("Core", "SharedDataPath", batoceraFiles.mupenConf)

	# disable AUDIO_SYNC while it causes issues
	if not iniConfig.has_section("Audio-SDL"):
		iniConfig.add_section("Audio-SDL")
	iniConfig.set("Audio-SDL", "AUDIO_SYNC", "False")

	# resolution
	if not iniConfig.has_section("Video-General"):
		iniConfig.add_section("Video-General")
	iniConfig.set("Video-General", "Version", "1")
	iniConfig.set("Video-General", "ScreenWidth",  gameResolution["width"])
	iniConfig.set("Video-General", "ScreenHeight", gameResolution["height"])
	iniConfig.set("Video-General", "VerticalSync", "True")
	
	# wide screen mode
	# Glide64mk2.: Adjust screen aspect for wide screen mode: -1=Game default, 0=disable. 1=enable
	# Glide64mk2.: Aspect ratio: -1=Game default, 0=Force 4:3, 1=Force 16:9, 2=Stretch, 3=Original	
	if not iniConfig.has_section("Video-Glide64mk2"):
            iniConfig.add_section("Video-Glide64mk2")
	if system.config["ratio"] == "16/9":
		iniConfig.set("Video-Glide64mk2", "adjust_aspect", "1")
		iniConfig.set("Video-Glide64mk2", "aspect", "1")        	
	else:
		iniConfig.set("Video-Glide64mk2", "adjust_aspect", "-1")
		iniConfig.set("Video-Glide64mk2", "aspect", "-1")

	# GLideN64.: Screen aspect ratio (0=stretch, 1=force 4:3, 2=force 16:9, 3=adjust)
	if not iniConfig.has_section("Video-GLideN64"):
            iniConfig.add_section("Video-GLideN64")
	if system.config["ratio"] == "16/9":
		iniConfig.set("Video-GLideN64", "AspectRatio", "2")
	else:
		iniConfig.set("Video-GLideN64", "AspectRatio", "1")

	# Rice
	if not iniConfig.has_section("Video-Rice"):
			iniConfig.add_section("Video-Rice")

	# fps
	iniConfig.set("Video-Rice", "Version", "1")
	iniConfig.set("Video-Glide64mk2", "Version", "1")	
	if system.config['showFPS'] == 'true':
		iniConfig.set("Video-Rice",      "ShowFPS",  "True")
		iniConfig.set("Video-Glide64mk2", "show_fps", "4")
	else:
		iniConfig.set("Video-Rice",       "ShowFPS",  "False")
		iniConfig.set("Video-Glide64mk2", "show_fps", "8")

        # custom : allow the user to configure directly mupen64plus.cfg via batocera.conf via lines like : n64.mupen64plus.section.option=value
        for user_config in system.config:
                if user_config[:12] == "mupen64plus.":
                        section_option = user_config[12:]
                        section_option_splitter = section_option.find(".")
                        custom_section = section_option[:section_option_splitter]
                        custom_option = section_option[section_option_splitter+1:]
                        if not iniConfig.has_section(custom_section):
                                iniConfig.add_section(custom_section)
                        iniConfig.set(custom_section, custom_option, system.config[user_config])
	
def setHotKeyConfig(iniConfig, controllers):
	if not iniConfig.has_section("CoreEvents"):
			iniConfig.add_section("CoreEvents")
	iniConfig.set("CoreEvents", "Version", "1")
        
	if '1' in controllers:
		if 'hotkey' in controllers['1'].inputs:
			if 'start' in controllers['1'].inputs:
				iniConfig.set("CoreEvents", "Joy Mapping Stop", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['start'])))
			if 'y' in controllers['1'].inputs:	
				iniConfig.set("CoreEvents", "Joy Mapping Save State", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['y'])))
			if 'x' in controllers['1'].inputs:	
				iniConfig.set("CoreEvents", "Joy Mapping Load State", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['x'])))
			if 'pageup' in controllers['1'].inputs:	
				iniConfig.set("CoreEvents", "Joy Mapping Screenshot", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['pageup'])))
			if 'up' in controllers['1'].inputs:	
				iniConfig.set("CoreEvents", "Joy Mapping Increment Slot", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['up'])))
			if 'right' in controllers['1'].inputs:	
				iniConfig.set("CoreEvents", "Joy Mapping Fast Forward", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['right'])))
                        if 'a' in controllers['1'].inputs:	
				iniConfig.set("CoreEvents", "Joy Mapping Reset", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['a'])))
                        if 'b' in controllers['1'].inputs:	
				#iniConfig.set("CoreEvents", "Joy Mapping Pause", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['b'])))
                                iniConfig.set("CoreEvents", "Joy Mapping Pause", "")

			
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
