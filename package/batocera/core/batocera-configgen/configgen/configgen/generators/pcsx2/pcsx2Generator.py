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
from utils.logger import get_logger
import psutil

eslog = get_logger(__name__)

class Pcsx2Generator(Generator):

    def getInGameRatio(self, config, gameResolution, rom):
        if getGfxRatioFromConfig(config, gameResolution) == "16:9" or (getGfxRatioFromConfig(config, gameResolution) == "Stretch" and gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1)):
            return 16/9
        return 4/3

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        isAVX2 = checkAvx2()

        pcsx2ConfigDir = "/userdata/system/configs/PCSX2"

        # Config files
        configureReg(pcsx2ConfigDir)
        configureUI(pcsx2ConfigDir, batoceraFiles.BIOS, system.config, gameResolution)
        configureVM(pcsx2ConfigDir, system)
        configureGFX(pcsx2ConfigDir, system)
        configureAudio(pcsx2ConfigDir)

        if isAVX2:
            commandArray = ["/usr/pcsx2-avx2/bin/pcsx2", rom]
        else:
            commandArray = ["/usr/pcsx2/bin/pcsx2", rom]

        # Fullscreen
        commandArray.append("--fullscreen")

        # Fullboot
        if system.isOptSet('fullboot') and system.config['fullboot'] == '0':
            eslog.debug("Fast Boot and skip BIOS")
        else:
            commandArray.append("--fullboot")

        # Arch
        arch = "x86"
        with open('/usr/share/batocera/batocera.arch', 'r') as content_file:
            arch = content_file.read()

        env = {}

        if isAVX2:
            env["LD_LIBRARY_PATH"] = "/usr/pcsx2-avx2/lib"
        else:
            env["LD_LIBRARY_PATH"] = "/usr/pcsx2/lib"

        env["XDG_CONFIG_HOME"] = batoceraFiles.CONF
        env["SDL_GAMECONTROLLERCONFIG"] = controllersConfig.generateSdlGameControllerConfig(playersControllers)
        env["SDL_PADSORDERCONFIG"] = controllersConfig.generateSdlGameControllerPadsOrderConfig(playersControllers)

        if arch == "x86":
            env["LD_LIBRARY_PATH"]    = "/lib32"
            env["LIBGL_DRIVERS_PATH"] = "/lib32/dri"
            # hum pw 0.2 and 0.3 are hardcoded, not nice
            env["SPA_PLUGIN_DIR"]      = "/usr/lib/spa-0.2:/lib32/spa-0.2"
            env["PIPEWIRE_MODULE_DIR"] = "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"

        return Command.Command(array=commandArray, env=env)

def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9
    if "ratio" in config:
        if config["ratio"] == "16/9":
            return "16:9"
        elif config["ratio"] == "full":
            return "Stretch"
    return "4:3"

def configureReg(config_directory):
    configFileName = "{}/{}".format(config_directory, "PCSX2-reg.ini")
    if not os.path.exists(config_directory):
        os.makedirs(config_directory)
    f = open(configFileName, "w")
    f.write("DocumentsFolderMode=User\n")
    f.write("CustomDocumentsFolder=/usr/pcsx2/bin\n")
    f.write("UseDefaultSettingsFolder=enabled\n")
    f.write("SettingsFolder=/userdata/system/configs/PCSX2/inis\n")
    f.write("Install_Dir=/usr/pcsx2/bin\n")
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

    # This file looks like a .ini
    pcsx2VMConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    pcsx2VMConfig.optionxform = str

    if os.path.isfile(configFileName):
        pcsx2VMConfig.read(configFileName)

    ## [EMUCORE/GS]
    if not pcsx2VMConfig.has_section("EmuCore/GS"):
        pcsx2VMConfig.add_section("EmuCore/GS")

    # Some defaults needed on first run
    pcsx2VMConfig.set("EmuCore/GS","FrameLimitEnable", "1")
    pcsx2VMConfig.set("EmuCore/GS","SynchronousMTGS", "disabled")
    pcsx2VMConfig.set("EmuCore/GS","FrameSkipEnable", "disabled")
    pcsx2VMConfig.set("EmuCore/GS","LimitScalar", "1.00")
    pcsx2VMConfig.set("EmuCore/GS","FramerateNTSC", "59.94")
    pcsx2VMConfig.set("EmuCore/GS","FrameratePAL", "50")
    pcsx2VMConfig.set("EmuCore/GS","FramesToDraw", "2")
    pcsx2VMConfig.set("EmuCore/GS","FramesToSkip", "2")

    # Vsync
    if system.isOptSet('vsync'):
        pcsx2VMConfig.set("EmuCore/GS","VsyncEnable", system.config["vsync"])
    else:
        pcsx2VMConfig.set("EmuCore/GS","VsyncEnable", "1")

    # Vsyncs in MTGS Queue
    if system.isOptSet('VsyncQueueSize'):
        pcsx2VMConfig.set("EmuCore/GS","VsyncQueueSize", system.config['VsyncQueueSize'])
    else:
        pcsx2VMConfig.set("EmuCore/GS","VsyncQueueSize", "2")

    if not pcsx2VMConfig.has_section("EmuCore/Speedhacks"):
        pcsx2VMConfig.add_section("EmuCore/Speedhacks")
    # Any speed hacks set explicitly or as defaults are considered safe by the PCSX2 devs
    # These hacks are also gentle on lower end systems with the exception of MTVU where we check system requirements
    pcsx2VMConfig.set("EmuCore/Speedhacks", "IntcStat", "enabled")
    pcsx2VMConfig.set("EmuCore/Speedhacks", "WaitLoop", "enabled")
    micro_vu_keys = {"vuFlagHack", "vuThread", "vu1Instant"}
    micro_vu_default_keys = {"vuFlagHack"}
    # MTVU + Instant VU1 is not supported by PCSX2; and so its one or the other
    if psutil.cpu_count(logical=False) >= 3:  # 3+ physical cores recommended by PCSX2 devs for MTVU
        micro_vu_default_keys.add("vuThread")
    else:
        micro_vu_default_keys.add("vu1Instant")
    micro_vu_enabled_keys = \
        set(system.config["micro_vu"].split(",")) if system.isOptSet("micro_vu") else micro_vu_default_keys
    for key in micro_vu_enabled_keys:
        pcsx2VMConfig.set("EmuCore/Speedhacks", key, "enabled")
    for key in micro_vu_keys - micro_vu_enabled_keys:
        pcsx2VMConfig.set("EmuCore/Speedhacks", key, "disabled")

    ## [EMUCORE]
    if not pcsx2VMConfig.has_section("EmuCore"):
        pcsx2VMConfig.add_section("EmuCore")

    # Enable Multitap
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

    # Enable Cheats
    if system.isOptSet('EmuCore_EnableCheats'):
        pcsx2VMConfig.set("EmuCore","EnableCheats", system.config["EmuCore_EnableCheats"])
    else:
        pcsx2VMConfig.set("EmuCore","EnableCheats", "disabled")

    # Enabme Widescreen Patches
    if system.isOptSet('EmuCore_EnableWideScreenPatches'):
        pcsx2VMConfig.set("EmuCore","EnableWideScreenPatches", system.config["EmuCore_EnableWideScreenPatches"])
    else:
        pcsx2VMConfig.set("EmuCore","EnableWideScreenPatches", "disabled")

    # Automatic Gamefixes
    if system.isOptSet('EmuCore_EnablePatches'):
        pcsx2VMConfig.set("EmuCore","EnablePatches", system.config["EmuCore_EnablePatches"])
    else:
        pcsx2VMConfig.set("EmuCore","EnablePatches", "enabled")


    ## [EMUCORE/GAMEFIXES]
    if not pcsx2VMConfig.has_section("EmuCore/Gamefixes"):
        pcsx2VMConfig.add_section("EmuCore/Gamefixes")

    # Manual Gamefixes
    if system.isOptSet('EmuCore_ManualPatches') and system.config["EmuCore_ManualPatches"] != 'disabled':
        pcsx2VMConfig.set("EmuCore/Gamefixes",system.config["EmuCore_ManualPatches"], "enabled")
    else:
        pcsx2VMConfig.set("EmuCore/Gamefixes","VuAddSubHack",           "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","FpuCompareHack",         "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","FpuMulHack",             "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","FpuNegDivHack",          "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","XgKickHack",             "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","IPUWaitHack",            "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","EETimingHack",           "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","SkipMPEGHack",           "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","OPHFlagHack",            "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","DMABusyHack",            "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","VIFFIFOHack",            "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","VIF1StallHack",          "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","GIFFIFOHack",            "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","GoemonTlbHack",          "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","ScarfaceIbit",           "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","CrashTagTeamRacingIbit", "disabled")
        pcsx2VMConfig.set("EmuCore/Gamefixes","VU0KickstartHack",       "disabled")


    with open(configFileName, 'w') as configfile:
        pcsx2VMConfig.write(configfile)

def configureGFX(config_directory, system):
    configFileName = "{}/{}".format(config_directory + "/inis", "GS.ini")
    if not os.path.exists(config_directory):
        os.makedirs(config_directory + "/inis")

    # Create the config file if it doesn't exist
    if not os.path.exists(configFileName):
        f = open(configFileName, "w")
        f.write("osd_fontname = /usr/share/fonts/dejavu/DejaVuSans.ttf\n")
        f.close()

    # Update settings
    pcsx2GFXSettings = UnixSettings(configFileName, separator=' ')
    pcsx2GFXSettings.save("osd_fontname", "/usr/share/fonts/dejavu/DejaVuSans.ttf")
    pcsx2GFXSettings.save("osd_indicator_enabled", 1)

    if system.isOptSet('ManualHWHacks'):
        pcsx2GFXSettings.save("UserHacks", system.config["ManualHWHacks"])
    else:
        pcsx2GFXSettings.save("UserHacks", 0)

    # Internal resolution
    if system.isOptSet('internal_resolution'):
        pcsx2GFXSettings.save("upscale_multiplier", system.config["internal_resolution"])
    else:
        pcsx2GFXSettings.save("upscale_multiplier", "1")

    # ShowFPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
        pcsx2GFXSettings.save("OsdShowFPS", 1)
        pcsx2GFXSettings.save("OsdShowGSStats", 1)
        pcsx2GFXSettings.save("OsdShowCPU", 1)
        pcsx2GFXSettings.save("OsdShowSpeed", 1)
    else:
        pcsx2GFXSettings.save("OsdShowFPS", 0)
        pcsx2GFXSettings.save("OsdShowGSStats", 0)
        pcsx2GFXSettings.save("OsdShowCPU", 0)
        pcsx2GFXSettings.save("OsdShowSpeed", 0)

    # Graphical Backend
    if system.isOptSet('gfxbackend'):
        pcsx2GFXSettings.save("Renderer", system.config["gfxbackend"])
    else:
        pcsx2GFXSettings.save("Renderer", "12")

    # Skipdraw Hack
    if system.isOptSet('skipdraw'):
        pcsx2GFXSettings.save('UserHacks_SkipDraw_Start', system.config['skipdraw'])
    else:
        pcsx2GFXSettings.save('UserHacks_SkipDraw_Start', '0')

    # Align sprite Hack
    if system.isOptSet('align_sprite'):
        pcsx2GFXSettings.save('UserHacks_align_sprite_X', system.config['align_sprite'])
    else:
        pcsx2GFXSettings.save('UserHacks_align_sprite_X', '0')

    # Vsync
    if system.isOptSet('vsync'):
        pcsx2GFXSettings.save("vsync", system.config["vsync"])
    else:
        pcsx2GFXSettings.save("vsync", "1")

    # Anisotropic Filtering
    if system.isOptSet('anisotropic_filtering'):
        pcsx2GFXSettings.save("MaxAnisotropy", system.config["anisotropic_filtering"])
    else:
        pcsx2GFXSettings.save("MaxAnisotropy", "0")

    pcsx2GFXSettings.write()

def configureUI(config_directory, bios_directory, system_config, gameResolution):
    configFileName = "{}/{}".format(config_directory + "/inis", "PCSX2_ui.ini")
    if not os.path.exists(config_directory + "/inis"):
        os.makedirs(config_directory + "/inis")

    # Find the first BIOS
    bios = [ "PS2 Bios 30004R V6 Pal.bin", "scph10000.bin", "scph39001.bin", "SCPH-70004_BIOS_V12_PAL_200.BIN" ]
    biosFound = False
    for bio in bios:
        if os.path.exists(bios_directory + "/" + bio):
            biosFile = bios_directory + "/" + bio
            biosFound = True
            break;
    if not biosFound:
        raise Exception("No bios found")

    # Ratio
    resolution = getGfxRatioFromConfig(system_config, gameResolution)

    # This file looks like a .ini, but no, it miss the first section name...
    iniConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    iniConfig.optionxform = str
    if os.path.exists(configFileName):
        try:
            file = io.StringIO()
            # Fake an initial section, because pcsx2 doesn't put one
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
    # manually allow speed hacks
    iniConfig.set("NO_SECTION","EnableSpeedHacks","enabled")
    iniConfig.set("ProgramLog", "Visible",     "disabled")
    iniConfig.set("Filenames",  "BIOS",        biosFile)
    iniConfig.set("GSWindow",   "AspectRatio", resolution)
    # Zoom: 100 = fit to screen, 0 = fill the screen, anywhere between = custom
    iniConfig.set("GSWindow", "Zoom", "100")

    # Save the ini file
    if not os.path.exists(os.path.dirname(configFileName)):
        os.makedirs(os.path.dirname(configFileName))
    with open(configFileName, 'w') as configfile:
        iniConfig.write(configfile)

    # Remove the first line (the [NO_SECTION])
    with open(configFileName, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(configFileName, 'w') as fout:
        fout.writelines(data[1:])

def configureAudio(config_directory):
    configFileName = "{}/{}".format(config_directory + "/inis", "spu2-x.ini")
    if not os.path.exists(config_directory + "/inis"):
        os.makedirs(config_directory + "/inis")

    # Keep the custom files
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
