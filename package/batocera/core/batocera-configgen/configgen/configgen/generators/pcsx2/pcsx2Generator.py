#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import os
from settings.unixSettings import UnixSettings
from utils.logger import get_logger
import re
import configparser
import io
import controllersConfig
import json
import httplib2
import time

eslog = get_logger(__name__)

class Pcsx2Generator(Generator):

    def getInGameRatio(self, config, gameResolution, rom):
        if getGfxRatioFromConfig(config, gameResolution) == "16:9" or (getGfxRatioFromConfig(config, gameResolution) == "Stretch" and gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1)):
            return 16/9
        return 4/3

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        isAVX2 = checkAvx2()

        pcsx2ConfigDir = "/userdata/system/configs/PCSX2"

        # Remove older config files if present
        inisDir = os.path.join(pcsx2ConfigDir, "inis")
        files_to_remove = ["PCSX2_ui.ini", "PCSX2_vm.ini", "GS.ini"]
        for filename in files_to_remove:
            file_path = os.path.join(inisDir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Config files
        configureReg(pcsx2ConfigDir)
        configureINI(pcsx2ConfigDir, batoceraFiles.BIOS, system, playersControllers)
        configureAudio(pcsx2ConfigDir)

        # write our own game_controller_db.txt file before launching the game
        dbfile = pcsx2ConfigDir + "/game_controller_db.txt"
        controllersConfig.writeSDLGameDBAllControllers(playersControllers, dbfile)
        
        commandArray = ["/usr/pcsx2-avx2/bin/pcsx2-qt"] if isAVX2 and rom == "config" else \
              ["/usr/pcsx2-avx2/bin/pcsx2-qt", "-nogui", rom] if isAVX2 else \
              ["/usr/pcsx2/bin/pcsx2-qt"] if rom == "config" else \
              ["/usr/pcsx2/bin/pcsx2-qt", "-nogui", rom]
        
        return Command.Command(
            array=commandArray,
            env={ "XDG_CONFIG_HOME":batoceraFiles.CONF,
            "QT_QPA_PLATFORM":"xcb",
            "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

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

def configureINI(config_directory, bios_directory, system, controllers):
    configFileName = "{}/{}".format(config_directory + "/inis", "PCSX2.ini")

    if not os.path.exists(config_directory + "/inis"):
        os.makedirs(config_directory + "/inis")

    if not os.path.isfile(configFileName):
        f = open(configFileName, "w")
        f.write("[UI]\n")
        f.close()
    
    pcsx2INIConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    pcsx2INIConfig.optionxform = str

    if os.path.isfile(configFileName):
        pcsx2INIConfig.read(configFileName)

    ## [UI]
    if not pcsx2INIConfig.has_section("UI"):
        pcsx2INIConfig.add_section("UI")
    
    # set the settings we want always enabled
    pcsx2INIConfig.set("UI", "SettingsVersion", "1")
    pcsx2INIConfig.set("UI", "InhibitScreensaver", "true")
    pcsx2INIConfig.set("UI", "ConfirmShutdown", "false")
    pcsx2INIConfig.set("UI", "StartPaused", "false")
    pcsx2INIConfig.set("UI", "PauseOnFocusLoss", "false")
    pcsx2INIConfig.set("UI", "StartFullscreen", "true")
    pcsx2INIConfig.set("UI", "HideMouseCursor", "true")
    pcsx2INIConfig.set("UI", "RenderToSeparateWindow", "false")
    pcsx2INIConfig.set("UI", "HideMainWindowWhenRunning", "true")

    ## [Folders]
    if not pcsx2INIConfig.has_section("Folders"):
        pcsx2INIConfig.add_section("Folders")
    
    # set the folders we want
    pcsx2INIConfig.set("Folders", "Bios", "../../../bios")
    pcsx2INIConfig.set("Folders", "Snapshots", "../../../screenshots")
    pcsx2INIConfig.set("Folders", "SaveStates", "../../../saves/ps2/pcsx2/sstates")
    pcsx2INIConfig.set("Folders", "MemoryCards", "../../../saves/ps2/pcsx2")
    pcsx2INIConfig.set("Folders", "Logs", "../../logs")
    pcsx2INIConfig.set("Folders", "Cheats", "../../../cheats/ps2")
    pcsx2INIConfig.set("Folders", "CheatsWS", "../../../cheats/ps2/cheats_ws")
    pcsx2INIConfig.set("Folders", "CheatsNI", "../../../cheats/ps2/cheats_ni")
    pcsx2INIConfig.set("Folders", "Cache", "../../cache/ps2")
    pcsx2INIConfig.set("Folders", "Textures", "textures")
    pcsx2INIConfig.set("Folders", "InputProfiles", "inputprofiles")
    pcsx2INIConfig.set("Folders", "Videos", "../../../saves/ps2/pcsx2/videos")

    ## [EmuCore]
    if not pcsx2INIConfig.has_section("EmuCore"):
        pcsx2INIConfig.add_section("EmuCore")

    # set the settings we want always enabled
    pcsx2INIConfig.set("EmuCore", "EnableDiscordPresence", "false")

    # Fastboot
    if system.isOptSet('pcsx2_fastboot') and system.config['pcsx2_fastboot'] == '0':
        pcsx2INIConfig.set("EmuCore", "EnableFastBoot", "true")
    else:
        pcsx2INIConfig.set("EmuCore", "EnableFastBoot", "false")
    # Cheats
    if system.isOptSet('pcsx2_cheats'):
        pcsx2INIConfig.set("EmuCore", "EnableCheats", system.config['pcsx2_cheats'])
    else:
        pcsx2INIConfig.set("EmuCore", "EnableCheats", "false")
    # Widescreen Patches
    if system.isOptSet('pcsx2_EnableWideScreenPatches'):
        pcsx2INIConfig.set("EmuCore", "EnableWideScreenPatches", system.config["pcsx2_EnableWideScreenPatches"])
    else:
        pcsx2INIConfig.set("EmuCore", "EnableWideScreenPatches", "false")
    # No-interlacing Patches
    if system.isOptSet('pcsx2_interlacing_patches'):
        pcsx2INIConfig.set("EmuCore", "EnableNoInterlacingPatches", system.config["pcsx2_interlacing_patches"])
    else:
        pcsx2INIConfig.set("EmuCore", "EnableNoInterlacingPatches", "false")

    ## [Achievements]
    if not pcsx2INIConfig.has_section("Achievements"):
        pcsx2INIConfig.add_section("Achievements")
    pcsx2INIConfig.set("Achievements", "Enabled", "false")
    if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
        headers   = {"Content-type": "text/plain"}
        login_url = "https://retroachievements.org/"
        username  = system.config.get('retroachievements.username', "")
        password  = system.config.get('retroachievements.password', "")
        hardcore  = system.config.get('retroachievements.hardcore', "")
        indicator = system.config.get('retroachievements.challenge_indicators', "")
        presence  = system.config.get('retroachievements.richpresence', "")
        leaderbd  = system.config.get('retroachievements.leaderboards', "")
        login_cmd = f"dorequest.php?r=login&u={username}&p={password}"
        try:
                cnx = httplib2.Http()
        except:
                eslog.error("ERROR: Unable to connect to " + login_url)
        try:
                res, rout = cnx.request(login_url + login_cmd, method="GET", body=None, headers=headers)
                if (res.status != 200):
                    eslog.warning(f"ERROR: RetroAchievements.org responded with #{res.status} [{res.reason}] {rout}")
                    settings.set("Cheevos", "Enabled",  "false")
                else:
                    parsedout = json.loads(rout.decode('utf-8'))
                    if not parsedout['Success']:
                        eslog.warning(f"ERROR: RetroAchievements login failed with ({str(parsedout)})")
                    token = parsedout['Token']
                    pcsx2INIConfig.set("Achievements", "Enabled", "true")
                    pcsx2INIConfig.set("Achievements", "Username", username)
                    pcsx2INIConfig.set("Achievements", "Token", token)
                    pcsx2INIConfig.set("Achievements", "LoginTimestamp", str(int(time.time())))
                    if hardcore == '1':
                        pcsx2INIConfig.set("Achievements", "ChallengeMode", "true")
                    else:
                        pcsx2INIConfig.set("Achievements", "ChallengeMode", "false")
                    if indicator == '1':
                        pcsx2INIConfig.set("Achievements", "PrimedIndicators", "true")
                    else:
                        pcsx2INIConfig.set("Achievements", "PrimedIndicators", "false")
                    if presence == '1':
                        pcsx2INIConfig.set("Achievements", "RichPresence", "true")
                    else:
                        pcsx2INIConfig.set("Achievements", "RichPresence", "false")
                    if leaderbd == '1':
                        pcsx2INIConfig.set("Achievements", "Leaderboards", "true")
                    else:
                        pcsx2INIConfig.set("Achievements", "Leaderboards", "false")
        except:
                eslog.error("ERROR: setting RetroAchievements parameters")
    # set other settings
    pcsx2INIConfig.set("Achievements", "TestMode", "false")
    pcsx2INIConfig.set("Achievements", "UnofficialTestMode", "false")
    pcsx2INIConfig.set("Achievements", "Notifications", "true")
    pcsx2INIConfig.set("Achievements", "SoundEffects", "true")

    ## [Filenames]
    if not pcsx2INIConfig.has_section("Filenames"):
        pcsx2INIConfig.add_section("Filenames")
    
    # Find the first BIOS
    bios = [ "PS2 Bios 30004R V6 Pal.bin", "scph10000.bin", "scph39001.bin", "SCPH-70004_BIOS_V12_PAL_200.BIN" ]
    biosFound = False
    for bio in bios:
        if os.path.exists(bios_directory + "/" + bio):
            biosFile = bio
            biosFound = True
            break;
    if not biosFound:
        raise Exception("No bios found")
    
    pcsx2INIConfig.set("Filenames", "BIOS", biosFile)

    ## [EMUCORE/GS]
    if not pcsx2INIConfig.has_section("EmuCore/GS"):
        pcsx2INIConfig.add_section("EmuCore/GS")
    
    # Renderer
    if system.isOptSet('pcsx2_gfxbackend'):
        pcsx2INIConfig.set("EmuCore/GS", "Renderer", system.config["pcsx2_gfxbackend"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "Renderer", "12")
    # Ratio
    if system.isOptSet('pcsx2_ratio'):
        pcsx2INIConfig.set("EmuCore/GS", "AspectRatio", system.config["pcsx2_ratio"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "AspectRatio", "Auto 4:3/3:2")
    # Vsync
    if system.isOptSet('pcsx2_vsync'):
        pcsx2INIConfig.set("EmuCore/GS","VsyncEnable", system.config["pcsx2_vsync"])
    else:
        pcsx2INIConfig.set("EmuCore/GS","VsyncEnable", "0")
    # Resolution
    if system.isOptSet('pcsx2_resolution'):
        pcsx2INIConfig.set("EmuCore/GS", "upscale_multiplier", system.config["pcsx2_resolution"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "upscale_multiplier", "1")
    # FXAA
    if system.isOptSet('pcsx2_fxaa'):
        pcsx2INIConfig.set("EmuCore/GS", "fxaa", system.config["pcsx2_fxaa"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "fxaa", "false")
    # FMV Ratio
    if system.isOptSet('pcsx2_fmv_ratio'):
        pcsx2INIConfig.set("EmuCore/GS", "FMVAspectRatioSwitch", system.config["pcsx2_fmv_ratio"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "FMVAspectRatioSwitch", "Auto 4:3/3:2")
    # Mipmapping
    if system.isOptSet('pcsx2_mipmapping'):
        pcsx2INIConfig.set("EmuCore/GS", "mipmap_hw", system.config["pcsx2_mipmapping"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "mipmap_hw", "-1")
    # Trilinear Filtering
    if system.isOptSet('pcsx2_trilinear_filtering'):
        pcsx2INIConfig.set("EmuCore/GS", "TriFilter", system.config["pcsx2_trilinear_filtering"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "TriFilter", "-1")
    # Anisotropic Filtering
    if system.isOptSet('pcsx2_anisotropic_filtering'):
        pcsx2INIConfig.set("EmuCore/GS", "MaxAnisotropy", system.config["pcsx2_anisotropic_filtering"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "MaxAnisotropy", "0")
    # Dithering
    if system.isOptSet('pcsx2_dithering'):
        pcsx2INIConfig.set("EmuCore/GS", "dithering_ps2", system.config["pcsx2_dithering"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "dithering_ps2", "2")
    # Texture Preloading
    if system.isOptSet('pcsx2_texture_loading'):
        pcsx2INIConfig.set("EmuCore/GS", "texture_preloading", system.config["pcsx2_texture_loading"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "texture_preloading", "2")
    # Deinterlacing
    if system.isOptSet('pcsx2_deinterlacing'):
        pcsx2INIConfig.set("EmuCore/GS", "deinterlace_mode", system.config["pcsx2_deinterlacing"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "deinterlace_mode", "0")
    # Anti-Blur
    if system.isOptSet('pcsx2_blur'):
        pcsx2INIConfig.set("EmuCore/GS", "pcrtc_antiblur", system.config["pcsx2_blur"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "pcrtc_antiblur", "true")
    # Integer Scaling
    if system.isOptSet('pcsx2_scaling'):
        pcsx2INIConfig.set("EmuCore/GS", "IntegerScaling", system.config["pcsx2_scaling"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "IntegerScaling", "false")
    # Blending Accuracy
    if system.isOptSet('pcsx2_blending'):
        pcsx2INIConfig.set("EmuCore/GS", "accurate_blending_unit", system.config["pcsx2_blending"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "accurate_blending_unit", "1")
    # Texture Filtering
    if system.isOptSet('pcsx2_texture_filtering'):
        pcsx2INIConfig.set("EmuCore/GS", "filter", system.config["pcsx2_texture_filtering"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "filter", "2")
    # Bilinear Filtering
    if system.isOptSet('pcsx2_bilinear_filtering'):
        pcsx2INIConfig.set("EmuCore/GS", "linear_present_mode", system.config["pcsx2_bilinear_filtering"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "linear_present_mode", "1")
        
    ## [InputSources]
    if not pcsx2INIConfig.has_section("InputSources"):
        pcsx2INIConfig.add_section("InputSources")
    
    pcsx2INIConfig.set("InputSources", "Keyboard", "true")
    pcsx2INIConfig.set("InputSources", "Mouse", "true")
    pcsx2INIConfig.set("InputSources", "SDL", "true")
    pcsx2INIConfig.set("InputSources", "SDLControllerEnhancedMode", "true")
    
    ## [Hotkeys]
    if not pcsx2INIConfig.has_section("Hotkeys"):
        pcsx2INIConfig.add_section("Hotkeys")
    
    pcsx2INIConfig.set("Hotkeys", "ToggleFullscreen", "Keyboard/Alt & Keyboard/Return")
    pcsx2INIConfig.set("Hotkeys", "CycleAspectRatio", "Keyboard/F6")
    pcsx2INIConfig.set("Hotkeys", "CycleInterlaceMode", "Keyboard/F5")
    pcsx2INIConfig.set("Hotkeys", "CycleMipmapMode", "Keyboard/Insert")
    pcsx2INIConfig.set("Hotkeys", "GSDumpMultiFrame", "Keyboard/Control & Keyboard/Shift & Keyboard/F8")
    pcsx2INIConfig.set("Hotkeys", "Screenshot", "Keyboard/F8")
    pcsx2INIConfig.set("Hotkeys", "GSDumpSingleFrame", "Keyboard/Shift & Keyboard/F8")
    pcsx2INIConfig.set("Hotkeys", "ToggleSoftwareRendering", "Keyboard/F9")
    pcsx2INIConfig.set("Hotkeys", "ZoomIn", "Keyboard/Control & Keyboard/Plus")
    pcsx2INIConfig.set("Hotkeys", "ZoomOut", "Keyboard/Control & Keyboard/Minus")
    pcsx2INIConfig.set("Hotkeys", "InputRecToggleMode", "Keyboard/Shift & Keyboard/R")
    pcsx2INIConfig.set("Hotkeys", "LoadStateFromSlot", "Keyboard/F3")
    pcsx2INIConfig.set("Hotkeys", "SaveStateToSlot", "Keyboard/F1")
    pcsx2INIConfig.set("Hotkeys", "NextSaveStateSlot", "Keyboard/F2")
    pcsx2INIConfig.set("Hotkeys", "PreviousSaveStateSlot", "Keyboard/Shift & Keyboard/F2")
    pcsx2INIConfig.set("Hotkeys", "OpenPauseMenu", "Keyboard/Escape")
    pcsx2INIConfig.set("Hotkeys", "ToggleFrameLimit", "Keyboard/F4")
    pcsx2INIConfig.set("Hotkeys", "TogglePause", "Keyboard/Space")
    pcsx2INIConfig.set("Hotkeys", "ToggleSlowMotion", "Keyboard/Shift & Keyboard/Backtab")
    pcsx2INIConfig.set("Hotkeys", "ToggleTurbo", "Keyboard/Tab")
    pcsx2INIConfig.set("Hotkeys", "HoldTurbo", "Keyboard/Period")

    ## [Pad]
    if not pcsx2INIConfig.has_section("Pad"):
        pcsx2INIConfig.add_section("Pad")
    
    pcsx2INIConfig.set("Pad", "MultitapPort1", "false")
    pcsx2INIConfig.set("Pad", "MultitapPort2", "false")

    # Now add Controllers
    nplayer = 1
    for controller, pad in sorted(controllers.items()):
        if nplayer <= 8:
            # automatically add the multi-tap
            if nplayer >> 2:
                pcsx2INIConfig.set("Pad", "MultitapPort1", "true")
            if nplayer >> 4:
                pcsx2INIConfig.set("Pad", "MultitapPort2", "true")
            pad_num = "Pad{}".format(nplayer)
            sdl_num = "SDL-" + "{}".format(nplayer - 1)
            if not pcsx2INIConfig.has_section(pad_num):
                pcsx2INIConfig.add_section(pad_num)
            
            pcsx2INIConfig.set(pad_num, "Type", "DualShock2")
            pcsx2INIConfig.set(pad_num, "InvertL", "0")
            pcsx2INIConfig.set(pad_num, "InvertR", "0")
            pcsx2INIConfig.set(pad_num, "Deadzone", "0")
            pcsx2INIConfig.set(pad_num, "AxisScale", "1.33")
            pcsx2INIConfig.set(pad_num, "TriggerDeadzone", "0")
            pcsx2INIConfig.set(pad_num, "TriggerScale", "1")
            pcsx2INIConfig.set(pad_num, "LargeMotorScale", "1")
            pcsx2INIConfig.set(pad_num, "SmallMotorScale", "1")
            pcsx2INIConfig.set(pad_num, "ButtonDeadzone", "0")
            pcsx2INIConfig.set(pad_num, "PressureModifier", "0.5")
            pcsx2INIConfig.set(pad_num, "Up", sdl_num + "/DPadUp")
            pcsx2INIConfig.set(pad_num, "Right", sdl_num + "/DPadRight")
            pcsx2INIConfig.set(pad_num, "Down", sdl_num + "/DPadDown")
            pcsx2INIConfig.set(pad_num, "Left", sdl_num + "/DPadLeft")
            pcsx2INIConfig.set(pad_num, "Triangle", sdl_num + "/Y")
            pcsx2INIConfig.set(pad_num, "Circle", sdl_num + "/B")
            pcsx2INIConfig.set(pad_num, "Cross", sdl_num + "/A")
            pcsx2INIConfig.set(pad_num, "Square", sdl_num + "/X")
            pcsx2INIConfig.set(pad_num, "Select", sdl_num + "/Back")
            pcsx2INIConfig.set(pad_num, "Start", sdl_num + "/Start")
            pcsx2INIConfig.set(pad_num, "L1", sdl_num + "/LeftShoulder")
            pcsx2INIConfig.set(pad_num, "L2", sdl_num + "/+LeftTrigger")
            pcsx2INIConfig.set(pad_num, "R1", sdl_num + "/RightShoulder")
            pcsx2INIConfig.set(pad_num, "R2", sdl_num + "/+RightTrigger")
            pcsx2INIConfig.set(pad_num, "L3", sdl_num + "/LeftStick")
            pcsx2INIConfig.set(pad_num, "R3", sdl_num + "/RightStick")
            pcsx2INIConfig.set(pad_num, "LUp", sdl_num + "/-LeftY")
            pcsx2INIConfig.set(pad_num, "LRight", sdl_num + "/+LeftX")
            pcsx2INIConfig.set(pad_num, "LDown", sdl_num + "/+LeftY")
            pcsx2INIConfig.set(pad_num, "LLeft", sdl_num + "/-LeftX")
            pcsx2INIConfig.set(pad_num, "RUp", sdl_num + "/-RightY")
            pcsx2INIConfig.set(pad_num, "RRight", sdl_num + "/+RightX")
            pcsx2INIConfig.set(pad_num, "RDown", sdl_num + "/+RightY")
            pcsx2INIConfig.set(pad_num, "RLeft", sdl_num + "/-RightX")
            pcsx2INIConfig.set(pad_num, "Analog", sdl_num + "/Guide")
            pcsx2INIConfig.set(pad_num, "LargeMotor", sdl_num + "/LargeMotor")
            pcsx2INIConfig.set(pad_num, "SmallMotor", sdl_num + "/SmallMotor")

        nplayer += 1

    ## [GameList]
    if not pcsx2INIConfig.has_section("GameList"):
        pcsx2INIConfig.add_section("GameList")
    
    pcsx2INIConfig.set("GameList", "RecursivePaths", "/userdata/roms/ps2")

    with open(configFileName, 'w') as configfile:
        pcsx2INIConfig.write(configfile)

def checkAvx2():
    for line in open("/proc/cpuinfo").readlines():
        if re.match("^flags[\t ]*:.* avx2", line):
            return True
    return False
