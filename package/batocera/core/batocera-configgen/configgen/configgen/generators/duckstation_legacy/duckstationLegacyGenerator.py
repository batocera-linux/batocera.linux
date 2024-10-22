from __future__ import annotations

import logging
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import BIOS, CONFIGS, ensure_parents_and_open
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


eslog = logging.getLogger(__name__)

class DuckstationLegacyGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "duckstation",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        # Test if it's a m3u file
        if rom_path.suffix == ".m3u":
            rom_path = rewriteM3uFullPath(rom_path)

        if Path('/usr/bin/duckstation-qt').exists():
            commandArray = ["duckstation-qt", "-batch", "-nogui", "--", rom_path ]
        else:
            commandArray = ["duckstation-nogui", "-batch", "-fullscreen", "--", rom_path ]

        settings = CaseSensitiveConfigParser(interpolation=None)
        settings_path = CONFIGS / "duckstation" / "settings.ini"
        if settings_path.exists():
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
        # overclock
        if system.isOptSet("duckstation_clocking"):
            settings.set("Main","EmulationSpeed", system.config["duckstation_clocking"])
        else:
            settings.set("Main","EmulationSpeed", "1")
        # host refresh rate
        if system.isOptSet("duckstation_hrr"):
            settings.set("Main","SyncToHostRefreshRate", system.config["duckstation_hrr"])
        else:
            settings.set("Main","SyncToHostRefreshRate", "false")

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
        settings.set("BIOS", "SearchDirectory", "/userdata/bios")
        # Boot Logo
        if system.isOptSet("duckstation_PatchFastBoot"):
            settings.set("BIOS", "PatchFastBoot", system.config["duckstation_PatchFastBoot"])
        else:
            settings.set("BIOS", "PatchFastBoot", "false")
        # Find & populate BIOS
        USbios = [ "scph101.bin", "scph1001.bin", "scph5501.bin", "scph7001.bin", "scph7501.bin" ]
        EUbios = [ "scph1002.bin", "scph5502.bin", "scph5552.bin", "scph7002.bin", "scph7502.bin", "scph9002.bin", "scph102a.bin", "scph102b.bin" ]
        JPbios = [ "scph100.bin", "scph1000.bin", "scph3000.bin", "scph3500.bin", "scph5500.bin", "scph7000.bin", "scph7003.bin" ]
        biosFound = False
        USbiosFile = EUbiosFile = JPbiosFile = None
        for bio in USbios:
            if (BIOS / bio).exists():
                USbiosFile = bio
                biosFound = True
                break
        for bio in EUbios:
            if (BIOS / bio).exists():
                EUbiosFile = bio
                biosFound = True
                break
        for bio in JPbios:
            if (BIOS / bio).exists():
                JPbiosFile = bio
                biosFound = True
                break
        if not biosFound:
            raise Exception("No PSX1 BIOS found")
        if USbiosFile is not None:
            settings.set("BIOS", "PathNTSCU", USbiosFile)
        if EUbiosFile is not None:
            settings.set("BIOS", "PathPAL", EUbiosFile)
        if JPbiosFile is not None:
            settings.set("BIOS", "PathNTSCJ", JPbiosFile)

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
        # True Color
        if system.isOptSet("duckstation_truecolour"):
           settings.set("GPU", "TrueColor", system.config["duckstation_truecolour"])
        else:
           settings.set("GPU", "TrueColor", "false")
        # Scaled Dithering
        if system.isOptSet("duckstation_dithering"):
           settings.set("GPU", "ScaledDithering", system.config["duckstation_dithering"])
        else:
           settings.set("GPU", "ScaledDithering", "true")
        # Disable Interlacing
        if system.isOptSet("duckstation_interlacing"):
           settings.set("GPU", "DisableInterlacing", system.config["duckstation_interlacing"])
        else:
           settings.set("GPU", "DisableInterlacing", "false")
        # Anti-Aliasing
        if system.isOptSet("duckstation_antialiasing"):
            if 'ssaa' in system.config["duckstation_antialiasing"]:
                settings.set("GPU", "PerSampleShading", "true")
                parts = system.config["duckstation_antialiasing"].split('-')
                multisamples = parts[0]
                settings.set("GPU", "Multisamples", multisamples)
            else:
                settings.set("GPU", "Multisamples", system.config["duckstation_antialiasing"])
                settings.set("GPU", "PerSampleShading", "false")

        ## [Display]
        if not settings.has_section("Display"):
            settings.add_section("Display")
        # Aspect Ratio
        if system.isOptSet("duckstation_ratio"):
            settings.set("Display", "AspectRatio", system.config["duckstation_ratio"])
            if not system.config["duckstation_ratio"] == "4:3":
                system.config['bezel'] = "none"
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
        # Optimal frame pacing
        if system.isOptSet("duckstation_ofp"):
            settings.set("Display","DisplayAllFrames", system.config["duckstation_ofp"])
        else:
            settings.set("Display","DisplayAllFrames", "false")
        # Integer Scaling
        if system.isOptSet("duckstation_integer"):
            settings.set("Display","IntegerScaling", system.config["duckstation_integer"])
        else:
            settings.set("Display","IntegerScaling", "false")
        # Linear Filtering
        if system.isOptSet("duckstation_linear"):
            settings.set("Display","LinearFiltering", system.config["duckstation_linear"])
        else:
            settings.set("Display","LinearFiltering", "false")
        # Stretch
        if system.isOptSet("duckstation_stretch") and system.config["duckstation_stretch"] == "true":
            settings.set("Display","Stretch", system.config["duckstation_stretch"])
            if not system.isOptSet("duckstation_integer") or system.config["duckstation_integer"] == "false":
                system.config['bezel'] = "none"
        else:
            settings.set("Display","Stretch", "false")

        ## [Audio]
        if not settings.has_section("Audio"):
            settings.add_section("Audio")
        if system.isOptSet("duckstation_audio_mode"):
            settings.set("Audio","StretchMode", system.config["duckstation_audio_mode"])
        else:
            settings.set("Audio","StretchMode", "TimeStretch")

        ## [GameList]
        if not settings.has_section("GameList"):
            settings.add_section("GameList")
        settings.set("GameList" , "RecursivePaths", "/userdata/roms/psx")

        ## [Cheevos]
        if not settings.has_section("Cheevos"):
            settings.add_section("Cheevos")
        # RetroAchievements
        if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
            headers   = {"Content-type": "text/plain", "User-Agent": "Batocera.linux"}
            login_url = "https://retroachievements.org/"
            username  = system.config.get('retroachievements.username', "")
            password  = system.config.get('retroachievements.password', "")
            hardcore  = system.config.get('retroachievements.hardcore', "")
            presence  = system.config.get('retroachievements.richpresence', "")
            indicator = system.config.get('retroachievements.challenge_indicators', "")
            leaderbd  = system.config.get('retroachievements.leaderboards', "")
            token     = system.config.get('retroachievements.token', "")
            settings.set("Cheevos", "Enabled",       "true")
            settings.set("Cheevos", "Username",      username)
            settings.set("Cheevos", "Token",         token)
            if hardcore == '1':
                settings.set("Cheevos", "ChallengeMode", "true")    # For "hardcore" retroachievement points (no save, no rewind...)
            else:
                settings.set("Cheevos", "ChallengeMode", "false")
            if presence == '1':
                settings.set("Cheevos", "RichPresence",  "true")    # Enable rich presence information will be collected and sent to the server where supported
            else:
                settings.set("Cheevos", "RichPresence",  "false")
            if indicator == '1':
                settings.set("Cheevos", "PrimedIndicators",  "true")
            else:
                settings.set("Cheevos", "PrimedIndicators",  "false")
            if leaderbd == '1':
                settings.set("Cheevos", "Leaderboards",  "true")
            else:
                settings.set("Cheevos", "Leaderboards",  "false")
            #settings.set("Cheevos", "UseFirstDiscFromPlaylist", "false") # When enabled, the first disc in a playlist will be used for achievements, regardless of which disc is active
            #settings.set("Cheevos", "TestMode",      "false")            # DuckStation will assume all achievements are locked and not send any unlock notifications to the server.
        else:
            settings.set("Cheevos", "Enabled", "false")

        ## [ControllerPorts]
        if not settings.has_section("ControllerPorts"):
            settings.add_section("ControllerPorts")
        # setting get applied later

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

        ## [MemoryCards]
        if not settings.has_section("MemoryCards"):
            settings.add_section("MemoryCards")
        # Set memory card location
        settings.set("MemoryCards", "Directory", "../../../saves/duckstation/memcards")

        ## [Folders]
        if not settings.has_section("Folders"):
            settings.add_section("Folders")
        # Set other folder locations too
        settings.set("Folders", "Cache", "../../cache/duckstation")
        settings.set("Folders", "Screenshots", "../../../screenshots")
        settings.set("Folders", "SaveStates", "../../../saves/duckstation")
        settings.set("Folders", "Cheats", "../../../cheats/duckstation")

        ## [Pad]
        # Clear existing Pad(x) configs
        for i in range(1, 9):
            if settings.has_section("Pad" + str(i)):
                settings.remove_section("Pad" + str(i))
        # Now create Pad1 - 8 None to start
        for i in range(1, 9):
            settings.add_section("Pad" + str(i))
            settings.set("Pad" + str(i), "Type", "None")
        # Start with mutitap disabled
        settings.set("ControllerPorts", "MultitapMode", "Disabled")
        # Now add the controller config based on the ES type & number connected
        nplayer = 1
        for controller, pad in sorted(playersControllers.items()):
            if nplayer <= 8:
                # automatically add the multi-tap
                if nplayer > 2:
                    settings.set("ControllerPorts", "MultitapMode", "Port1Only")
                    if nplayer > 4:
                        settings.set("ControllerPorts", "MultitapMode", "BothPorts")
                pad_num = "Pad{}".format(nplayer)
                sdl_num = "SDL-{}".format(pad.index)
                ctrl_num = "Controller" + str(nplayer)
                # SDL2 configs are always the same for controllers
                if system.isOptSet("duckstation_" + ctrl_num):
                    settings.set(pad_num, "Type", system.config["duckstation_" + ctrl_num])
                else:
                    settings.set(pad_num, "Type", "DigitalController")
                settings.set(pad_num, "Up", sdl_num+"/DPadUp")
                settings.set(pad_num, "Right", sdl_num+"/DPadRight")
                settings.set(pad_num, "Down", sdl_num+"/DPadDown")
                settings.set(pad_num, "Left", sdl_num+"/DPadLeft")
                settings.set(pad_num, "Triangle", sdl_num+"/Y")
                settings.set(pad_num, "Circle", sdl_num+"/B")
                settings.set(pad_num, "Cross", sdl_num+"/A")
                settings.set(pad_num, "Square", sdl_num+"/X")
                settings.set(pad_num, "Select", sdl_num+"/Back")
                settings.set(pad_num, "Start", sdl_num+"/Start")
                settings.set(pad_num, "L1", sdl_num+"/LeftShoulder")
                settings.set(pad_num, "R1", sdl_num+"/RightShoulder")
                settings.set(pad_num, "L2", sdl_num+"/+LeftTrigger")
                settings.set(pad_num, "R2", sdl_num+"/+RightTrigger")
                settings.set(pad_num, "L3", sdl_num+"/LeftStick")
                settings.set(pad_num, "R3", sdl_num+"/RightStick")
                settings.set(pad_num, "LLeft", sdl_num+"/-LeftX")
                settings.set(pad_num, "LRight", sdl_num+"/+LeftX")
                settings.set(pad_num, "LDown", sdl_num+"/+LeftY")
                settings.set(pad_num, "LUp", sdl_num+"/-LeftY")
                settings.set(pad_num, "RLeft", sdl_num+"/-RightX")
                settings.set(pad_num, "RRight", sdl_num+"/+RightX")
                settings.set(pad_num, "RDown", sdl_num+"/+RightY")
                settings.set(pad_num, "RUp", sdl_num+"/-RightY")
                settings.set(pad_num, "SmallMotor", sdl_num+"/SmallMotor")
                settings.set(pad_num, "LargeMotor", sdl_num+"/LargeMotor")
                settings.set(pad_num, "VibrationBias", "8")
                # D-Pad to Joystick
                if system.isOptSet("duckstation_digitalmode"):
                    settings.set(pad_num, "AnalogDPadInDigitalMode", system.config["duckstation_digitalmode"])
                    if system.isOptSet("duckstation_" + ctrl_num) and system.config["duckstation_" + ctrl_num] == "AnalogController":
                        settings.set(pad_num, "Analog", sdl_num+"/Guide & "+sdl_num+"/+LeftTrigger")
                else:
                    settings.set(pad_num, "AnalogDPadInDigitalMode", "false")
                # NeGcon ?
                if system.isOptSet("duckstation_" + ctrl_num) and system.config["duckstation_" + ctrl_num] == "NeGcon":
                    settings.set(pad_num, "A", sdl_num+"/B")
                    settings.set(pad_num, "B", sdl_num+"/Y")
                    settings.set(pad_num, "I", sdl_num+"/+RightTrigger")
                    settings.set(pad_num, "II", sdl_num+"/+LeftTrigger")
                    settings.set(pad_num, "L", sdl_num+"/LeftShoulder")
                    settings.set(pad_num, "R", sdl_num+"/RightShoulder")
                    settings.set(pad_num, "SteeringLeft", sdl_num+"/-LeftX")
                    settings.set(pad_num, "SteeringRight", sdl_num+"/+LeftX")
                # Guns - GunCon
                if system.isOptSet("duckstation_" + ctrl_num) and system.config["duckstation_" + ctrl_num] == "GunCon":
                    settings.set(pad_num, "Trigger", sdl_num+"/+RightTrigger")
                    settings.set(pad_num, "ShootOffscreen", sdl_num+"/+LeftTrigger")
                    settings.set(pad_num, "A", sdl_num+"/A")
                    settings.set(pad_num, "B", sdl_num+"/B")
                # Mouse
                if system.isOptSet("duckstation_" + ctrl_num) and system.config["duckstation_" + ctrl_num] == "PlayStationMouse":
                    settings.set(pad_num, "Right", sdl_num+"/B")
                    settings.set(pad_num, "Left", sdl_num+"/A")
                    settings.set(pad_num, "RelativeMouseMode", sdl_num+"true")
            # Next controller
            nplayer += 1

        ## [Hotkeys]
        if not settings.has_section("Hotkeys"):
            settings.add_section("Hotkeys")
        # Force defaults to be aligned with evmapy
        settings.set("Hotkeys", "FastForward",                 "Keyboard/Tab")
        settings.set("Hotkeys", "Reset",                       "Keyboard/F6")
        settings.set("Hotkeys", "LoadSelectedSaveState",       "Keyboard/F1")
        settings.set("Hotkeys", "SaveSelectedSaveState",       "Keyboard/F2")
        settings.set("Hotkeys", "SelectPreviousSaveStateSlot", "Keyboard/F3")
        settings.set("Hotkeys", "SelectNextSaveStateSlot",     "Keyboard/F4")
        settings.set("Hotkeys", "Screenshot",                  "Keyboard/F10")
        settings.set("Hotkeys", "Rewind",                      "Keyboard/F5")
        settings.set("Hotkeys", "OpenPauseMenu",               "Keyboard/F7")
        settings.set("Hotkeys", "ChangeDisc",                  "Keyboard/F8")
        if settings.has_option('Hotkeys', 'OpenQuickMenu'):
            settings.remove_option('Hotkeys', 'OpenQuickMenu')

        ## [CDROM]
        if not settings.has_section("CDROM"):
            settings.add_section("CDROM")
        if system.isOptSet("duckstation_boot_without_sbi"):
            settings.set("CDROM", "AllowBootingWithoutSBIFile", system.config["duckstation_boot_without_sbi"])
        else:
            settings.set("CDROM", "AllowBootingWithoutSBIFile", "false")

        # Save config
        with ensure_parents_and_open(settings_path, 'w') as configfile:
            settings.write(configfile)

        # write our own gamecontrollerdb.txt file before launching the game
        dbfile = "/usr/share/duckstation/resources/gamecontrollerdb.txt"
        write_sdl_controller_db(playersControllers, dbfile)

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "QT_QPA_PLATFORM": "xcb",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

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

def rewriteM3uFullPath(m3u: Path) -> Path:
    # Rewrite a clean m3u file with valid fullpath

    # get initialm3u
    with m3u.open() as f:
        firstline = f.readline().rstrip()  # Get first line in m3u

    initialfirstdisc = Path("/tmp") / Path(firstline).with_suffix(".m3u").name  # Generating a temp path with the first iso filename in m3u

    # create a temp m3u to bypass Duckstation m3u bad pathfile
    fulldirname = m3u.parent
    with initialfirstdisc.open("w"):
        pass

    with m3u.open() as initialm3u, initialfirstdisc.open('a') as f1:
        for line in initialm3u:
            # handle both "/MGScd1.chd" and "MGScd1.chd"
            if line[0] == "/":
                newpath = fulldirname / line[1:]
            else:
                newpath = fulldirname / line
            f1.write(str(newpath))

    return initialfirstdisc  # Return the tempm3u pathfile written with valid fullpath
