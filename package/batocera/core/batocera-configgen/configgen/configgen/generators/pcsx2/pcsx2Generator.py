#!/usr/bin/env python

from generators.Generator import Generator
import recalboxFiles
import pcsx2Controllers
import Command
import os
from settings.unixSettings import UnixSettings
import re

class Pcsx2Generator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        isAVX2 = checkAvx2()
        
        pcsx2Controllers.generateControllerConfig(system, playersControllers, rom)

        # config files
        configureReg(recalboxFiles.pcsx2ConfigDir)
        configureUI(recalboxFiles.pcsx2ConfigDir, recalboxFiles.BIOS, system.config, gameResolution)
        configureAudio(recalboxFiles.pcsx2ConfigDir)

        if isAVX2:
            commandArray = [recalboxFiles.recalboxBins['pcsx2_avx2'], rom]
        else:
            commandArray = [recalboxFiles.recalboxBins['pcsx2'], rom]

        # fullscreen
        commandArray.append("--fullscreen")

        # no gui
        commandArray.append("--nogui")

        # plugins
        real_pluginsDir = recalboxFiles.pcsx2PluginsDir
        if isAVX2:
            real_pluginsDir = recalboxFiles.pcsx2Avx2PluginsDir
        commandArray.append("--gs="   + real_pluginsDir + "/libGSdx.so")
        commandArray.append("--pad="  + real_pluginsDir + "/libonepad-legacy.so")
        commandArray.append("--cdvd=" + real_pluginsDir + "/libCDVDnull.so")
        commandArray.append("--usb="  + real_pluginsDir + "/libUSBnull-0.7.0.so")
        commandArray.append("--fw="   + real_pluginsDir + "/libFWnull-0.7.0.so")
        commandArray.append("--dev9=" + real_pluginsDir + "/libdev9null-0.5.0.so")
        commandArray.append("--spu2=" + real_pluginsDir + "/libspu2x-2.0.0.so")
        
        if 'args' in system.config and system.config['args'] is not None:
             commandArray.extend(system.config['args'])
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":recalboxFiles.CONF})

def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9
    if "ratio" in config:
        if config["ratio"] == "4/3" or (config["ratio"] == "auto" and gameResolution["width"] / float(gameResolution["height"]) < (16.0 / 9.0) - 0.1): # let a marge):
            return "4:3"
        else:
            return "16:9"
    return "4:3"

def configureReg(config_directory):
    configFileName = "{}/{}".format(config_directory, "PCSX2-reg.ini")
    if not os.path.exists(config_directory):
        os.makedirs(config_directory)
    f = open(configFileName, "w")
    f.write("DocumentsFolderMode=User\n")
    f.write("CustomDocumentsFolder=/usr/PCSX/bin\n")
    f.write("UseDefaultSettingsFolder=enabled\n")
    f.write("SettingsFolder=/recalbox/share/system/configs/PCSX2/inis\n")
    f.write("Install_Dir=/usr/PCSX/bin\n")
    f.write("RunWizard=0\n")
    f.close()

def configureUI(config_directory, bios_directory, system_config, gameResolution):
    configFileName = "{}/{}".format(config_directory + "/inis", "PCSX2_ui.ini")
    if not os.path.exists(config_directory + "/inis"):
        os.makedirs(config_directory + "/inis")

    # find the first bios
    bios = [ "PS2 Bios 30004R V6 Pal.bin", "scph10000.bin", "scph39001.bin", "SCPH-70004_BIOS_V12_PAL_200.BIN" ]
    biosFound = False
    for bio in bios:
        if os.path.exists(bios_directory + "/" + bio):
            biosFile = bios_directory + "/" + bio
            biosFound = True
            break;
    if not biosFound:
        raise Exception("No bios found")

    resolution = getGfxRatioFromConfig(system_config, gameResolution)
    if os.path.exists(configFileName):
        # existing configuration file
        pcsx2Settings = UnixSettings(configFileName)
        pcsx2Settings.save("BIOS", biosFile)
        pcsx2Settings.save("AspectRatio", resolution)
    else:
        # new configuration file
        f = open(configFileName, "w")
        f.write("[ProgramLog]\n")
        f.write("Visible=disabled\n")
        f.write("[Filenames]\n")
        f.write("BIOS=" + biosFile + "\n")
        f.write("[GSWindow]\n")
        f.write("AspectRatio=" + resolution + "\n")
        f.close()

def configureAudio(config_directory):
    configFileName = "{}/{}".format(config_directory + "/inis", "spu2-x.ini")
    if not os.path.exists(config_directory + "/inis"):
        os.makedirs(config_directory + "/inis")

    # keep the custom files
    if os.path.exists(configFileName):
        return

    f = open(configFileName, "w")
    f.write("[MIXING]\n")
    f.write("Interpolation=1\n")
    f.write("Disable_Effects=0\n")
    f.write("[OUTPUT]\n")
    f.write("Output_Module=SDLAudio\n")
    f.write("[PORTAUDIO]\n")
    f.write("HostApi=ALSA\n")
    f.write("Device=default\n")
    f.write("[SDL]\n")
    f.write("HostApi=alsa\n")
    f.close()

def checkAvx2():
    for line in open("/proc/cpuinfo").readlines():
        if re.match("^flags[\t ]*:.* avx2", line):
            return True
    return False
