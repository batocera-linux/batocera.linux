from __future__ import annotations

import logging
import re
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser

from ... import Command
from ...batoceraPaths import (
    BIOS,
    CACHE,
    CONFIGS,
    DATAINIT_DIR,
    ROMS,
    configure_emulator,
    ensure_parents_and_open,
    mkdir_if_not_exists,
)
from ...controller import Controllers, generate_sdl_game_controller_config, write_sdl_controller_db
from ...utils import vulkan
from ..Generator import Generator

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...config import SystemConfig
    from ...Emulator import Emulator
    from ...types import HotkeysContext, Resolution

_logger = logging.getLogger(__name__)

_PCSX2X6_BIN_DIR: Final = Path("/usr/pcsx2x6/bin")
_PCSX2X6_RESOURCES_DIR: Final = _PCSX2X6_BIN_DIR / "resources"
_PCSX2X6_CONFIG: Final = CONFIGS / "PCSX2x6"
_PCSX2X6_BIOS: Final = BIOS / "namco2x6"

class Pcsx2x6Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "pcsx2x6",
            "keys": { "exit":          ["KEY_LEFTALT", "KEY_F4"],
                      "menu":          "KEY_ESC",
                      "pause":         "KEY_ESC",
                      "save_state":    "KEY_F1",
                      "restore_state": "KEY_F3",
                      "previous_slot": [ "KEY_LEFTSHIFT", "KEY_F2" ],
                      "next_slot":     "KEY_F2"
                     }
        }

    def getInGameRatio(self, config, gameResolution, rom):
        config_ratio = getGfxRatioFromConfig(config, gameResolution)
        if config_ratio == "16:9" or (config_ratio == "Stretch" and gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1)):
            return 16/9
        return 4/3

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        pcsx2Patches = _PCSX2X6_BIOS / "patches.zip"

        # Remove older config files if present
        inisDir = _PCSX2X6_CONFIG / "inis"
        files_to_remove = ["PCSX2_ui.ini", "PCSX2_vm.ini", "GS.ini"]
        for filename in files_to_remove:
            file_path = inisDir / filename
            if file_path.exists():
                file_path.unlink()

        # Config files
        configureReg(_PCSX2X6_CONFIG)
        configureINI(_PCSX2X6_CONFIG, _PCSX2X6_BIOS, system, rom, playersControllers, metadata)
        configureAudio(_PCSX2X6_CONFIG)

        # write our own game_controller_db.txt file before launching the game
        dbfile = _PCSX2X6_CONFIG / "game_controller_db.txt"
        write_sdl_controller_db(playersControllers, dbfile)

        commandArray = ["/usr/pcsx2x6/bin/pcsx2x6-qt"] if configure_emulator(rom) else \
              ["/usr/pcsx2x6/bin/pcsx2x6-qt", "-nogui", rom]

        with Path("/proc/cpuinfo").open() as cpuinfo:
            if not re.search(r'^flags\s*:.*\ssse4_1\W', cpuinfo.read(), re.MULTILINE):
                _logger.warning("CPU does not support SSE4.1 which is required by pcsx2x6.  The emulator will likely crash with SIGILL (illegal instruction).")

        envcmd: dict[str, str | Path] = {
            "XDG_CONFIG_HOME": CONFIGS,
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
        }

        # ensure we have the patches.zip file to avoid message.
        mkdir_if_not_exists(pcsx2Patches.parent)
        if not pcsx2Patches.exists():
            shutil.copy(DATAINIT_DIR / "bios" / "namco2x6" / "patches.zip", pcsx2Patches)

        # state_slot option
        if state_filename := system.config.get('state_filename'):
            commandArray.extend(["-statefile", state_filename])

        if state_slot := system.config.get_str('state_slot'):
            commandArray.extend(["-stateindex", state_slot])

        return Command.Command(
            array=commandArray,
            env=envcmd
        )

def getGfxRatioFromConfig(config: SystemConfig, gameResolution: Resolution):
    # 2: 4:3 ; 1: 16:9
    ratio = config.get("pcsx2x6_ratio")
    if ratio == "16:9":
        return "16:9"
    if ratio == "full":
        return "Stretch"
    return "4:3"

def configureReg(config_directory: Path) -> None:
    with ensure_parents_and_open(config_directory / "PCSX2-reg.ini", "w") as f:
        f.write("DocumentsFolderMode=User\n")
        f.write(f"CustomDocumentsFolder={_PCSX2X6_BIN_DIR}\n")
        f.write("UseDefaultSettingsFolder=enabled\n")
        f.write(f"SettingsFolder={config_directory / 'inis'}\n")
        f.write(f"Install_Dir={_PCSX2X6_BIN_DIR}\n")
        f.write("RunWizard=0\n")

def configureAudio(config_directory: Path) -> None:
    configFileName = config_directory / 'inis' / "spu2-x.ini"
    mkdir_if_not_exists(configFileName.parent)

    # Keep the custom files
    if configFileName.exists():
        return

    f = configFileName.open("w")
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

def configureINI(config_directory: Path, bios_directory: Path, system: Emulator, rom: Path, controllers: Controllers, metadata: Mapping[str, str]) -> None:
    configFileName = config_directory / 'inis' / "PCSX2.ini"

    mkdir_if_not_exists(configFileName.parent)

    if not configFileName.is_file():
        with configFileName.open("w") as f:
            f.write("[UI]\n")

    pcsx2x6INIConfig = CaseSensitiveConfigParser(interpolation=None)

    if configFileName.is_file():
        pcsx2x6INIConfig.read(configFileName)

    ## [UI]
    if not pcsx2x6INIConfig.has_section("UI"):
        pcsx2x6INIConfig.add_section("UI")

    # set the settings we want always enabled
    pcsx2x6INIConfig.set("UI", "SettingsVersion", "1")
    pcsx2x6INIConfig.set("UI", "InhibitScreensaver", "true")
    pcsx2x6INIConfig.set("UI", "ConfirmShutdown", "false")
    pcsx2x6INIConfig.set("UI", "StartPaused", "false")
    pcsx2x6INIConfig.set("UI", "PauseOnFocusLoss", "false")
    pcsx2x6INIConfig.set("UI", "StartFullscreen", "true")
    pcsx2x6INIConfig.set("UI", "HideMouseCursor", "true")
    pcsx2x6INIConfig.set("UI", "RenderToSeparateWindow", "false")
    pcsx2x6INIConfig.set("UI", "HideMainWindowWhenRunning", "true")
    pcsx2x6INIConfig.set("UI", "DoubleClickTogglesFullscreen", "false")

    # clear to not have the window anywhere when switching from multi to single screen and vice and versa
    for opt in ["MainWindowGeometry", "MainWindowState", "DisplayWindowGeometry"]:
        if pcsx2x6INIConfig.has_section("UI") and pcsx2x6INIConfig.has_option("UI", opt):
            pcsx2x6INIConfig.remove_option("UI", opt)

    ## [Folders]
    if not pcsx2x6INIConfig.has_section("Folders"):
        pcsx2x6INIConfig.add_section("Folders")

    # remove inconsistent SaveStates casing if it exists
    pcsx2x6INIConfig.remove_option("Folders", "SaveStates")

    # set the folders we want
    pcsx2x6INIConfig.set("Folders", "Bios", "../../../bios/namco2x6")
    pcsx2x6INIConfig.set("Folders", "Snapshots", "../../../screenshots")
    pcsx2x6INIConfig.set("Folders", "Savestates", "../../../saves/namco2x6/pcsx2x6/sstates")
    pcsx2x6INIConfig.set("Folders", "MemoryCards", "../../../saves/namco2x6/pcsx2x6")
    pcsx2x6INIConfig.set("Folders", "Logs", "../../logs")
    pcsx2x6INIConfig.set("Folders", "Cheats", "../../../cheats/namco2x6")
    pcsx2x6INIConfig.set("Folders", "CheatsWS", "../../../cheats/namco2x6/cheats_ws")
    pcsx2x6INIConfig.set("Folders", "CheatsNI", "../../../cheats/namco2x6/cheats_ni")
    pcsx2x6INIConfig.set("Folders", "Cache", "../../cache/namco2x6")
    pcsx2x6INIConfig.set("Folders", "Textures", "textures")
    pcsx2x6INIConfig.set("Folders", "InputProfiles", "inputprofiles")
    pcsx2x6INIConfig.set("Folders", "Videos", "../../../saves/namco2x6/pcsx2x6/videos")

    # create cache folder
    mkdir_if_not_exists(CACHE / "namco2x6")

    ## [EmuCore]
    if not pcsx2x6INIConfig.has_section("EmuCore"):
        pcsx2x6INIConfig.add_section("EmuCore")

    # set the settings we want always enabled
    pcsx2x6INIConfig.set("EmuCore", "EnableDiscordPresence", "false")

    # Cheats
    #pcsx2x6INIConfig.set("EmuCore", "EnableCheats", system.config.get('pcsx2x6_cheats', "false"))

    # Widescreen Patches
    #pcsx2x6INIConfig.set("EmuCore", "EnableWideScreenPatches", system.config.get("pcsx2x6_EnableWideScreenPatches", "false"))

    # No-interlacing Patches
    #pcsx2x6INIConfig.set("EmuCore", "EnableNoInterlacingPatches", system.config.get("pcsx2x6_interlacing_patches", "false"))

    ## [Achievements]
    if not pcsx2x6INIConfig.has_section("Achievements"):
        pcsx2x6INIConfig.add_section("Achievements")
    pcsx2x6INIConfig.set("Achievements", "Enabled", "false")
    if system.config.get_bool('retroachievements'):
        username  = system.config.get('retroachievements.username', "")
        token     = system.config.get('retroachievements.token', "")
        pcsx2x6INIConfig.set("Achievements", "Enabled", "true")
        pcsx2x6INIConfig.set("Achievements", "Username", username)
        pcsx2x6INIConfig.set("Achievements", "Token", token)
        pcsx2x6INIConfig.set("Achievements", "LoginTimestamp", str(int(time.time())))
        pcsx2x6INIConfig.set("Achievements", "ChallengeMode", system.config.get_bool('retroachievements.hardcore', return_values=("true", "false")))
        pcsx2x6INIConfig.set("Achievements", "PrimedIndicators", system.config.get_bool('retroachievements.challenge_indicators', return_values=("true", "false")))
        pcsx2x6INIConfig.set("Achievements", "RichPresence", system.config.get_bool('retroachievements.richpresence', return_values=("true", "false")))
        pcsx2x6INIConfig.set("Achievements", "Leaderboards", system.config.get_bool('retroachievements.leaderboards', return_values=("true", "false")))
        pcsx2x6INIConfig.set("Achievements", "EncoreMode", system.config.get_bool('retroachievements.encore', return_values=("true", "false")))
        pcsx2x6INIConfig.set("Achievements", "UnofficialTestMode", system.config.get_bool('retroachievements.unofficial', return_values=("true", "false")))
    # set other settings
    pcsx2x6INIConfig.set("Achievements", "TestMode", "false")
    pcsx2x6INIConfig.set("Achievements", "UnofficialTestMode", "false")
    pcsx2x6INIConfig.set("Achievements", "Notifications", "true")
    pcsx2x6INIConfig.set("Achievements", "SoundEffects", "true")

    ## [Filenames]
    if not pcsx2x6INIConfig.has_section("Filenames"):
        pcsx2x6INIConfig.add_section("Filenames")

    # Read rom metadata/info file to find the platform value
    platform = "256"
    if rom.is_file():
        try:
            with rom.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned.startswith("platform"):
                        parts = [p.strip() for p in cleaned.split("=", 1)]
                        if len(parts) == 2 and parts[0] == "platform":
                            platform = parts[1]
                            break
        except Exception as e:
            _logger.warning("Could not read platform from ROM file %s: %s", rom, e)

    # Use r27v1602f.7d for 246 platform, default to r27v1602f.8g (for 256 or others)
    bios_file = "r27v1602f.7d" if platform == "246" else "r27v1602f.8g"
    pcsx2x6INIConfig.set("Filenames", "BIOS", bios_file)

    ## [EMUCORE/GS]
    if not pcsx2x6INIConfig.has_section("EmuCore/GS"):
        pcsx2x6INIConfig.add_section("EmuCore/GS")

    ## [EMUCORE/Speedhacks]
    if not pcsx2x6INIConfig.has_section("EmuCore/Speedhacks"):
        pcsx2x6INIConfig.add_section("EmuCore/Speedhacks")

    # Renderer
    # Check Vulkan first to be sure
    if vulkan.is_available():
        _logger.debug("Vulkan driver is available on the system.")
        renderer = "-1"

        if gfxbackend := system.config.get("pcsx2x6_gfxbackend"):
            if gfxbackend == "12":
                _logger.debug("User selected OpenGL")
            if gfxbackend == "13":
                _logger.debug("User selected Software! Man you must have a fast CPU!")
            elif gfxbackend == "14":
                _logger.debug("User selected Vulkan")
                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_name = vulkan.get_discrete_gpu_name()
                    if discrete_name:
                        _logger.debug("Using Discrete GPU Name: %s for PCSX2x6", discrete_name)
                        pcsx2x6INIConfig.set("EmuCore/GS", "Adapter", discrete_name)
                    else:
                        _logger.debug("Couldn't get discrete GPU Name")
                        pcsx2x6INIConfig.set("EmuCore/GS", "Adapter", "(Default)")
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
                    pcsx2x6INIConfig.set("EmuCore/GS", "Adapter", "(Default)")
            renderer = gfxbackend
        else:
            _logger.debug("User selected to Automatic")

        pcsx2x6INIConfig.set("EmuCore/GS", "Renderer", renderer)
    else:
        _logger.debug("Vulkan driver is not available on the system. Falling back to Automatic")
        pcsx2x6INIConfig.set("EmuCore/GS", "Renderer", "-1")

    # Ratio
    pcsx2x6INIConfig.set("EmuCore/GS", "AspectRatio", system.config.get("pcsx2x6_ratio", "Auto 4:3/3:2"))

    # Vsync
    pcsx2x6INIConfig.set("EmuCore/GS","VsyncEnable", system.config.get("pcsx2x6_vsync", "0"))

    # Resolution
    pcsx2x6INIConfig.set("EmuCore/GS", "upscale_multiplier", system.config.get("pcsx2x6_resolution", "1"))

    # FXAA
    pcsx2x6INIConfig.set("EmuCore/GS", "fxaa", system.config.get("pcsx2x6_fxaa", "false"))

    # FMV Ratio
    pcsx2x6INIConfig.set("EmuCore/GS", "FMVAspectRatioSwitch", system.config.get("pcsx2x6_fmv_ratio", "Auto 4:3/3:2"))

    # Mipmapping
    pcsx2x6INIConfig.set("EmuCore/GS", "mipmap_hw", system.config.get("pcsx2x6_mipmapping", "-1"))

    # Trilinear Filtering
    pcsx2x6INIConfig.set("EmuCore/GS", "TriFilter", system.config.get("pcsx2x6_trilinear_filtering", "-1"))

    # Anisotropic Filtering
    pcsx2x6INIConfig.set("EmuCore/GS", "MaxAnisotropy", system.config.get("pcsx2x6_anisotropic_filtering", "0"))

    # Dithering
    pcsx2x6INIConfig.set("EmuCore/GS", "dithering_ps2", system.config.get("pcsx2x6_dithering", "2"))

    # Texture Preloading
    pcsx2x6INIConfig.set("EmuCore/GS", "texture_preloading", system.config.get("pcsx2x6_texture_loading", "2"))

    # Deinterlacing
    pcsx2x6INIConfig.set("EmuCore/GS", "deinterlace_mode", system.config.get("pcsx2x6_deinterlacing", "0"))

    # Anti-Blur
    pcsx2x6INIConfig.set("EmuCore/GS", "pcrtc_antiblur", system.config.get("pcsx2x6_blur", "true"))

    # Integer Scaling
    pcsx2x6INIConfig.set("EmuCore/GS", "IntegerScaling", system.config.get("pcsx2x6_scaling", "false"))

    # Blending Accuracy
    pcsx2x6INIConfig.set("EmuCore/GS", "accurate_blending_unit", system.config.get("pcsx2x6_blending", "1"))

    # Texture Filtering
    pcsx2x6INIConfig.set("EmuCore/GS", "filter", system.config.get("pcsx2x6_texture_filtering", "2"))

    # Bilinear Filtering
    pcsx2x6INIConfig.set("EmuCore/GS", "linear_present_mode", system.config.get("pcsx2x6_bilinear_filtering", "1"))

    # Load Texture Replacements
    #pcsx2x6INIConfig.set("EmuCore/GS", "LoadTextureReplacements", system.config.get("pcsx2x6_texture_replacements", "false"))

    # OSD messages
    osd_enabled = system.config.get("pcsx2x6_osd_messages", "true")
    pcsx2x6INIConfig.set("EmuCore/GS", "OsdShowMessages", osd_enabled)

    # OSD Messages Position
    pcsx2x6INIConfig.set("EmuCore/GS", "OsdMessagesPos", "0" if osd_enabled == "false" else system.config.get("pcsx2x6_osd_messages_position", "2"))

    # OSD Performance Position
    pcsx2x6INIConfig.set("EmuCore/GS", "OsdPerformancePos", system.config.get("pcsx2x6_osd_performance_position", "0"))

    # Crop Overscan
    cropOverscan = "3" if system.config.get_bool("pcsx2x6_overscan") else "0"

    pcsx2x6INIConfig.set("EmuCore/GS", "CropLeft", cropOverscan)
    pcsx2x6INIConfig.set("EmuCore/GS", "CropTop", cropOverscan)
    pcsx2x6INIConfig.set("EmuCore/GS", "CropRight", cropOverscan)
    pcsx2x6INIConfig.set("EmuCore/GS", "CropBottom", cropOverscan)

    # TV Shader
    pcsx2x6INIConfig.set("EmuCore", "TVShader", system.config.get("pcsx2x6_shaderset", "0"))

    pcsx2x6INIConfig.set("EmuCore", "AutoIncrementSlot", system.config.get_bool('incrementalsavestates', True, return_values=("true", "false")))

    pcsx2x6INIConfig.set("EmuCore", "SaveStateOnShutdown", system.config.get_bool('autosave', return_values=("true", "false")))

    # VU thread speedhack
    pcsx2x6INIConfig.set("EmuCore/Speedhacks", "vuThread", system.config.get_bool("pcsx2x6_vuthread", return_values=("true", "false")))

    # EE Cycle Rate speedhack
    pcsx2x6INIConfig.set("EmuCore/Speedhacks", "EECycleRate", system.config.get("pcsx2x6_eecyclerate", "0"))

    ## [InputSources]
    if not pcsx2x6INIConfig.has_section("InputSources"):
        pcsx2x6INIConfig.add_section("InputSources")

    pcsx2x6INIConfig.set("InputSources", "Keyboard", "true")
    pcsx2x6INIConfig.set("InputSources", "Mouse", "true")
    pcsx2x6INIConfig.set("InputSources", "SDL", "true")

    ## [Hotkeys]
    if not pcsx2x6INIConfig.has_section("Hotkeys"):
        pcsx2x6INIConfig.add_section("Hotkeys")

    pcsx2x6INIConfig.set("Hotkeys", "ToggleFullscreen", "Keyboard/Alt & Keyboard/Return")
    pcsx2x6INIConfig.set("Hotkeys", "CycleAspectRatio", "Keyboard/F6")
    pcsx2x6INIConfig.set("Hotkeys", "CycleInterlaceMode", "Keyboard/F5")
    pcsx2x6INIConfig.set("Hotkeys", "CycleMipmapMode", "Keyboard/Insert")
    pcsx2x6INIConfig.set("Hotkeys", "GSDumpMultiFrame", "Keyboard/Control & Keyboard/Shift & Keyboard/F8")
    pcsx2x6INIConfig.set("Hotkeys", "Screenshot", "Keyboard/F8")
    pcsx2x6INIConfig.set("Hotkeys", "GSDumpSingleFrame", "Keyboard/Shift & Keyboard/F8")
    pcsx2x6INIConfig.set("Hotkeys", "ToggleSoftwareRendering", "Keyboard/F9")
    pcsx2x6INIConfig.set("Hotkeys", "ZoomIn", "Keyboard/Control & Keyboard/Plus")
    pcsx2x6INIConfig.set("Hotkeys", "ZoomOut", "Keyboard/Control & Keyboard/Minus")
    pcsx2x6INIConfig.set("Hotkeys", "InputRecToggleMode", "Keyboard/Shift & Keyboard/R")
    pcsx2x6INIConfig.set("Hotkeys", "LoadStateFromSlot", "Keyboard/F3")
    pcsx2x6INIConfig.set("Hotkeys", "SaveStateToSlot", "Keyboard/F1")
    pcsx2x6INIConfig.set("Hotkeys", "NextSaveStateSlot", "Keyboard/F2")
    pcsx2x6INIConfig.set("Hotkeys", "PreviousSaveStateSlot", "Keyboard/Shift & Keyboard/F2")
    pcsx2x6INIConfig.set("Hotkeys", "OpenPauseMenu", "Keyboard/Escape")
    pcsx2x6INIConfig.set("Hotkeys", "ToggleFrameLimit", "Keyboard/F4")
    pcsx2x6INIConfig.set("Hotkeys", "TogglePause", "Keyboard/Space")
    pcsx2x6INIConfig.set("Hotkeys", "ToggleSlowMotion", "Keyboard/Shift & Keyboard/Backtab")
    pcsx2x6INIConfig.set("Hotkeys", "ToggleTurbo", "Keyboard/Tab")
    pcsx2x6INIConfig.set("Hotkeys", "HoldTurbo", "Keyboard/Period")

    # Clear old USB sections to prevent lingering device configuration values
    for usb_section in ["USB1", "USB2"]:
        if pcsx2x6INIConfig.has_section(usb_section):
            pcsx2x6INIConfig.remove_section(usb_section)

    ## [Pad]
    if not pcsx2x6INIConfig.has_section("Pad"):
        pcsx2x6INIConfig.add_section("Pad")

    pcsx2x6INIConfig.set("Pad", "MultitapPort1", "false")
    pcsx2x6INIConfig.set("Pad", "MultitapPort2", "false")

    # remove the previous [Padx] sections to avoid phantom controllers
    section_names = ["Pad1", "Pad2", "Pad3", "Pad4", "Pad5", "Pad6", "Pad7", "Pad8"]
    for section_name in section_names:
        if pcsx2x6INIConfig.has_section(section_name):
            pcsx2x6INIConfig.remove_section(section_name)

    # Extract Player 1 and Player 2 controller objects safely
    pad1 = controllers[0] if len(controllers) > 0 else None
    pad2 = controllers[1] if len(controllers) > 1 else None

    p1_sdl = f"SDL-{pad1.index}" if pad1 is not None else "SDL-0"
    p2_sdl = f"SDL-{pad2.index}" if pad2 is not None else "SDL-1"

    pcsx2x6INIConfig.set("InputSources", "SDLControllerEnhancedMode", "false")

    ## [JVS]
    if not pcsx2x6INIConfig.has_section("JVS"):
        pcsx2x6INIConfig.add_section("JVS")

    jvs_mappings = {
        "TestMode": "false",
        "VideoVoltage": "true",
        "MonitorSyncFrequency": "true",
        "VideoSyncSplit": "true",
        "SindenBorderEnabled": "false",
        "SindenBorderMode": "0",
        "SindenBorderThickness": "10",

        # Player 1 controls
        "P1_Up": f"{p1_sdl}/DPadUp",
        "P1_Down": f"{p1_sdl}/DPadDown",
        "P1_Left": f"{p1_sdl}/DPadLeft",
        "P1_Right": f"{p1_sdl}/DPadRight",
        "Tekken_LeftPunch_P1": f"{p1_sdl}/FaceWest",
        "Tekken_RightPunch_P1": f"{p1_sdl}/FaceNorth",
        "Tekken_LeftKick_P1": f"{p1_sdl}/FaceSouth",
        "Tekken_RightKick_P1": f"{p1_sdl}/FaceEast",
        "SoulCal_Horizontal_P1": f"{p1_sdl}/FaceWest",
        "SoulCal_Vertical_P1": f"{p1_sdl}/FaceNorth",
        "SoulCal_Kick_P1": f"{p1_sdl}/FaceEast",
        "SoulCal_Guard_P1": f"{p1_sdl}/FaceSouth",
        "Gundam_Shoot_P1": f"{p1_sdl}/FaceWest",
        "Gundam_Melee_P1": f"{p1_sdl}/FaceNorth",
        "Gundam_Jump_P1": f"{p1_sdl}/FaceSouth",
        "Gundam_Target_P1": f"{p1_sdl}/FaceEast",
        "BloodyRoar_Punch_P1": f"{p1_sdl}/FaceWest",
        "BloodyRoar_Kick_P1": f"{p1_sdl}/FaceSouth",
        "BloodyRoar_Beast_P1": f"{p1_sdl}/FaceEast",
        "BloodyRoar_Block_P1": f"{p1_sdl}/FaceNorth",
        "Fate_Weak_P1": f"{p1_sdl}/FaceWest",
        "Fate_Medium_P1": f"{p1_sdl}/FaceNorth",
        "Fate_Strong_P1": f"{p1_sdl}/FaceEast",
        "Fate_Guard_P1": f"{p1_sdl}/FaceSouth",
        "Kinnikuman_Attack_P1": f"{p1_sdl}/FaceWest",
        "Kinnikuman_ThrowGrab_P1": f"{p1_sdl}/FaceNorth",
        "Kinnikuman_Special_P1": f"{p1_sdl}/FaceEast",
        "Kinnikuman_Guard_P1": f"{p1_sdl}/FaceSouth",
        "PrideGP_LeftPunch_P1": f"{p1_sdl}/FaceWest",
        "PrideGP_RightPunch_P1": f"{p1_sdl}/FaceNorth",
        "PrideGP_LeftKick_P1": f"{p1_sdl}/FaceSouth",
        "PrideGP_RightKick_P1": f"{p1_sdl}/FaceEast",
        "Basara_Weak_P1": f"{p1_sdl}/FaceWest",
        "Basara_Medium_P1": f"{p1_sdl}/FaceNorth",
        "Basara_Strong_P1": f"{p1_sdl}/FaceEast",
        "Basara_Striker_P1": f"{p1_sdl}/FaceSouth",
        "DragonBallZ_Light_P1": f"{p1_sdl}/FaceWest",
        "DragonBallZ_Heavy_P1": f"{p1_sdl}/FaceNorth",
        "DragonBallZ_Guard_P1": f"{p1_sdl}/FaceSouth",
        "DragonBallZ_Jump_P1": f"{p1_sdl}/FaceEast",
        "YuYu_Punch_P1": f"{p1_sdl}/FaceWest",
        "YuYu_Kick_P1": f"{p1_sdl}/FaceNorth",
        "YuYu_Guard_P1": f"{p1_sdl}/FaceSouth",
        "SixButton_LightPunch_P1": f"{p1_sdl}/FaceWest",
        "SixButton_MediumPunch_P1": f"{p1_sdl}/FaceNorth",
        "SixButton_HeavyPunch_P1": f"{p1_sdl}/LeftShoulder",
        "SixButton_LightKick_P1": f"{p1_sdl}/FaceSouth",
        "SixButton_MediumKick_P1": f"{p1_sdl}/FaceEast",
        "SixButton_HeavyKick_P1": f"{p1_sdl}/RightShoulder",
        "SteerLeft": f"{p1_sdl}/-LeftX",
        "SteerRight": f"{p1_sdl}/+LeftX",
        "Gas": f"{p1_sdl}/+RightTrigger",
        "Brake": f"{p1_sdl}/+LeftTrigger",
        "Racing_ShiftUp_P1": f"{p1_sdl}/RightShoulder",
        "Racing_ShiftDown_P1": f"{p1_sdl}/LeftShoulder",
        "Racing_View_P1": f"{p1_sdl}/FaceNorth",
        "BG3_ShiftUp_P1": f"{p1_sdl}/RightShoulder",
        "BG3_ShiftDown_P1": f"{p1_sdl}/LeftShoulder",
        "BG3_View_P1": f"{p1_sdl}/FaceNorth",
        "BG3_Sidebrake_P1": f"{p1_sdl}/FaceWest",
        "BG3_Hazard_P1": f"{p1_sdl}/FaceEast",
        "P1_DonLeft": f"{p1_sdl}/FaceWest",
        "P1_DonRight": f"{p1_sdl}/FaceNorth",
        "P1_KaLeft": f"{p1_sdl}/FaceSouth",
        "P1_KaRight": f"{p1_sdl}/FaceEast",
        "P1_LLeverUp": f"{p1_sdl}/-LeftY",
        "P1_LLeverDown": f"{p1_sdl}/+LeftY",
        "P1_LLeverLeft": f"{p1_sdl}/-LeftX",
        "P1_LLeverRight": f"{p1_sdl}/+LeftX",
        "P1_RLeverUp": f"{p1_sdl}/-RightY",
        "P1_RLeverDown": f"{p1_sdl}/+RightY",
        "P1_RLeverLeft": f"{p1_sdl}/-RightX",
        "P1_RLeverRight": f"{p1_sdl}/+RightX",
        "P1_LTrigger": f"{p1_sdl}/+LeftTrigger",
        "P1_RTrigger": f"{p1_sdl}/+RightTrigger",
        "P1_LButton": f"{p1_sdl}/LeftShoulder",
        "P1_RButton": f"{p1_sdl}/RightShoulder",
        "Smash_TopSpin_P1": f"{p1_sdl}/FaceSouth",
        "Smash_Slice_P1": f"{p1_sdl}/FaceWest",
        "Technic_Activate_P1": f"{p1_sdl}/FaceWest",
        "Technic_Action_P1": f"{p1_sdl}/FaceSouth",
        "Technic_Super_P1": f"{p1_sdl}/FaceEast",
        "Baseball_A_P1": f"{p1_sdl}/FaceSouth",
        "Baseball_B_P1": f"{p1_sdl}/FaceWest",
        "Baseball_C_P1": f"{p1_sdl}/FaceNorth",
        "GundamQuiz_Target_P1": f"{p1_sdl}/FaceEast",
        "GundamQuiz_Shoot_P1": f"{p1_sdl}/FaceWest",
        "GundamQuiz_Melee_P1": f"{p1_sdl}/FaceNorth",
        "GundamQuiz_Jump_P1": f"{p1_sdl}/FaceSouth",
        "Inufuku_1_P1": f"{p1_sdl}/FaceNorth",
        "Inufuku_2_P1": f"{p1_sdl}/FaceSouth",
        "Inufuku_3_P1": f"{p1_sdl}/FaceWest",
        "Inufuku_4_P1": f"{p1_sdl}/FaceEast",

        # Player 2 controls
        "P2_Up": f"{p2_sdl}/DPadUp",
        "P2_Down": f"{p2_sdl}/DPadDown",
        "P2_Left": f"{p2_sdl}/DPadLeft",
        "P2_Right": f"{p2_sdl}/DPadRight",
        "Tekken_LeftPunch_P2": f"{p2_sdl}/FaceWest",
        "Tekken_RightPunch_P2": f"{p2_sdl}/FaceNorth",
        "Tekken_LeftKick_P2": f"{p2_sdl}/FaceSouth",
        "Tekken_RightKick_P2": f"{p2_sdl}/FaceEast",
        "SoulCal_Horizontal_P2": f"{p2_sdl}/FaceWest",
        "SoulCal_Vertical_P2": f"{p2_sdl}/FaceNorth",
        "SoulCal_Kick_P2": f"{p2_sdl}/FaceEast",
        "SoulCal_Guard_P2": f"{p2_sdl}/FaceSouth",
        "BloodyRoar_Punch_P2": f"{p2_sdl}/FaceWest",
        "BloodyRoar_Kick_P2": f"{p2_sdl}/FaceSouth",
        "BloodyRoar_Beast_P2": f"{p2_sdl}/FaceEast",
        "BloodyRoar_Block_P2": f"{p2_sdl}/FaceNorth",
        "Fate_Weak_P2": f"{p2_sdl}/FaceWest",
        "Fate_Medium_P2": f"{p2_sdl}/FaceNorth",
        "Fate_Strong_P2": f"{p2_sdl}/FaceEast",
        "Fate_Guard_P2": f"{p2_sdl}/FaceSouth",
        "Kinnikuman_Attack_P2": f"{p2_sdl}/FaceWest",
        "Kinnikuman_ThrowGrab_P2": f"{p2_sdl}/FaceNorth",
        "Kinnikuman_Special_P2": f"{p2_sdl}/FaceEast",
        "Kinnikuman_Guard_P2": f"{p2_sdl}/FaceSouth",
        "PrideGP_LeftPunch_P2": f"{p2_sdl}/FaceWest",
        "PrideGP_RightPunch_P2": f"{p2_sdl}/FaceNorth",
        "PrideGP_LeftKick_P2": f"{p2_sdl}/FaceSouth",
        "PrideGP_RightKick_P2": f"{p2_sdl}/FaceEast",
        "Basara_Weak_P2": f"{p2_sdl}/FaceWest",
        "Basara_Medium_P2": f"{p2_sdl}/FaceNorth",
        "Basara_Strong_P2": f"{p2_sdl}/FaceEast",
        "Basara_Striker_P2": f"{p2_sdl}/FaceSouth",
        "DragonBallZ_Light_P2": f"{p2_sdl}/FaceWest",
        "DragonBallZ_Heavy_P2": f"{p2_sdl}/FaceNorth",
        "DragonBallZ_Guard_P2": f"{p2_sdl}/FaceSouth",
        "DragonBallZ_Jump_P2": f"{p2_sdl}/FaceEast",
        "YuYu_Punch_P2": f"{p2_sdl}/FaceWest",
        "YuYu_Kick_P2": f"{p2_sdl}/FaceNorth",
        "YuYu_Guard_P2": f"{p2_sdl}/FaceSouth",
        "SixButton_LightPunch_P2": f"{p2_sdl}/FaceWest",
        "SixButton_MediumPunch_P2": f"{p2_sdl}/FaceNorth",
        "SixButton_HeavyPunch_P2": f"{p2_sdl}/LeftShoulder",
        "SixButton_LightKick_P2": f"{p2_sdl}/FaceSouth",
        "SixButton_MediumKick_P2": f"{p2_sdl}/FaceEast",
        "SixButton_HeavyKick_P2": f"{p2_sdl}/RightShoulder",
        "P2_DonLeft": f"{p2_sdl}/FaceWest",
        "P2_DonRight": f"{p2_sdl}/FaceNorth",
        "P2_KaLeft": f"{p2_sdl}/FaceSouth",
        "P2_KaRight": f"{p2_sdl}/FaceEast",
        "Smash_TopSpin_P2": f"{p2_sdl}/FaceSouth",
        "Smash_Slice_P2": f"{p2_sdl}/FaceWest",
        "Technic_Activate_P2": f"{p2_sdl}/FaceWest",
        "Technic_Action_P2": f"{p2_sdl}/FaceSouth",
        "Technic_Super_P2": f"{p2_sdl}/FaceEast",
        "Baseball_A_P2": f"{p2_sdl}/FaceSouth",
        "Baseball_B_P2": f"{p2_sdl}/FaceWest",
        "Baseball_C_P2": f"{p2_sdl}/FaceNorth",
        "GundamQuiz_Target_P2": f"{p2_sdl}/FaceEast",
        "GundamQuiz_Shoot_P2": f"{p2_sdl}/FaceWest",
        "GundamQuiz_Melee_P2": f"{p2_sdl}/FaceNorth",
        "GundamQuiz_Jump_P2": f"{p2_sdl}/FaceSouth",
        "Inufuku_1_P2": f"{p2_sdl}/FaceNorth",
        "Inufuku_2_P2": f"{p2_sdl}/FaceSouth",
        "Inufuku_3_P2": f"{p2_sdl}/FaceWest",
        "Inufuku_4_P2": f"{p2_sdl}/FaceEast",

        # Generic & Special buttons mapping
        "P1_Button1": f"{p1_sdl}/FaceSouth",
        "Coin1": f"{p1_sdl}/Back",
        "P1_Start": f"{p1_sdl}/Start"
    }

    for k, v in jvs_mappings.items():
        pcsx2x6INIConfig.set("JVS", k, v)

    ## [GameList]
    if not pcsx2x6INIConfig.has_section("GameList"):
        pcsx2x6INIConfig.add_section("GameList")

    pcsx2x6INIConfig.set("GameList", "RecursivePaths", str(ROMS / "namco2x6"))

    with configFileName.open('w') as configfile:
        pcsx2x6INIConfig.write(configfile)
