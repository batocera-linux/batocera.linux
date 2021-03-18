#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import os
from settings.unixSettings import UnixSettings
import re
import configparser
import io
import controllersConfig

class Pcsx2Generator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        isAVX2 = checkAvx2()
        sseLib = checkSseLib(isAVX2)

        # config files
        configureReg(batoceraFiles.pcsx2ConfigDir)
        configureUI(batoceraFiles.pcsx2ConfigDir, batoceraFiles.BIOS, system.config, gameResolution)
        configureVM(batoceraFiles.pcsx2ConfigDir, system)
        configureGFX(batoceraFiles.pcsx2ConfigDir, system)
        configureAudio(batoceraFiles.pcsx2ConfigDir)

        if isAVX2:
            commandArray = [batoceraFiles.batoceraBins['pcsx2_avx2'], rom]
        else:
            commandArray = [batoceraFiles.batoceraBins['pcsx2'], rom]

        # fullscreen
        commandArray.append("--fullscreen")

        # no gui
        commandArray.append("--nogui")

        # fullboot
        if system.isOptSet('fullboot') and system.getOptBoolean('fullboot') == True:
            commandArray.append("--fullboot")

        # plugins
        real_pluginsDir = batoceraFiles.pcsx2PluginsDir
        if isAVX2:
            real_pluginsDir = batoceraFiles.pcsx2Avx2PluginsDir
        commandArray.append("--gs="   + real_pluginsDir + "/" + sseLib)
        
        # arch
        arch = "x86"
        with open('/usr/share/batocera/batocera.arch', 'r') as content_file:
            arch = content_file.read()

        env = {}
        env["XDG_CONFIG_HOME"] = batoceraFiles.CONF
        env["SDL_GAMECONTROLLERCONFIG"] = controllersConfig.generateSdlGameControllerConfig(playersControllers)

        env["SDL_PADSORDERCONFIG"] = controllersConfig.generateSdlGameControllerPadsOrderConfig(playersControllers)

        if arch == "x86":
            env["LD_LIBRARY_PATH"]    = "/lib32"
            env["LIBGL_DRIVERS_PATH"] = "/lib32/dri"

        return Command.Command(array=commandArray, env=env)

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
    f.write("SettingsFolder=/userdata/system/configs/PCSX2/inis\n")
    f.write("Install_Dir=/usr/PCSX/bin\n")
    f.write("RunWizard=0\n")
    f.close()

def configureVM(config_directory, system):

    configFileName = "{}/{}".format(config_directory + "/inis", "PCSX2_vm.ini")
    
    if not os.path.exists(config_directory + "/inis"):
        os.makedirs(config_directory + "/inis")
        
    if not os.path.isfile(configFileName):
        f = open(configFileName, "w")
        f.write("[EmuCore]\n")
        f.close()
    
    # this file looks like a .ini
    pcsx2VMConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    pcsx2VMConfig.optionxform = str   
    
    if os.path.isfile(configFileName):  
        pcsx2VMConfig.read(configFileName)
    
    if not pcsx2VMConfig.has_section("EmuCore/GS"):
        #Some defaults needed on first run 
        pcsx2VMConfig.add_section("EmuCore/GS")
        pcsx2VMConfig.set("EmuCore/GS","VsyncQueueSize", "2")
        pcsx2VMConfig.set("EmuCore/GS","FrameLimitEnable", "1")
        pcsx2VMConfig.set("EmuCore/GS","SynchronousMTGS", "disabled")
        pcsx2VMConfig.set("EmuCore/GS","FrameSkipEnable", "disabled")
        pcsx2VMConfig.set("EmuCore/GS","LimitScalar", "1.00")
        pcsx2VMConfig.set("EmuCore/GS","FramerateNTSC", "59.94")
        pcsx2VMConfig.set("EmuCore/GS","FrameratePAL", "50")
        pcsx2VMConfig.set("EmuCore/GS","FramesToDraw", "2")
        pcsx2VMConfig.set("EmuCore/GS","FramesToSkip", "2")

    if not pcsx2VMConfig.has_section("EmuCore"):
        pcsx2VMConfig.add_section("EmuCore")

    # enable multitap
    if system.isOptSet('multitap') and system.config['multitap'] != 'disabled':
        if system.config['multitap'] == 'port1':
            pcsx2VMConfig.set("EmuCore","MultitapPort0_Enabled", "enabled")
            pcsx2VMConfig.set("EmuCore","MultitapPort1_Enabled", "disabled")
        elif system.config['multitap'] == 'port2':
            pcsx2VMConfig.set("EmuCore","MultitapPort0_Enabled", "disabled")
            pcsx2VMConfig.set("EmuCore","MultitapPort1_Enabled", "enabled")
        elif system.config['multitap'] == 'port12':
            pcsx2VMConfig.set("EmuCore","MultitapPort0_Enabled", "enabled")
            pcsx2VMConfig.set("EmuCore","MultitapPort1_Enabled", "enabled")
    else:
        pcsx2VMConfig.set("EmuCore","MultitapPort0_Enabled", "disabled")
        pcsx2VMConfig.set("EmuCore","MultitapPort1_Enabled", "disabled")

    if system.isOptSet('vsync'):
        pcsx2VMConfig.set("EmuCore/GS","VsyncEnable", system.config["vsync"])
    else:
        pcsx2VMConfig.set("EmuCore/GS","VsyncEnable", "1")    

    with open(configFileName, 'w') as configfile:
        pcsx2VMConfig.write(configfile)
        
        
def configureGFX(config_directory, system):
    configFileName = "{}/{}".format(config_directory + "/inis", "GSdx.ini")
    if not os.path.exists(config_directory):
        os.makedirs(config_directory + "/inis")
    
    #create the config file if it doesn't exist
    if not os.path.exists(configFileName):
        f = open(configFileName, "w")
        f.write("osd_fontname = /usr/share/fonts/dejavu/DejaVuSans.ttf\n")
        f.close()
        
    
    # Update settings
    pcsx2GFXSettings = UnixSettings(configFileName, separator=' ')
    pcsx2GFXSettings.save("osd_fontname", "/usr/share/fonts/dejavu/DejaVuSans.ttf")
    pcsx2GFXSettings.save("osd_indicator_enabled", 1)
    pcsx2GFXSettings.save("UserHacks", 1)
    #showFPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
        pcsx2GFXSettings.save("osd_monitor_enabled", 1)
    else:
        pcsx2GFXSettings.save("osd_monitor_enabled", 0)
    #internal resolution
    if system.isOptSet('internalresolution'):
        pcsx2GFXSettings.save("upscale_multiplier", system.config["internalresolution"])
    else:
        pcsx2GFXSettings.save("upscale_multiplier", "1")
    #skipdraw
    if system.isOptSet('skipdraw'):
        pcsx2GFXSettings.save('UserHacks_SkipDraw', system.config['skipdraw'])
    else:
        pcsx2GFXSettings.save('UserHacks_SkipDraw', '0')
    #align sprite
    if system.isOptSet('align_sprite'):
        pcsx2GFXSettings.save('UserHacks_align_sprite_X', system.config['align_sprite'])
    else:
        pcsx2GFXSettings.save('UserHacks_align_sprite_X', '0')
        
    if system.isOptSet('vsync'):
        pcsx2GFXSettings.save("vsync", system.config["vsync"])
    else:
        pcsx2GFXSettings.save("vsync", "1")

    if system.isOptSet('anisotropic_filtering'):
        pcsx2GFXSettings.save("MaxAnisotropy", system.config["anisotropic_filtering"])
    else:
        pcsx2GFXSettings.save("MaxAnisotropy", "0")    

    pcsx2GFXSettings.write()

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

    # this file looks like a .ini, but no, it miss the first section name...
    iniConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    iniConfig.optionxform = str
    if os.path.exists(configFileName):
        try:
            file = io.StringIO()
            # fake an initial section, because pcsx2 doesn't put one
            file.write('[NO_SECTION]\n')
            file.write(io.open(configFileName, encoding='utf_8_sig').read())
            file.seek(0, os.SEEK_SET)
            iniConfig.readfp(file)
        except:
            pass

    for section in [ "ProgramLog", "Filenames", "GSWindow", "NO_SECTION" ]:
        if not iniConfig.has_section(section):
            iniConfig.add_section(section)
    
    iniConfig.set("NO_SECTION","EnablePresets","disabled")
    iniConfig.set("ProgramLog", "Visible",     "disabled")
    iniConfig.set("Filenames",  "BIOS",        biosFile)
    iniConfig.set("GSWindow",   "AspectRatio", resolution)

    # save the ini file
    if not os.path.exists(os.path.dirname(configFileName)):
        os.makedirs(os.path.dirname(configFileName))
    with open(configFileName, 'w') as configfile:
        iniConfig.write(configfile)

    # remove the first line (the [NO_SECTION])
    with open(configFileName, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(configFileName, 'w') as fout:
        fout.writelines(data[1:])

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

def checkSseLib(isAVX2):
    if not isAVX2:
        for line in open("/proc/cpuinfo").readlines():
            if re.match("^flags[\t ]*:.* sse4_1", line) and re.match("^flags[\t ]*:.* sse4_2", line):
                return "libGSdx-SSE4.so"
    return "libGSdx.so"
