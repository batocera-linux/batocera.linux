#!/usr/bin/env python

from generators.Generator import Generator
import Command
import batoceraFiles
import controllersConfig
import configparser
import os.path
import httplib2
import json
from utils.logger import get_logger
from os import environ

eslog = get_logger(__name__)

class DuckstationGenerator(Generator):
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        # Test if it's a m3u file
        if os.path.splitext(rom)[1] == ".m3u":
            rom = rewriteM3uFullPath(rom)

        if os.path.exists('/usr/bin/duckstation-qt'):
            commandArray = ["duckstation-qt", "-batch", "-nogui", rom ]
        else:
            commandArray = ["duckstation-nogui", "-batch", "-fullscreen", "--", rom ]

        settings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        settings.optionxform = str
        settings_path = batoceraFiles.CONF + "/duckstation/settings.ini"
        if os.path.exists(settings_path):
            settings.read(settings_path)

        ## [Main]
        if not settings.has_section("Main"):
            settings.add_section("Main")
        # Settings, Language and ConfirmPowerOff
        settings.set("Main", "SettingsVersion", "3") # Probably to be updated in the future
        settings.set("Main", "InhibitScreensaver", "true")
        settings.set("Main", "StartPaused", "false")
        # Force Fullscreen
        settings.set("Main", "StartFullscreen", "true")
        settings.set("Main", "PauseOnFocusLoss", "false")
        settings.set("Main", "PauseOnMenu", "true")
        settings.set("Main", "ConfirmPowerOff", "false")
        # Force applying game Settings fixes
        settings.set("Main","ApplyGameSettings", "true")
        # Rewind
        #if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        settings.set("Main","RewindEnable",    "true")
        settings.set("Main","RewindFrequency", "1")        # Frame skipped each seconds
        if system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"]   == '120':
            settings.set("Main","RewindSaveSlots", "120")  # Total duration available in sec
        elif system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"] == '90':
            settings.set("Main","RewindSaveSlots", "90")
        elif system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"] == '60':
            settings.set("Main","RewindSaveSlots", "60")
        elif system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"] == '30':
            settings.set("Main","RewindSaveSlots", "30")
        elif system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"] == '15':
            settings.set("Main","RewindSaveSlots", "15")
        elif system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"] == '10':
            settings.set("Main","RewindSaveSlots", "100")
            settings.set("Main","RewindFrequency", "0.100000")
        elif system.isOptSet("duckstation_rewind") and system.config["duckstation_rewind"] == '5':
            settings.set("Main","RewindSaveSlots", "50")
            settings.set("Main","RewindFrequency", "0.050000")
        else:
            settings.set("Main","RewindEnable", "false")
        # Discord
        settings.set("Main","EnableDiscordPresence", "false")
        # Language
        settings.set("Main", "Language", getLangFromEnvironment())

        ## [ControllerPorts]
        if not settings.has_section("ControllerPorts"):
            settings.add_section("ControllerPorts")
        settings.set("ControllerPorts", "ControllerSettingsMigrated", "true")
        settings.set("ControllerPorts", "MultitapMode", "Disabled")
        settings.set("ControllerPorts", "PointerXScale", "8")
        settings.set("ControllerPorts", "PointerYScale", "8")
        settings.set("ControllerPorts", "PointerXInvert", "false")
        settings.set("ControllerPorts", "PointerYInvert", "false")
        
        ## [Console]
        if not settings.has_section("Console"):
            settings.add_section("Console")
        # Region
        if system.isOptSet("duckstation_region"):
            settings.set("Console", "Region", system.config["duckstation_region"])
        else:
            settings.set("Console", "Region", "Auto")
        
        ## [BIOS]
        if not settings.has_section("BIOS"):
            settings.add_section("BIOS")
        settings.set("BIOS", "SearchDirectory", "/userdata/bios") # Path
        # Boot Logo
        if system.isOptSet("duckstation_PatchFastBoot"):
            settings.set("BIOS", "PatchFastBoot", system.config["duckstation_PatchFastBoot"])
        else:
            settings.set("BIOS", "PatchFastBoot", "false")

        ## [CPU]
        if not settings.has_section("CPU"):
            settings.add_section("CPU")
        # ExecutionMode
        if system.isOptSet("duckstation_executionmode"):
            settings.set("CPU", "ExecutionMode", system.config["duckstation_executionmode"])
        else:
            settings.set("CPU", "ExecutionMode", "Recompiler")

        ## [GPU]
        if not settings.has_section("GPU"):
            settings.add_section("GPU")
        # Renderer
        if system.isOptSet("duckstation_gfxbackend"):
            settings.set("GPU", "Renderer", system.config["duckstation_gfxbackend"])
        else:
            settings.set("GPU", "Renderer", "OpenGL")
        # Multisampling force (MSAA or SSAA) - no GUI option anymore...
        settings.set("GPU", "PerSampleShading", "false")
        settings.set("GPU", "Multisamples", "1")
        # Threaded Presentation (Vulkan Improve)
        if system.isOptSet("duckstation_threadedpresentation"):
            settings.set("GPU", "ThreadedPresentation", system.config["duckstation_threadedpresentation"])
        else:
            settings.set("GPU", "ThreadedPresentation", "false")
        # Internal resolution
        if system.isOptSet("duckstation_resolution_scale"):
            settings.set("GPU", "ResolutionScale", system.config["duckstation_resolution_scale"])
        else:
            settings.set("GPU", "ResolutionScale", "1")
        # WideScreen Hack
        if system.isOptSet('duckstation_widescreen_hack'):
            settings.set("GPU", "WidescreenHack", system.config["duckstation_widescreen_hack"])
        else:
            settings.set("GPU", "WidescreenHack", "false")
        # Force 60hz
        if system.isOptSet("duckstation_60hz"):
           settings.set("GPU", "ForceNTSCTimings", system.config["duckstation_60hz"])
        else:
           settings.set("GPU", "ForceNTSCTimings", "false")
        # TextureFiltering
        if system.isOptSet("duckstation_texture_filtering") and system.config["duckstation_texture_filtering"] != 'Nearest':
           settings.set("GPU", "TextureFilter", system.config["duckstation_texture_filtering"])
        else:
           settings.set("GPU", "TextureFilter", "Nearest")
        # PGXP - enabled by default
        if system.isOptSet("duckstation_pgxp"):
           settings.set("GPU", "PGXPEnable", system.config["duckstation_pgxp"])
           settings.set("GPU", "PGXPCulling", system.config["duckstation_pgxp"])
           settings.set("GPU", "PGXPTextureCorrection", system.config["duckstation_pgxp"])
           settings.set("GPU", "PGXPPreserveProjFP", system.config["duckstation_pgxp"])
        else:
           settings.set("GPU", "PGXPEnable", "true")
           settings.set("GPU", "PGXPCulling", "true")
           settings.set("GPU", "PGXPTextureCorrection", "true")
           settings.set("GPU", "PGXPPreserveProjFP", "true")

        ## [DISPLAY]
        if not settings.has_section("Display"):
            settings.add_section("Display")
        # Aspect Ratio
        if system.isOptSet("duckstation_ratio"):
            settings.set("Display", "AspectRatio", system.config["duckstation_ratio"])
        else:
            settings.set("Display", "AspectRatio", "Auto (Game Native)")
        # Vsync
        if system.isOptSet("duckstation_vsync"):
            settings.set("Display", "VSync", system.config["duckstation_vsync"])
        else:
            settings.set("Display", "VSync", "false")
        # CropMode
        if system.isOptSet("duckstation_CropMode"):
           settings.set("Display", "CropMode", system.config["duckstation_CropMode"])
        else:
            settings.set("Display", "CropMode", "Overscan")
        # Enable Frameskipping = option missing
        settings.set("Display", "DisplayAllFrames", "false")
        # OSD Messages
        if system.isOptSet("duckstation_osd"):
            settings.set("Display", "ShowOSDMessages", system.config["duckstation_osd"])
        else:
            settings.set("Display", "ShowOSDMessages", "false")
        
        ## [GameList]
        if not settings.has_section("GameList"):
            settings.add_section("GameList")
        settings.set("GameList" , "RecursivePaths", "/userdata/roms/psx")

        ## [CHEEVOS]
        if not settings.has_section("Cheevos"):
            settings.add_section("Cheevos")
        # RetroAchievements
        if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
            headers   = {"Content-type": "text/plain"}
            login_url = "https://retroachievements.org/"
            username  = system.config.get('retroachievements.username', "")
            password  = system.config.get('retroachievements.password', "")
            hardcore  = system.config.get('retroachievements.hardcore', "")
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
                    settings.set("Cheevos", "Enabled",       "true")
                    settings.set("Cheevos", "Username",      username)
                    settings.set("Cheevos", "Token",         token)

                    # Disables save states, cheats, slowdown functions but you receive 2x achievements points.
                    if hardcore == '1':
                        settings.set("Cheevos", "ChallengeMode", "true")
                    else:
                        settings.set("Cheevos", "ChallengeMode", "false")
                    #settings.set("Cheevos", "UseFirstDiscFromPlaylist", "false") # When enabled, the first disc in a playlist will be used for achievements, regardless of which disc is active
                    #settings.set("Cheevos", "RichPresence",  "true")             # Enable rich presence information will be collected and sent to the server where supported
                    #settings.set("Cheevos", "TestMode",      "false")            # DuckStation will assume all achievements are locked and not send any unlock notifications to the server.

                    eslog.debug(f"Duckstation RetroAchievements enabled for {username}")
            except Exception as e:
                eslog.error(f"ERROR: Impossible to get a RetroAchievements token ({e})")
                settings.set("Cheevos", "Enabled", "false")
        else:
            settings.set("Cheevos", "Enabled", "false")

        ## [ControllerPorts]
        if not settings.has_section("ControllerPorts"):
            settings.add_section("ControllerPorts")
        # Multitap
        if system.isOptSet("duckstation_multitap"):
            settings.set("ControllerPorts", "MultitapMode", system.config["duckstation_multitap"])
        else:
            settings.set("ControllerPorts", "MultitapMode", "Disabled")

        ## [TextureReplacements]
        if not settings.has_section("TextureReplacements"):
            settings.add_section("TextureReplacements")
        # Texture Replacement saves\textures\psx game id - by default in Normal
        if system.isOptSet("duckstation_custom_textures") and system.config["duckstation_custom_textures"] == '0':
            settings.set("TextureReplacements", "EnableVRAMWriteReplacements", "false")
            settings.set("TextureReplacements", "PreloadTextures",  "false")
        elif system.isOptSet("duckstation_custom_textures") and system.config["duckstation_custom_textures"] == 'preload':
            settings.set("TextureReplacements", "EnableVRAMWriteReplacements", "true")
            settings.set("TextureReplacements", "PreloadTextures",  "true")
        else:
            settings.set("TextureReplacements", "EnableVRAMWriteReplacements", "true")
            settings.set("TextureReplacements", "PreloadTextures",  "false")

        if not settings.has_section("InputSources"):
            settings.add_section("InputSources")
        settings.set("InputSources", "SDL", "true")
        settings.set("InputSources", "SDLControllerEnhancedMode", "false")
        settings.set("InputSources", "Evdev", "false")
        settings.set("InputSources", "XInput", "false")
        settings.set("InputSources", "RawInput", "false")
        
        ## [CONTROLLERS]
        configurePads(settings, playersControllers, system, guns)

        ## [Hotkeys]
        if not settings.has_section("Hotkeys"):
            settings.add_section("Hotkeys")
        # Force defaults to be aligned with evmapy
        settings.set("Hotkeys", "FastForward",                 "Keyboard/Tab")
        settings.set("Hotkeys", "Reset",                       "Keyboard/F6")
        settings.set("Hotkeys", "PowerOff",                    "Keyboard/Escape")
        settings.set("Hotkeys", "LoadSelectedSaveState",       "Keyboard/F1")
        settings.set("Hotkeys", "SaveSelectedSaveState",       "Keyboard/F2")
        settings.set("Hotkeys", "SelectPreviousSaveStateSlot", "Keyboard/F3")
        settings.set("Hotkeys", "SelectNextSaveStateSlot",     "Keyboard/F4")
        settings.set("Hotkeys", "Screenshot",                  "Keyboard/F10")
        settings.set("Hotkeys", "Rewind",                      "Keyboard/F5")
        settings.set("Hotkeys", "OpenQuickMenu",               "Keyboard/F7")

        ## [CDROM]
        if not settings.has_section("CDROM"):
            settings.add_section("CDROM")
        if system.isOptSet("duckstation_boot_without_sbi"):
            settings.set("CDROM", "AllowBootingWithoutSBIFile", system.config["duckstation_boot_without_sbi"])
        else:
            settings.set("CDROM", "AllowBootingWithoutSBIFile", "false")

        # Save config
        if not os.path.exists(os.path.dirname(settings_path)):
            os.makedirs(os.path.dirname(settings_path))
        with open(settings_path, 'w') as configfile:
            settings.write(configfile)
         
        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": batoceraFiles.CONF,
                "QT_QPA_PLATFORM": "xcb",
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

def configurePads(settings, playersControllers, system, guns):
    mappings = {
        "ButtonUp":       "up",
        "ButtonDown":     "down",
        "ButtonLeft":     "left",
        "ButtonRight":    "right",
        "ButtonSelect":   "select",
        "ButtonStart":    "start",
        "ButtonTriangle": "x",
        "ButtonCross":    "b",
        "ButtonSquare":   "y",
        "ButtonCircle":   "a",
        "ButtonL1":       "pageup",
        "ButtonL2":       "l2",
        "ButtonR1":       "pagedown",
        "ButtonR2":       "r2",
        "ButtonL3":       "l3",
        "ButtonR3":       "r3",
        "AxisLeftX":      "joystick1left",
        "AxisLeftY":      "joystick1up",
        "AxisRightX":     "joystick2left",
        "AxisRightY":     "joystick2up"
        }

    # Clear existing config
    for i in range(1, 8):
        if settings.has_section("Controller" + str(i)):
            settings.remove_section("Controller" + str(i))

    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        controller = "Controller" + str(nplayer)

        ## [SECTION]
        if not settings.has_section(controller):
            settings.add_section(controller)

        # Controller Type
        ctrlType = "AnalogController"
        settings.set(controller, "Type", "AnalogController") # defaults to AnalogController to make dpad to joystick work by default
        if system.isOptSet("duckstation_" + controller) and system.config['duckstation_' + controller] != 'DigitalController':
            settings.set(controller, "Type", system.config["duckstation_" + controller])
            ctrlType = system.config["duckstation_" + controller]

        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
            if nplayer == 1 and len(guns) >= 1:
                settings.set(controller, "Type", "NamcoGunCon")
                ctrlType = "NamcoGunCon"

        # Rumble
        controllerRumbleList = {'AnalogController', 'NamcoGunCon', 'NeGcon'};

        if system.isOptSet("duckstation_rumble") and system.config["duckstation_rumble"] != '0':
            if system.isOptSet("duckstation_" + controller) and (system.config["duckstation_" + controller] in controllerRumbleList):
                settings.set(controller, "Rumble", "Controller" + str(pad.index))
        else:
            settings.set(controller, "Rumble", "false")

        # Dpad to Joystick
        if system.isOptSet("duckstation_digitalmode") and system.config["duckstation_digitalmode"] == '0':
            settings.set(controller, "AnalogDPadInDigitalMode", "false")
        else:
            settings.set(controller, "AnalogDPadInDigitalMode", "true")

        for mapping in mappings:
            if mappings[mapping] in pad.inputs:
                # mapping workaround - for l2 & r2 if axis, require positive value
                if mappings[mapping] == "l2" or mappings[mapping] == "r2" and ctrlType == "AnalogController":
                    trigger=input2definition(pad.inputs[mappings[mapping]])
                    if "Axis" in trigger:
                        settings.set(controller, mapping, "Controller" + str(pad.index) + "/+" + input2definition(pad.inputs[mappings[mapping]]))
                    else:
                        settings.set(controller, mapping, "Controller" + str(pad.index) + "/" + input2definition(pad.inputs[mappings[mapping]]))
                else:
                    settings.set(controller, mapping, "Controller" + str(pad.index) + "/" + input2definition(pad.inputs[mappings[mapping]]))

        controllerGunList = {'NamcoGunCon', 'NeGcon'};
        # Testing if Gun, add specific keys
        if system.isOptSet("duckstation_" + controller) and system.config["duckstation_" + controller] in controllerGunList:
            settings.set(controller, "ButtonTrigger"       ,"Mouse/Button1")
            settings.set(controller, "ButtonShootOffscreen","Mouse/Button2")
            settings.set(controller, "ButtonA"             ,"Keyboard/VolumeUp")
            settings.set(controller, "ButtonB"             ,"Keyboard/VolumeDown")
            settings.set(controller, "AxisSteering"       ,"")
            settings.set(controller, "AxisI"              ,"")
            settings.set(controller, "AxisII"             ,"")
            settings.set(controller, "AxisL"              ,"")
            #settings.set(controller, "CrosshairImagePath" ,"/userdata/saves/duckstation/aimP1.png")     TO BE DISCUSSED LATER FOR CUSTOM AIMING
            #settings.set(controller, "CrosshairScale"     ,"0.3")                                       TO BE DISCUSSED LATER FOR CUSTOM AIMING

        # Testing if Mouse, add specific keys
        elif system.isOptSet("duckstation_" + controller) and system.config["duckstation_" + controller] == "PlayStationMouse":
            settings.set(controller, "Left"                ,"Mouse/Button1")
            settings.set(controller, "Right"               ,"Mouse/Button2")

        nplayer = nplayer + 1

def input2definition(input):
    if input.type == "button":
        return "Button" + str(input.id)
    elif input.type == "hat":
        if input.value == "1":
            return "Hat0 Up"
        elif input.value == "2":
            return "Hat0 Right"
        elif input.value == "4":
            return "Hat0 Down"
        elif input.value == "8":
            return "Hat0 Left"
    elif input.type == "axis":
        return "Axis" + str(input.id)
    return "unknown"

def getLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": "en",
                           "de_DE": "de",
                           "fr_FR": "fr",
                           "es_ES": "es",
                           "he_IL": "he",
                           "it_IT": "it",
                           "ja_JP": "ja",
                           "nl_NL": "nl",
                           "pl_PL": "pl",
                           "pt_BR": "pt-br",
                           "pt_PT": "pt-pt",
                           "ru_RU": "ru",
                           "zh_CN": "zh-cn"
    }

    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]

def rewriteM3uFullPath(m3u):                                                                    # Rewrite a clean m3u file with valid fullpath
    # get initialm3u
    firstline = open(m3u).readline().rstrip()                                                   # Get first line in m3u
    initialfirstdisc = "/tmp/" + os.path.splitext(os.path.basename(firstline))[0] + ".m3u"      # Generating a temp path with the first iso filename in m3u

    # create a temp m3u to bypass Duckstation m3u bad pathfile
    fulldirname = os.path.dirname(m3u)
    readtempm3u = open(initialfirstdisc, "w")

    initialm3u = open(m3u, "r")
    with open(initialfirstdisc, 'a') as f1:
        for line in initialm3u:
            if line[0] == "/":                          # for /MGScd1.chd
                newpath = fulldirname + line
            else:
                newpath = fulldirname + "/" + line      # for MGScd1.chd
            f1.write(newpath)

    return initialfirstdisc                                                                      # Return the tempm3u pathfile written with valid fullpath
