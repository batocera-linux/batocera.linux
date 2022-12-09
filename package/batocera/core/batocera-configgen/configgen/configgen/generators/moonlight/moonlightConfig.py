#!/usr/bin/env python

import batoceraFiles
import os
import shutil
from Emulator import Emulator
from settings.unixSettings import UnixSettings

def generateMoonlightConfig(system):

    moonlightStagingConfigFile = batoceraFiles.moonlightStagingConfigFile
    if not os.path.exists(batoceraFiles.moonlightCustom + '/staging'):
        os.makedirs(batoceraFiles.moonlightCustom + '/staging')

    # If user made config file exists, copy to staging directory for use
    if os.path.exists(batoceraFiles.moonlightConfigFile):
        shutil.copy(batoceraFiles.moonlightConfigFile, batoceraFiles.moonlightStagingConfigFile)
    else:
        # truncate existing config and create new one
        f = open(moonlightStagingConfigFile, "w").close()

        moonlightConfig = UnixSettings(moonlightStagingConfigFile, separator=' ')

        # resolution
        if system.isOptSet('moonlight_resolution'):
            if system.config["moonlight_resolution"] == "0":
                moonlightConfig.save('width', '1280')
                moonlightConfig.save('height', '720')
            elif system.config["moonlight_resolution"] == "1":
                moonlightConfig.save('width', '1920')
                moonlightConfig.save('height', '1080')
            elif system.config["moonlight_resolution"] == "2":
                moonlightConfig.save('width', '3840')
                moonlightConfig.save('height', '2160')
            else:
                moonlightConfig.save('width', '1280')
                moonlightConfig.save('height', '720')
        else:
            moonlightConfig.save('width', '1280')
            moonlightConfig.save('height', '720')

        # framerate
        if system.isOptSet('moonlight_framerate'):
            if system.config["moonlight_framerate"] == "0":
                moonlightConfig.save('fps', '30')
            elif system.config["moonlight_framerate"] == "1":
                moonlightConfig.save('fps', '60')
            elif system.config["moonlight_framerate"] == "2":
                moonlightConfig.save('fps', '120')
            else:
                moonlightConfig.save('fps', '30')
        else:
            moonlightConfig.save('fps', '30')

        # bitrate
        if system.isOptSet('moonlight_bitrate'):
            if system.config["moonlight_bitrate"] == "0":
                moonlightConfig.save('bitrate', '5000')
            elif system.config["moonlight_bitrate"] == "1":
                moonlightConfig.save('bitrate', '10000')
            elif system.config["moonlight_bitrate"] == "2":
                moonlightConfig.save('bitrate', '20000')
            elif system.config["moonlight_bitrate"] == "3":
                moonlightConfig.save('bitrate', '50000')
            else:
                moonlightConfig.save('bitrate', '-1') #-1 sets Moonlight default
        else:
            moonlightConfig.save('bitrate', '-1') #-1 sets Moonlight default

        # codec
        if system.isOptSet('moonlight_codec'):
            if system.config["moonlight_codec"] == "0":
                moonlightConfig.save('codec', 'h264')
            elif system.config["moonlight_codec"] == "1":
                moonlightConfig.save('codec', 'h265')
            else:
                moonlightConfig.save('codec', 'auto')
        else:
            moonlightConfig.save('codec', 'auto')

        # sops (Streaming Optimal Playable Settings)
        if system.isOptSet('moonlight_sops'):
            if system.config["moonlight_sops"] == "0":
                moonlightConfig.save('sops', 'true')
            elif system.config["moonlight_sops"] == "1":
                moonlightConfig.save('sops', 'false')
            else:
                moonlightConfig.save('sops', 'true')
        else:
            moonlightConfig.save('sops', 'true')

        # quit remote app on exit
        if system.isOptSet('moonlight_quitapp'):
            if system.config["moonlight_quitapp"] == "0":
                moonlightConfig.save('quitappafter', 'true')
            else:
                moonlightConfig.save('quitappafter', 'false')
        else:
            moonlightConfig.save('quitappafter', 'false')

        # av decoder
        if system.isOptSet('moonlight_avdecoder'):
            if system.config["moonlight_avdecoder"] == "sdl": 
                moonlightConfig.save('platform', 'sdl')
            else:
                moonlightConfig.save('platform', 'auto')
        else:
            moonlightConfig.save('platform', 'auto')

        ## Directory to store encryption keys
        moonlightConfig.save('keydir', batoceraFiles.moonlightCustom + '/keydir')

        moonlightConfig.write()
