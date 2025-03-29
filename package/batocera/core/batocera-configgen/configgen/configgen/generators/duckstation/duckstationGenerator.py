from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import BIOS, CONFIGS, ensure_parents_and_open
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ...exceptions import BatoceraException
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ...types import HotkeysContext


class DuckstationGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "duckstation",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F7", "reset": "KEY_F6",
                      "restore_state": "KEY_F1", "save_state": "KEY_F2", "previous_slot": "KEY_F3", "next_slot": "KEY_F4",
                      "rewind": "KEY_F5", "fastforward": "KEY_TAB", "next_disk": "KEY_F8"
                     }
    }

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
        # Test if it's a m3u file
        if rom.suffix == ".m3u":
            rom = rewriteM3uFullPath(rom)

        if Path('/usr/bin/duckstation-qt').exists():
            commandArray = ["duckstation-qt", "-batch", "-nogui", "--", rom ]
        else:
            commandArray = ["duckstation-nogui", "-batch", "-fullscreen", "--", rom ]

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
        # Remove wizard
        settings.set("Main","SetupWizardIncomplete", "false")
        # overclock
        settings.set("Main","EmulationSpeed", system.config.get("duckstation_clocking", "1"))
        # host refresh rate
        settings.set("Main","SyncToHostRefreshRate", system.config.get("duckstation_hrr", "false"))

        # Rewind
        #if system.config.get_bool('rewind'):
        settings.set("Main","RewindEnable",    "true")
        settings.set("Main","RewindFrequency", "1")        # Frame skipped each seconds
        match system.config.get("duckstation_rewind"):
            case '120' | '90' | '60' | '30' | '15' as rewind:
                settings.set("Main","RewindSaveSlots", rewind)  # Total duration available in sec
            case '10':
                settings.set("Main","RewindSaveSlots", "100")
                settings.set("Main","RewindFrequency", "0.100000")
            case '5':
                settings.set("Main","RewindSaveSlots", "50")
                settings.set("Main","RewindFrequency", "0.050000")
            case _:
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
        settings.set("Console", "Region", system.config.get("duckstation_region", "Auto"))
        # Enable Cheats
        settings.set("Console", "EnableCheats", system.config.get("duckstation_cheats", "False"))


        ## [BIOS]
        if not settings.has_section("BIOS"):
            settings.add_section("BIOS")
        settings.set("BIOS", "SearchDirectory", "/userdata/bios")
        # Boot Logo
        settings.set("BIOS", "PatchFastBoot", system.config.get("duckstation_PatchFastBoot", "false"))
        # Find & populate BIOS
        found_bios = find_bios(bios_lists)

        if not found_bios:
            raise BatoceraException("No PSX1 BIOS found")

        # Set BIOS paths
        if "Uni" in found_bios:
            uni_bios = found_bios["Uni"]
            settings.set("BIOS", "PathNTSCU", uni_bios)
            settings.set("BIOS", "PathPAL", uni_bios)
            settings.set("BIOS", "PathNTSCJ", uni_bios)
        else:
            region_mapping = {"NTSCU": "PathNTSCU", "PAL": "PathPAL", "NTSCJ": "PathNTSCJ"}
            for region, bios in found_bios.items():
                settings.set("BIOS", region_mapping[region], bios)

        ## [CPU]
        if not settings.has_section("CPU"):
            settings.add_section("CPU")
        # ExecutionMode
        settings.set("CPU", "ExecutionMode", system.config.get("duckstation_executionmode", "Recompiler"))

        ## [GPU]
        if not settings.has_section("GPU"):
            settings.add_section("GPU")
        # Renderer
        settings.set("GPU", "Renderer", system.config.get("duckstation_gfxbackend", "OpenGL"))
        # Multisampling force (MSAA or SSAA) - no GUI option anymore...
        settings.set("GPU", "PerSampleShading", "false")
        settings.set("GPU", "Multisamples", "1")
        # Threaded Presentation (Vulkan Improve)
        settings.set("GPU", "ThreadedPresentation", system.config.get("duckstation_threadedpresentation", "false"))
        # Internal resolution
        settings.set("GPU", "ResolutionScale", system.config.get("duckstation_resolution_scale", "1"))
        # WideScreen Hack
        settings.set("GPU", "WidescreenHack", system.config.get("duckstation_widescreen_hack", "false"))
        # Force 60hz
        settings.set("GPU", "ForceNTSCTimings", system.config.get("duckstation_60hz", "false"))
        # TextureFiltering
        settings.set("GPU", "TextureFilter", system.config.get("duckstation_texture_filtering", "Nearest"))
        # PGXP - enabled by default
        pgxp = system.config.get("duckstation_pgxp", "true")
        settings.set("GPU", "PGXPEnable", pgxp)
        settings.set("GPU", "PGXPCulling", pgxp)
        settings.set("GPU", "PGXPTextureCorrection", pgxp)
        settings.set("GPU", "PGXPPreserveProjFP", pgxp)
        # True Color
        settings.set("GPU", "TrueColor", system.config.get("duckstation_truecolour", "false"))
        # Scaled Dithering
        settings.set("GPU", "ScaledDithering", system.config.get("duckstation_dithering", "true"))
        # Disable Interlacing
        settings.set("GPU", "DisableInterlacing", system.config.get("duckstation_interlacing", "false"))
        # Anti-Aliasing
        if antialiasing := system.config.get("duckstation_antialiasing"):
            if 'ssaa' in antialiasing:
                settings.set("GPU", "PerSampleShading", "true")
                parts = antialiasing.split('-')
                multisamples = parts[0]
                settings.set("GPU", "Multisamples", multisamples)
            else:
                settings.set("GPU", "Multisamples", antialiasing)
                settings.set("GPU", "PerSampleShading", "false")

        ## [Display]
        if not settings.has_section("Display"):
            settings.add_section("Display")
        # Aspect Ratio
        aspect_ratio = system.config.get("duckstation_ratio")
        settings.set("Display", "AspectRatio", aspect_ratio or "Auto (Game Native)")

        if aspect_ratio is not system.config.MISSING and  aspect_ratio != "4:3":
            system.config['bezel'] = "none"
        # Vsync
        settings.set("Display", "VSync", system.config.get("duckstation_vsync", "false"))
        # CropMode
        settings.set("Display", "CropMode", system.config.get("duckstation_CropMode", "Overscan"))
        # Enable Frameskipping = option missing
        settings.set("Display", "DisplayAllFrames", "false")
        # OSD Messages
        settings.set("Display", "ShowOSDMessages", system.config.get("duckstation_osd", "false"))
        # Optimal frame pacing
        settings.set("Display","DisplayAllFrames", system.config.get("duckstation_ofp", "false"))
        # Integer Scaling
        settings.set("Display","IntegerScaling", system.config.get("duckstation_integer", "false"))
        # Linear Filtering
        settings.set("Display","LinearFiltering", system.config.get("duckstation_linear", "false"))
        # Stretch
        stretch = system.config.get("duckstation_stretch", "false")
        settings.set("Display","Stretch", stretch)

        if stretch == "true" and system.config.get("duckstation_integer", "false") == "false":
            system.config['bezel'] = "none"

        ## [Audio]
        if not settings.has_section("Audio"):
            settings.add_section("Audio")
        settings.set("Audio","StretchMode", system.config.get("duckstation_audio_mode", "TimeStretch"))

        ## [GameList]
        if not settings.has_section("GameList"):
            settings.add_section("GameList")
        settings.set("GameList" , "RecursivePaths", "/userdata/roms/psx")

        ## [Cheevos]
        if not settings.has_section("Cheevos"):
            settings.add_section("Cheevos")
        # RetroAchievements
        if system.config.get_bool('retroachievements'):
            username  = system.config.get('retroachievements.username', "")
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

        ## [TextureReplacements]
        if not settings.has_section("TextureReplacements"):
            settings.add_section("TextureReplacements")
        # Texture Replacement saves\textures\psx game id - by default in Normal
        enable_vram_write_replacements = "true"
        preload_textures = "false"

        match system.config.get("duckstation_custom_textures"):
            case "false" | "0":
                enable_vram_write_replacements = "false"
            case "preload":
                preload_textures = "true"

        settings.set("TextureReplacements", "EnableVRAMWriteReplacements", enable_vram_write_replacements)
        settings.set("TextureReplacements", "PreloadTextures",  preload_textures)

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
            if settings.has_section(f"Pad{i}"):
                settings.remove_section(f"Pad{i}")
        # Now create Pad1 - 8 None to start
        for i in range(1, 9):
            settings.add_section(f"Pad{i}")
            settings.set(f"Pad{i}", "Type", "None")
        # Start with mutitap disabled
        settings.set("ControllerPorts", "MultitapMode", "Disabled")
        # Now add the controller config based on the ES type & number connected
        for nplayer, pad in enumerate(playersControllers[:8], start=1):
            # automatically add the multi-tap
            if nplayer > 2:
                settings.set("ControllerPorts", "MultitapMode", "Port1Only")
                if nplayer > 4:
                    settings.set("ControllerPorts", "MultitapMode", "BothPorts")
            pad_num = f"Pad{nplayer}"
            gun_num = f"Pointer-{pad.index}"
            sdl_num = f"SDL-{pad.index}"
            ctrl_num = f"Controller{nplayer}"
            # SDL2 configs are always the same for controllers
            settings.set(pad_num, "Type", system.config.get(f"duckstation_{ctrl_num}", "DigitalController"))
            settings.set(pad_num, "Up", f"{sdl_num}/DPadUp")
            settings.set(pad_num, "Right", f"{sdl_num}/DPadRight")
            settings.set(pad_num, "Down", f"{sdl_num}/DPadDown")
            settings.set(pad_num, "Left", f"{sdl_num}/DPadLeft")
            settings.set(pad_num, "Triangle", f"{sdl_num}/Y")
            settings.set(pad_num, "Circle", f"{sdl_num}/B")
            settings.set(pad_num, "Cross", f"{sdl_num}/A")
            settings.set(pad_num, "Square", f"{sdl_num}/X")
            settings.set(pad_num, "Select", f"{sdl_num}/Back")
            settings.set(pad_num, "Start", f"{sdl_num}/Start")
            settings.set(pad_num, "L1", f"{sdl_num}/LeftShoulder")
            settings.set(pad_num, "R1", f"{sdl_num}/RightShoulder")
            settings.set(pad_num, "L2", f"{sdl_num}/+LeftTrigger")
            settings.set(pad_num, "R2", f"{sdl_num}/+RightTrigger")
            settings.set(pad_num, "L3", f"{sdl_num}/LeftStick")
            settings.set(pad_num, "R3", f"{sdl_num}/RightStick")
            settings.set(pad_num, "LLeft", f"{sdl_num}/-LeftX")
            settings.set(pad_num, "LRight", f"{sdl_num}/+LeftX")
            settings.set(pad_num, "LDown", f"{sdl_num}/+LeftY")
            settings.set(pad_num, "LUp", f"{sdl_num}/-LeftY")
            settings.set(pad_num, "RLeft", f"{sdl_num}/-RightX")
            settings.set(pad_num, "RRight", f"{sdl_num}/+RightX")
            settings.set(pad_num, "RDown", f"{sdl_num}/+RightY")
            settings.set(pad_num, "RUp", f"{sdl_num}/-RightY")
            settings.set(pad_num, "SmallMotor", f"{sdl_num}/SmallMotor")
            settings.set(pad_num, "LargeMotor", f"{sdl_num}/LargeMotor")
            settings.set(pad_num, "VibrationBias", "8")
            # D-Pad to Joystick
            digitalmode = system.config.get("duckstation_digitalmode")
            settings.set(pad_num, "AnalogDPadInDigitalMode", digitalmode or "false")
            if digitalmode and system.config.get(f"duckstation_{ctrl_num}") == "AnalogController":
                settings.set(pad_num, "Analog", f"{sdl_num}/Guide")
            # NeGcon ?
            if system.config.get(f"duckstation_{ctrl_num}") == "NeGcon":
                settings.set(pad_num, "A", f"{sdl_num}/B")
                settings.set(pad_num, "B", f"{sdl_num}/Y")
                settings.set(pad_num, "I", f"{sdl_num}/+RightTrigger")
                settings.set(pad_num, "II", f"{sdl_num}/+LeftTrigger")
                settings.set(pad_num, "L", f"{sdl_num}/LeftShoulder")
                settings.set(pad_num, "R", f"{sdl_num}/RightShoulder")
                settings.set(pad_num, "SteeringLeft", f"{sdl_num}/-LeftX")
                settings.set(pad_num, "SteeringRight", f"{sdl_num}/+LeftX")
            # Guns
            if system.config.use_guns and guns:
                # Justifier compatible ROM...
                if metadata.get("gun_type") == "justifier":
                    settings.set(pad_num, "Type", "Justifier")
                    settings.set(pad_num, "Trigger", f"{gun_num}/LeftButton")
                    settings.set(pad_num, "Start", f"{gun_num}/RightButton")
                # Default or GunCon compatible ROM...
                else:
                    settings.set(pad_num, "Type", "GunCon")
                    settings.set(pad_num, "Trigger", f"{gun_num}/LeftButton")

                ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
                pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
                pedalkey = None
                pedalcname = f"controllers.pedals{nplayer}"
                if pedalcname in system.config:
                    pedalkey = system.config[pedalcname]
                else:
                    if nplayer in pedalsKeys:
                        pedalkey = pedalsKeys[nplayer]
                if pedalkey is None:
                    settings.set(pad_num, "A", f"{gun_num}/RightButton")
                else:
                    settings.set(pad_num, "A", f"{gun_num}/RightButton & Keyboard/{pedalkey.upper()}")
                ###
                settings.set(pad_num, "B", f"{gun_num}/MiddleButton")
                if system.config.get(f"duckstation_{ctrl_num}") == "GunCon":
                    settings.set(pad_num, "Trigger", f"{sdl_num}/+RightTrigger")
                    settings.set(pad_num, "ShootOffscreen", f"{sdl_num}/+LeftTrigger")
                    settings.set(pad_num, "A", f"{sdl_num}/A")
                    settings.set(pad_num, "B", f"{sdl_num}/B")
            # Guns crosshair
            settings.set(pad_num, "CrosshairScale", system.config.get("duckstation_crosshair", "0"))
            # Mouse
            if system.config.get(f"duckstation_{ctrl_num}") == "PlayStationMouse":
                settings.set(pad_num, "Right", f"{sdl_num}/B")
                settings.set(pad_num, "Left", f"{sdl_num}/A")
                settings.set(pad_num, "RelativeMouseMode", f"{sdl_num}true")

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

        settings.set("CDROM", "AllowBootingWithoutSBIFile", system.config.get("duckstation_boot_without_sbi", "false"))

        ## [UI]
        if not settings.has_section("UI"):
            settings.add_section("UI")
        settings.set("UI", "UnofficialBuildWarningConfirmed", "true")

        # Save config
        with ensure_parents_and_open(settings_path, 'w') as configfile:
            settings.write(configfile)

        # write our own gamecontrollerdb.txt file before launching the game
        dbfile = "/usr/share/duckstation/resources/gamecontrollerdb.txt"
        write_sdl_controller_db(playersControllers, dbfile)

        # check if we're running wayland
        if environ.get("WAYLAND_DISPLAY"):
            qt_qpa_platform = "wayland"
        else:
            qt_qpa_platform = "xcb"

        # use their modified shaderc library
        return Command.Command(
            array=commandArray,
            env={
                "LD_LIBRARY_PATH": "/usr/stenzek-shaderc/lib:/usr/lib",
                "XDG_CONFIG_HOME": CONFIGS,
                "QT_QPA_PLATFORM": qt_qpa_platform,
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

def find_bios(bios_lists: Mapping[str, Sequence[str]]):
    found_bios: dict[str, str] = {}

    try:
        files_lower = {f.name.lower(): f.name for f in BIOS.iterdir()}
    except OSError as e:
        raise BatoceraException(f"Unable to read BIOS directory: {BIOS}") from e

    for region, bios_list in bios_lists.items():
        for bios in bios_list:
            if bios.lower() in files_lower:
                found_bios[region] = files_lower[bios.lower()]
                break

    return found_bios

# Define BIOS lists
bios_lists = {
    "NTSCU": ["scph101.bin", "scph1001.bin", "scph5501.bin", "scph7001.bin", "scph7501.bin"],
    "PAL": ["scph1002.bin", "scph5502.bin", "scph5552.bin", "scph7002.bin", "scph7502.bin", "scph9002.bin", "scph102a.bin", "scph102b.bin"],
    "NTSCJ": ["scph100.bin", "scph1000.bin", "scph3000.bin", "scph3500.bin", "scph5500.bin", "scph7000.bin", "scph7003.bin"],
    "Uni": ["psxonpsp660.bin", "ps1_rom.bin"]
}
