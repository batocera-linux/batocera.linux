from __future__ import annotations

import json
import logging
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, cast

from ... import controllersConfig
from ...batoceraPaths import DEFAULTS_DIR, ES_SETTINGS, SAVES, mkdir_if_not_exists
from ...controller import Controller
from ...settings.unixSettings import UnixSettings
from ...utils import bezels as bezelsUtil, videoMode, vulkan
from ..hatari.hatariGenerator import HATARI_CONFIG
from . import libretroMAMEConfig, libretroOptions
from .libretroPaths import (
    RETROARCH_CONFIG,
    RETROARCH_CORE_CUSTOM,
    RETROARCH_OVERLAY_CONFIG,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...config import SystemConfig
    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...generators.Generator import Generator
    from ...gun import Gun, Guns
    from ...types import BezelInfo, DeviceInfoMapping, Resolution

_logger = logging.getLogger(__name__)


class _GunMappingItem(TypedDict):
    device: NotRequired[int]
    p1: NotRequired[int]
    p2: NotRequired[int]
    p3: NotRequired[int]
    p4: NotRequired[int]
    gameDependant: NotRequired[list[dict[str, Any]]]


# Return value for es invertedbuttons
def getInvertButtonsValue() -> bool:
    try:
        tree = ET.parse(ES_SETTINGS)
        root = tree.getroot()
        # Find the InvertButtons element and return value
        elem = root.find(".//bool[@name='InvertButtons']")
        if elem is not None:
            return elem.get('value') == 'true'
        return False  # Return False if not found
    except Exception:
        return False # when file is not yet here or malformed

# return true if the option is considered defined
def defined(key: str, dict: Mapping[str, Any] | SystemConfig, /) -> bool:
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0


# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L188
ratioIndexes = ["4/3", "16/9", "16/10", "16/15", "21/9", "1/1", "2/1", "3/2", "3/4", "4/1", "9/16", "5/4", "6/5", "7/9", "8/3",
                "8/7", "19/12", "19/14", "30/17", "32/9", "config", "squarepixel", "core", "custom", "full"]

# Define system emulated by bluemsx core
systemToBluemsx = {'msx': '"MSX2"', 'msx1': '"MSX2"', 'msx2': '"MSX2"', 'colecovision': '"COL - ColecoVision"' }

# Define Retroarch Core compatible with retroachievements
# List taken from https://docs.libretro.com/guides/retroachievements/#cores-compatibility
coreToRetroachievements = {'arduous', 'beetle-saturn', 'blastem', 'bluemsx', 'bsnes', 'bsnes_hd', 'cap32', 'desmume', 'duckstation', 'fbneo', 'fceumm', 'flycast', 'flycastvl', 'freechaf', 'freeintv', 'gambatte', 'genesisplusgx', 'genesisplusgx-expanded', 'genesisplusgx-wide','handy', 'kronos', 'mednafen_lynx', 'mednafen_ngp', 'mednafen_psx', 'mednafen_supergrafx', 'mednafen_wswan', 'melonds', 'mesen', 'mesens', 'mgba', 'mupen64plus-next', 'neocd', 'o2em', 'opera', 'parallel_n64', 'pce', 'pce_fast', 'pcfx', 'pcsx_rearmed', 'picodrive', 'pokemini', 'potator', 'ppsspp', 'prosystem', 'quasi88', 'snes9x', 'sameduck', 'snes9x_next', 'stella', 'stella2014', 'swanstation', 'uzem', 'vb', 'vba-m', 'vecx', 'virtualjaguar', 'wasm4'}

# Define systems NOT compatible with rewind option
systemNoRewind = {'sega32x', 'psx', 'zxspectrum', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'saturn', 'dice'}
# 'o2em', 'mame', 'neogeocd', 'fbneo'

# Define systems NOT compatible with run-ahead option (warning: this option is CPU intensive!)
systemNoRunahead = {'sega32x', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'neogeocd', 'saturn', 'dice'}

# Define the libretro device type corresponding to the libretro CORE (when needed)
coreToP1Device = {'atari800': '513', 'cap32': '513', '81': '259', 'fuse': '769'}
coreToP2Device = {'atari800': '513', 'fuse': '513'}

# Define the libretro device type corresponding to the libretro SYSTEM (when needed)
systemToP1Device = {'msx': '1', 'msx1': '1', 'msx2': '1', 'colecovision': '1' }
systemToP2Device = {'msx': '1', 'msx1': '1', 'msx2': '1', 'colecovision': '1' }

# Netplay modes
systemNetplayModes = {'host', 'client', 'spectator'}

# Cores that require .slang shaders (even on OpenGL, not only Vulkan)
coreForceSlangShaders = { 'mupen64plus-next' }

def connected_to_internet() -> bool:
    # Try Cloudflare one.one.one.one first
    cmd = ["timeout", "1", "ping", "-c", "1", "-t", "255", "one.one.one.one"]
    process = subprocess.Popen(cmd)
    process.wait()
    if process.returncode == 0:
        _logger.debug("Connected to the internet")
        return True

    # Try dns.google if one.one.one.one fails
    cmd = ["timeout", "1", "ping", "-c", "1", "-t", "255", "dns.google"]
    process = subprocess.Popen(cmd)
    process.wait()
    if process.returncode == 0:
        _logger.debug("Connected to the internet")
        return True

    _logger.error("Not connected to the internet")
    return False

def writeLibretroConfig(
    generator: Generator,
    retroconfig: UnixSettings,
    system: Emulator,
    controllers: Controllers,
    metadata: Mapping[str, str],
    guns: Guns,
    wheels: DeviceInfoMapping,
    rom: Path,
    bezel: str | None,
    shaderBezel: bool,
    gameResolution: Resolution,
    gfxBackend: str,
    /,
) -> None:
    writeLibretroConfigToFile(retroconfig, createLibretroConfig(generator, system, controllers, metadata, guns, wheels, rom, bezel, shaderBezel, gameResolution, gfxBackend))

# Take a system, and returns a dict of retroarch.cfg compatible parameters
def createLibretroConfig(
    generator: Generator,
    system: Emulator,
    controllers: Controllers,
    metadata: Mapping[str, str],
    guns: Guns,
    wheels: DeviceInfoMapping,
    rom: Path,
    bezel: str | None,
    shaderBezel: bool,
    gameResolution: Resolution,
    gfxBackend: str,
    /,
) -> dict[str, object]:

    # retroarch-core-options.cfg
    mkdir_if_not_exists(RETROARCH_CORE_CUSTOM.parent)

    try:
        coreSettings = UnixSettings(RETROARCH_CORE_CUSTOM, separator=' ')
    except UnicodeError:
        # invalid retroarch-core-options.cfg
        # remove it and try again
        RETROARCH_CORE_CUSTOM.unlink()
        coreSettings = UnixSettings(RETROARCH_CORE_CUSTOM, separator=' ')

    # Create/update retroarch-core-options.cfg
    libretroOptions.generateCoreSettings(coreSettings, system, rom, guns, wheels)

    # Create/update hatari.cfg
    if system.name == 'atarist':
        libretroOptions.generateHatariConf(HATARI_CONFIG / 'hatari.cfg')

    if system.config.core in [ 'mame', 'mess', 'mamevirtual', 'same_cdi' ]:
        libretroMAMEConfig.generateMAMEConfigs(controllers, system, rom, guns)

    retroarchConfig: dict[str, object] = {}
    renderConfig = system.renderconfig
    systemCore = system.config.core
    # Get value from ES settings
    swapButtons = '"false"' if getInvertButtonsValue() else '"true"'

    # Basic configuration
    retroarchConfig['quit_press_twice'] = 'false'                 # not aligned behavior on other emus
    retroarchConfig['menu_show_restart_retroarch'] = 'false'      # this option messes everything up on Batocera if ever clicked
    retroarchConfig['menu_show_load_content_animation'] = 'false' # hide popup when starting a game
    retroarchConfig['menu_swap_ok_cancel_buttons'] = swapButtons  # Set the correct value to match ES confirm /cancel inputs
    retroarchConfig["video_viewport_bias_x"] = "0.500000"
    retroarchConfig["video_viewport_bias_y"] = "0.500000"

    retroarchConfig['video_driver'] = f'"{gfxBackend}"'  # needed for the ozone menu
    # Set Vulkan
    if system.config.get("gfxbackend") == "vulkan" and vulkan.is_available():
        _logger.debug("Vulkan driver is available on the system.")
        if vulkan.has_discrete_gpu():
            _logger.debug("A discrete GPU is available on the system. We will use that for performance")
            discrete_index = vulkan.get_discrete_gpu_index()
            if discrete_index:
                _logger.debug("Using Discrete GPU Index: %s for RetroArch", discrete_index)
                retroarchConfig["vulkan_gpu_index"] = f'"{discrete_index}"'
            else:
                _logger.debug("Couldn't get discrete GPU index")
        else:
            _logger.debug("Discrete GPU is not available on the system. Using default.")

    retroarchConfig['audio_driver'] = system.config.get("audio_driver", '"pulse"')
    retroarchConfig['audio_latency'] = system.config.get("audio_latency", '64')  # 64 = best balance with audio perf
    retroarchConfig['audio_volume'] = system.config.get("audio_volume", '0')

    display_rotate = system.config.get_str("display.rotate")
    if display_rotate and not videoMode.supportSystemRotation(): # only for systems that don't support global rotation (xorg, wayland, ...)
        # 0 => 0 ; 1 => 270; 2 => 180 ; 3 => 90
        if display_rotate == "0":
            retroarchConfig['video_rotation'] = "0"
        elif display_rotate == "1":
            retroarchConfig['video_rotation'] = "3"
        elif display_rotate == "2":
            retroarchConfig['video_rotation'] = "2"
        elif display_rotate == "3":
            retroarchConfig['video_rotation'] = "1"
    else:
        retroarchConfig['video_rotation'] = '0'

    retroarchConfig['video_threaded'] = system.config.get_bool('video_threaded', return_values=('true', 'false'))
    retroarchConfig['video_allow_rotate'] = system.config.get_bool('video_allow_rotate', True, return_values=('true', 'false'))

    # variable refresh rate
    retroarchConfig['vrr_runloop_enable'] = system.config.get_bool('vrr_runloop_enable', return_values=('true', 'false'))

    # required at least for vulkan (to get the correct resolution)
    retroarchConfig['video_fullscreen_x'] = gameResolution["width"]
    retroarchConfig['video_fullscreen_y'] = gameResolution["height"]

    retroarchConfig['video_black_frame_insertion'] = 'false'    # don't use anymore this value while it doesn't allow the shaders to work
    retroarchConfig['pause_nonactive'] = 'false'                # required at least on x86 x86_64 otherwise, the game is paused at launch

    mkdir_if_not_exists(RETROARCH_CONFIG / 'cache')
    retroarchConfig['cache_directory'] = RETROARCH_CONFIG / 'cache'

    # require for core informations
    retroarchConfig['libretro_directory'] = '/usr/lib/libretro'
    retroarchConfig['libretro_info_path'] = '/usr/share/libretro/info'

    retroarchConfig['video_fullscreen'] = 'true'                # Fullscreen is required at least for x86* and odroidn2

    retroarchConfig['sort_savefiles_enable'] = 'false'     # ensure we don't save system.name + core
    retroarchConfig['sort_savestates_enable'] = 'false'    # ensure we don't save system.name + core
    retroarchConfig['savestate_directory'] = SAVES / system.name
    retroarchConfig['savefile_directory'] = SAVES / system.name

    # Forced values (so that if the config is not correct, fix it)
    if system.config.core == 'tgbdual':
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("core")) # Reset each time in this function

    # Disable internal image viewer (ES does it, and pico-8 won't load .p8.png)
    retroarchConfig['builtin_imageviewer_enable'] = 'false'

    # Input configuration
    retroarchConfig['input_joypad_driver'] = 'udev'
    retroarchConfig['input_driver'] = 'udev'                    # driver for mouse/keyboard. udev required for guns.
    retroarchConfig['input_max_users'] = "16"                   # Allow up to 16 players

    retroarchConfig['input_libretro_device_p1'] = '1'           # Default devices choices
    retroarchConfig['input_libretro_device_p2'] = '1'

    # D-pad = Left analog stick forcing on PUAE and VICE (New D2A system on RA doesn't work with these cores.)
    if system.config.core == 'puae' or system.config.core == 'puae2021' or system.config.core == 'vice_x64':
        retroarchConfig['input_player1_analog_dpad_mode'] = '3'
        retroarchConfig['input_player2_analog_dpad_mode'] = '3'

    # force notification messages, but not the "remap" one
    retroarchConfig['video_font_enable'] = '"true"'
    retroarchConfig['notification_show_remap_load'] = '"false"'

    language = system.config.get_str('retroarch.user_language', system.config.get_str('system.language'))
    # RETRO_LANGUAGE_JAPANESE = 1
    if language == '1' or language == 'ja_JP':
        retroarchConfig['video_font_path'] = "/usr/share/fonts/truetype/noto/NotoSansJP-VF.ttf"
    # RETRO_LANGUAGE_KOREAN = 10
    elif language == '10' or language == 'ko_KR':
        retroarchConfig['video_font_path'] = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
    # RETRO_LANGUAGE_CHINESE_TRADITIONAL = 11
    elif language == '11' or language == 'zh_TW':
        retroarchConfig['video_font_path'] = "/usr/share/fonts/truetype/noto/NotoSansTC-VF.ttf"
    # RETRO_LANGUAGE_CHINESE_SIMPLIFIED = 12
    elif language == '12' or language == 'zh_CN':
        retroarchConfig['video_font_path'] = "/usr/share/fonts/truetype/noto/NotoSansSC-VF.ttf"

    # prevent displaying "QUICK MENU" with "No Items" after DOSBox Pure, TyrQuake and PrBoom games exit
    retroarchConfig['load_dummy_on_core_shutdown'] = '"false"'

    ## Specific choices
    if system.config.core in coreToP1Device:
        retroarchConfig['input_libretro_device_p1'] = coreToP1Device[system.config.core]
    if system.config.core in coreToP2Device:
        retroarchConfig['input_libretro_device_p2'] = coreToP2Device[system.config.core]

    ## AMIGA BIOS files are in /userdata/bios/amiga
    if system.config.core == 'puae' or system.config.core == 'puae2021' or system.config.core == 'uae4arm':
        retroarchConfig['system_directory'] = '"/userdata/bios/amiga/"'

    ## AMIGA OCS-ECS/AGA/CD32
    if system.config.core == 'puae' or system.config.core == 'puae2021':
        if system.name != 'amigacd32':
            retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_puae', '1')
            retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_puae', '1')
        else:
            retroarchConfig['input_libretro_device_p1'] = '517'     # CD 32 Pad

    ## BlueMSX choices by System
    if system.name in systemToBluemsx and system.config.core == 'bluemsx':
        retroarchConfig['input_libretro_device_p1'] = systemToP1Device[system.name]
        retroarchConfig['input_libretro_device_p2'] = systemToP2Device[system.name]

    ## SNES9x and SNES9x_next (2010) controller
    if system.config.core == 'snes9x' or system.config.core == 'snes9x_next':
        if 'controller1_snes9x' in system.config:
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_snes9x']
        elif 'controller1_snes9x_next' in system.config:
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_snes9x_next']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        # Player 2
        if 'controller2_snes9x' in system.config:
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_snes9x']
        elif 'controller2_snes9x_next' in system.config:
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_snes9x_next']
        elif len(controllers) > 2:                              # More than 2 controller connected
            retroarchConfig['input_libretro_device_p2'] = '257'
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
        # Player 3
        retroarchConfig['input_libretro_device_p3'] = system.config.get('controller3_snes9x', '1')

    ## NES controller
    if system.config.core == 'fceumm':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_nes', '1')
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_nes', '1')

    ## PlayStation controller
    if system.config.core == 'mednafen_psx':               # Madnafen
        if psx_controller_1 := system.config.get('beetle_psx_hw_Controller1'):
            retroarchConfig['input_libretro_device_p1'] = psx_controller_1
            retroarchConfig['input_player1_analog_dpad_mode'] = '0' if psx_controller_1 != '1' else '1'
        if psx_controller_2 := system.config.get('beetle_psx_hw_Controller2'):
            retroarchConfig['input_libretro_device_p2'] = psx_controller_2
            retroarchConfig['input_player2_analog_dpad_mode'] = '0' if psx_controller_2 != '1' else '1'

    if system.config.core == 'pcsx_rearmed':               # PCSX Rearmed
        if psx_controller_1 := system.config.get('controller1_pcsx'):
            retroarchConfig['input_libretro_device_p1'] = psx_controller_1
            retroarchConfig['input_player1_analog_dpad_mode'] = '0' if psx_controller_1 != '1' else '1'
        if psx_controller_2 := system.config.get('controller2_pcsx'):
            retroarchConfig['input_libretro_device_p2'] = psx_controller_2
            retroarchConfig['input_player2_analog_dpad_mode'] = '0' if psx_controller_2 != '1' else '1'

        # wheel
        if system.config.use_wheels:
            deviceInfos = controllersConfig.getDevicesInformation()
            for pad in controllers:
                if pad.device_path in deviceInfos and deviceInfos[pad.device_path]["isWheel"]:
                    retroarchConfig[f'input_player{pad.player_number}_analog_dpad_mode'] = '1'
                    if "wheel_type" in metadata and metadata["wheel_type"] == "negcon" :
                        retroarchConfig[f'input_libretro_device_p{pad.player_number}'] = 773 # Negcon
                    else:
                        retroarchConfig[f'input_libretro_device_p{pad.player_number}'] = 517 # DualShock Controller

    ## Sega Dreamcast controller
    if system.config.core == 'flycast':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_dc', '1')
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_dc', '1')
        retroarchConfig['input_libretro_device_p3'] = system.config.get('controller3_dc', '1')
        retroarchConfig['input_libretro_device_p4'] = system.config.get('controller4_dc', '1')

        # wheel
        if system.config.use_wheels and wheels:
            retroarchConfig['input_libretro_device_p1'] = '2049' # Race Controller

    ## Sega Megadrive controller
    if (system.config.core == 'genesisplusgx' or system.config.core == 'genesisplusgx-expanded') and system.name == 'megadrive':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_md', '513')  # 513 = 6 button
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_md', '513')  # 513 = 6 button

    ## Sega Megadrive style controller remap
    if system.config.core in ['genesisplusgx', 'genesisplusgx-expanded', 'picodrive']:

        valid_megadrive_controller_guids = [
        # 8bitdo m30
        "05000000c82d00005106000000010000",
        "03000000c82d00000650000011010000",
        "050000005e0400008e02000030110000",
        # 8bitdo m30 modkit
        "03000000c82d00000150000011010000",
        "05000000c82d00000151000000010000",
        # Retrobit bt saturn
        "0500000049190000020400001b010000",
        ]

        valid_megadrive_controller_names = [
        "8BitDo M30 gamepad",
        "8Bitdo  8BitDo M30 gamepad",
        "8BitDo M30 Modkit",
        "8Bitdo  8BitDo M30 Modkit",
        "Retro Bit Bluetooth Controller",
        ]

        def update_megadrive_controller_config(controller_number: int, /):
            # Remaps for Megadrive style controllers
            remap_values = {
                'btn_a': '0', 'btn_b': '1', 'btn_x': '9', 'btn_y': '10',
                'btn_l': '11', 'btn_r': '8',
            }

            for btn, value in remap_values.items():
                retroarchConfig[f'input_player{controller_number}_{btn}'] = value

        if system.config.core == 'genesisplusgx' or system.config.core == 'genesisplusgx-expanded':
            option = 'gx'
        else:  # picodrive
            option = 'pd'

        for i in range(1, min(5, len(controllers) + 1)):
            pad = controllers[i - 1]
            if (pad.guid in valid_megadrive_controller_guids and pad.name in valid_megadrive_controller_names) or system.config.get(f'{option}_controller{i}_mapping', 'retropad') != 'retropad':
                update_megadrive_controller_config(i)

    ## Sega Mastersystem controller
    if system.config.core == 'genesisplusgx' and system.name == 'mastersystem':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_ms', '769')
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_ms', '769')

    ## Sega Saturn controller
    if system.config.core in ['yabasanshiro', 'beetle-saturn'] and system.name == 'saturn':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_saturn', '1')  # 1 = Saturn pad
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_saturn', '1')  # 1 = Saturn pad

    # wheel
    if system.config.core == 'beetle-saturn' and system.name == 'saturn' and system.config.use_wheels:
        retroarchConfig['input_libretro_device_p1'] = '517' # Arcade Racer

    ## NEC PCEngine controller
    if system.config.core == 'pce' or system.config.core == 'pce_fast':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_pce', '1')

    ## WII controller
    if system.config.core == 'dolphin' or system.config.core == 'dolphin':
        # Controller 1 Type
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_wii', '1')
        # Controller 2 Type
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_wii', '1')
        # Controller 3 Type
        retroarchConfig['input_libretro_device_p3'] = system.config.get('controller3_wii', '1')
        # Controller 4 Type
        retroarchConfig['input_libretro_device_p4'] = system.config.get('controller4_wii', '1')

    ## MS-DOS controller
    if system.config.core == 'dosbox_pure':               # Dosbox-Pure
        if controller1 := system.config.get('controller1_dosbox_pure'):
            retroarchConfig['input_libretro_device_p1'] = controller1
            retroarchConfig['input_player1_analog_dpad_mode'] = controller1 if controller1 == '3' else '0'
        if controller2 := system.config.get('controller2_dosbox_pure'):
            retroarchConfig['input_libretro_device_p2'] = controller2
            retroarchConfig['input_player2_analog_dpad_mode'] = controller2 if controller2 == '3' else '0'

    ## PS1 Swanstation
    if system.config.core == 'swanstation':
        controller1 = system.config.get('swanstation_Controller1', '1')
        retroarchConfig['input_libretro_device_p1'] = controller1
        retroarchConfig['input_player1_analog_dpad_mode'] = '0' if controller1 not in ['261', '517'] else '1'

        controller2 = system.config.get('swanstation_Controller2', '1')
        retroarchConfig['input_libretro_device_p2'] = controller2
        retroarchConfig['input_player2_analog_dpad_mode'] = '0' if controller2 not in ['261', '517'] else '1'

    ## Wonder Swan & Wonder Swan Color
    if system.config.core == "mednafen_wswan":             # Beetle Wonderswan
        # If set manually, proritize that.
        # Otherwise, set to portrait for games listed as 90 degrees, manual (default) if not.
        if (rotate_display := system.config.get('wswan_rotate_display')) is not system.config.MISSING:
            wswanOrientation = rotate_display
        else:
            wswanGameRotation = videoMode.getAltDecoration(system.name, rom, 'retroarch')
            wswanOrientation = "portrait" if wswanGameRotation == "90" else "manual"

        retroarchConfig['wswan_rotate_display'] = wswanOrientation

    ## N64 Controller Remap
    if system.config.core in ['mupen64plus-next', 'parallel_n64']:

        valid_n64_controller_guids = [
            "050000007e0500001920000001800000", # official nintendo switch n64 controller
            "05000000c82d00006928000000010000", # 8bitdo n64 modkit
            "030000007e0500001920000011810000",
            "05000000c82d00001930000001000000", # 8bitdo n64 bt
            "03000000c82d00001930000011010000", # 8bitdo n64 wired
        ]

        valid_n64_controller_names = [
            "N64 Controller",
            "Nintendo Co., Ltd. N64 Controller",
            "8BitDo N64 Modkit",
            "8BitDo 64 BT",
            "8BitDo 8BitDo 64 Bluetooth Controller",
        ]

        def update_n64_controller_config(controller_number: int, /):
            # Remaps for N64 style controllers
            remap_values = {
                'btn_a': '1', 'btn_b': '0', 'btn_x': '23', 'btn_y': '21',
                'btn_l2': '22', 'btn_r2': '20', 'btn_select': '12',
            }

            for btn, value in remap_values.items():
                retroarchConfig[f'input_player{controller_number}_{btn}'] = value


        if system.config.core == 'mupen64plus-next':
            option = 'mupen64plus'
        else:  # parallel_n64
            option = 'parallel-n64'

        for i in range(1, min(5, len(controllers) + 1)):
            pad = controllers[i - 1]
            if (pad.guid in valid_n64_controller_guids and pad.name in valid_n64_controller_names) or (system.config.get(f'{option}-controller{i}', 'retropad') != 'retropad'):
                update_n64_controller_config(i)

    ## Bennu Game Development
    if system.config.core == 'bennugd':
        bezel = None

    ## PORTS
    ## Quake
    if system.config.core == 'tyrquake':
        controller1 = system.config.get('tyrquake_controller1')
        retroarchConfig['input_libretro_device_p1'] = controller1 or '1'
        if controller1:
            retroarchConfig['input_player1_analog_dpad_mode'] = '0' if controller1 in ['773', '3'] else '1'

    ## DOOM
    if system.config.core == 'prboom':
        controller1 = system.config.get('prboom_controller1')
        retroarchConfig['input_libretro_device_p1'] = controller1 or '1'
        if controller1:
            retroarchConfig['input_player1_analog_dpad_mode'] = '0' if controller1 != '1' else '1'

    ## ZX Spectrum
    if system.config.core == 'fuse':
        retroarchConfig['input_libretro_device_p1'] = system.config.get('controller1_zxspec', '769') # 769 = Sinclair 1 controller - most used on games
        retroarchConfig['input_libretro_device_p2'] = system.config.get('controller2_zxspec', '1025') # 1025 = Sinclair 2 controller
        retroarchConfig['input_libretro_device_p3'] = system.config.get('controller3_zxspec', '259')

    ## Mr. Boom
    if system.config.core == 'mrboom':
        bezel = None

    # Smooth option
    retroarchConfig['video_smooth'] = system.config.get_bool('smooth', return_values=('true', 'false'))

    # Shader option
    if 'shader' in renderConfig:
        if renderConfig['shader'] is not None and renderConfig['shader'] != "none":
            retroarchConfig['video_shader_enable'] = 'true'
            retroarchConfig['video_smooth']        = 'false'     # seems to be necessary for weaker SBCs
    else:
        retroarchConfig['video_shader_enable'] = 'false'

     # Ratio option
    retroarchConfig['aspect_ratio_index'] = ''              # reset in case config was changed (or for overlays)
    if ratio := system.config.get_str('ratio'):
        index = '22'    # default value (core)
        if ratio in ratioIndexes:
            index = ratioIndexes.index(ratio)
        if ratio == "full":
            bezel = None
        # Check if game natively supports widescreen from metadata (not widescreen hack) (for easy scalability ensure all values for respective systems start with core name and end with "-autowidescreen")
        elif system.config.get_bool(f"{systemCore}-autowidescreen"):
            metadata = controllersConfig.getGamesMetaData(system.name, rom)
            if metadata.get("video_widescreen") == "true":
                index = str(ratioIndexes.index("16/9"))
                # Easy way to disable bezels if setting to 16/9
                bezel = None

        # Independently check if the ratio is numerically widescreen to disable bezels.
        # This handles cases like "16/9", "16/10", etc., where bezels are not wanted.
        try:
            # Check if the ratio string contains a '/' to see if it's numerical
            if '/' in ratio:
                numerator, denominator = map(float, ratio.split('/'))
                # If the calculated ratio is wider than 4/3, disable the bezel.
                if denominator != 0 and (numerator / denominator) > (4/3):
                    _logger.debug("Bezel set to none for widescreen ratio. Ratio %s:%s selected", int(numerator), int(denominator))
                    bezel = None
        except (ValueError, TypeError):
            pass

        retroarchConfig['video_aspect_ratio_auto'] = 'false'
        retroarchConfig['aspect_ratio_index'] = index

    # Rewind option
    retroarchConfig['rewind_enable'] = 'true' if system.name not in systemNoRewind and system.config.get_bool('rewind') else 'false'

    # Run-ahead option (latency reduction)
    retroarchConfig['run_ahead_enabled'] = 'false'
    retroarchConfig['preemptive_frames_enable'] = 'false'
    retroarchConfig['run_ahead_frames'] = '0'
    retroarchConfig['run_ahead_secondary_instance'] = 'false'
    if (runahead := system.config.get_int('runahead')) > 0 and system.name not in systemNoRunahead:
        if system.config.get_bool('preemptiveframes'):
            retroarchConfig['preemptive_frames_enable'] = 'true'
        else:
            retroarchConfig['run_ahead_enabled'] = 'true'
        retroarchConfig['run_ahead_frames'] = runahead

        if system.config.get_bool('secondinstance'):
            retroarchConfig['run_ahead_secondary_instance'] = 'true'

    # Auto frame delay (input delay reduction via frame timing)
    retroarchConfig['video_frame_delay_auto'] = system.config.get_bool('video_frame_delay_auto', return_values=('true', 'false'))

    # Retroachievement option
    if (ra_sound := system.config.get("retroachievements.sound", "none")) != "none":
        retroarchConfig['cheevos_unlock_sound_enable'] = 'true'
        retroarchConfig['cheevos_unlock_sound'] = ra_sound
    else:
        retroarchConfig['cheevos_unlock_sound_enable'] = 'false'

    # Autosave option
    autosave = system.config.get_bool('autosave', return_values=('true', 'false'))
    retroarchConfig['savestate_auto_save'] = autosave
    retroarchConfig['savestate_auto_load'] = autosave

    if system.config.get_bool('incrementalsavestates', True):
        retroarchConfig['savestate_auto_index'] = 'true'
        retroarchConfig['savestate_max_keep'] = '0'
    else:
        retroarchConfig['savestate_auto_index'] = 'false'
        retroarchConfig['savestate_max_keep'] = '50'

    # state_slot option
    retroarchConfig['state_slot'] = system.config.get('state_slot', '0')

    # in case of the auto state_filename, do an autoload
    if (state_filename := system.config.get_str('state_filename')) and state_filename.endswith('.auto'):
        retroarchConfig['savestate_auto_load'] = 'true'

    # Retroachievements option
    retroarchConfig['cheevos_enable'] = 'false'
    retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
    retroarchConfig['cheevos_leaderboards_enable'] = 'false'
    retroarchConfig['cheevos_verbose_enable'] = 'false'
    retroarchConfig['cheevos_auto_screenshot'] = 'false'
    retroarchConfig['cheevos_challenge_indicators'] = 'false'
    retroarchConfig['cheevos_start_active'] = 'false'
    retroarchConfig['cheevos_richpresence_enable'] = 'false'

    if system.config.get_bool('retroachievements'):
        if system.config.core in coreToRetroachievements or system.config.get_bool('cheevos_force'):
            retroarchConfig['cheevos_enable'] = 'true'
            retroarchConfig['cheevos_username'] = system.config.get('retroachievements.username', "")
            retroarchConfig['cheevos_password'] = "" # clear the password - only use the token
            retroarchConfig['cheevos_token'] = system.config.get('retroachievements.token', "")
            retroarchConfig['cheevos_cmd'] = DEFAULTS_DIR / "call_achievements_hooks.sh"
            # retroachievements_hardcore_mode
            retroarchConfig['cheevos_hardcore_mode_enable'] = system.config.get_bool('retroachievements.hardcore', return_values=('true', 'false'))
            # retroachievements_leaderboards
            retroarchConfig['cheevos_leaderboards_enable'] = system.config.get_bool('retroachievements.leaderboards', return_values=('true', 'false'))
            # retroachievements_verbose_mode
            retroarchConfig['cheevos_verbose_enable'] = system.config.get_bool('retroachievements.verbose', return_values=('true', 'false'))
            # retroachievements_automatic_screenshot
            retroarchConfig['cheevos_auto_screenshot'] = system.config.get_bool('retroachievements.screenshot', return_values=('true', 'false'))
            # retroarchievements_challenge_indicators
            retroarchConfig['cheevos_challenge_indicators'] = system.config.get_bool('retroachievements.challenge_indicators', return_values=('true', 'false'))
            # retroarchievements_encore_mode
            retroarchConfig['cheevos_start_active'] = system.config.get_bool('retroachievements.encore', return_values=('true', 'false'))
            # retroarchievements_rich_presence
            retroarchConfig['cheevos_richpresence_enable'] = system.config.get_bool('retroachievements.richpresence', return_values=('true', 'false'))
            # retroarchievements_unofficial
            retroarchConfig['cheevos_test_unofficial'] = system.config.get_bool('retroachievements.unofficial', return_values=('true', 'false'))
            if not connected_to_internet():
                retroarchConfig['cheevos_enable'] = 'false'
    else:
        retroarchConfig['cheevos_enable'] = 'false'

    retroarchConfig['video_scale_integer'] = system.config.get_bool('integerscale', return_values=('true', 'false'))

    # Netplay management
    if (netplay_mode := system.config.get('netplay.mode')) in systemNetplayModes:
        # Security : hardcore mode disables save states, which would kill netplay
        retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
        # Quite strangely, host mode requires netplay_mode to be set to false when launched from command line
        retroarchConfig['netplay_mode']              = "false"
        retroarchConfig['netplay_ip_port']           = system.config.get('netplay.port', "")
        retroarchConfig['netplay_delay_frames']      = system.config.get('netplay.frames', "")
        retroarchConfig['netplay_nickname']          = system.config.get('netplay.nickname', "")
        retroarchConfig['netplay_client_swap_input'] = "false"
        if netplay_mode == 'client' or system.config['netplay.mode'] == 'spectator':
            # But client needs netplay_mode = true ... bug ?
            retroarchConfig['netplay_mode']              = "true"
            retroarchConfig['netplay_ip_address']        = system.config.get('netplay.server.ip', "")
            retroarchConfig['netplay_ip_port']           = system.config.get('netplay.server.port', "")
            retroarchConfig['netplay_client_swap_input'] = "true"

        # Connect as client
        if netplay_mode == 'client':
            if netplay_password := system.config.get_str('netplay.password'):
                retroarchConfig['netplay_password'] = f'"{netplay_password}"'
            else:
                retroarchConfig['netplay_password'] = ""

        # Connect as spectator
        if netplay_mode == 'spectator':
            retroarchConfig['netplay_start_as_spectator'] = "true"
            if netplay_password := system.config.get_str('netplay.password'):
                retroarchConfig['netplay_spectate_password'] = f'"{netplay_password}"'
            else:
                retroarchConfig['netplay_spectate_password'] = ""
        else:
            retroarchConfig['netplay_start_as_spectator'] = "false"

         # Netplay host passwords
        if system.config['netplay.mode'] == 'host':
            retroarchConfig['netplay_password'] = f'"{system.config.get("netplay.password", "")}"'
            retroarchConfig['netplay_spectate_password'] = f'"{system.config.get("netplay.spectatepassword", "")}"'

        # Netplay hide the gameplay
        retroarchConfig['netplay_public_announce'] = system.config.get_bool('netplay_public_announce', True, return_values=('true', 'false'))

        # Enable or disable server spectator mode
        retroarchConfig['netplay_spectator_mode_enable'] = system.config.get_bool('netplay.spectator', return_values=('true', 'false'))

        # Relay
        if (netplay_relay := system.config.get('netplay.relay')) and netplay_relay != "none":
            retroarchConfig['netplay_use_mitm_server'] = "true"
            retroarchConfig['netplay_mitm_server'] = netplay_relay
            if netplay_relay == "custom" and (netplay_customserver := system.config.get('netplay.customserver')) is not system.config.MISSING:
                retroarchConfig['netplay_custom_mitm_server'] = netplay_customserver
        else:
            retroarchConfig['netplay_use_mitm_server'] = "false"

    # Display FPS
    retroarchConfig['fps_show'] = 'true' if system.config.show_fps else 'false'

    # rumble (to reduce force feedback on devices like RG552)
    retroarchConfig['input_rumble_gain'] = system.config.get('rumble_gain', "")

    # On-Screen Display
    retroarchConfig['width']  = gameResolution["width"]  # default value
    retroarchConfig['height'] = gameResolution["height"] # default value
    # force the assets directory while it was wrong in some beta versions
    retroarchConfig['assets_directory'] = '/usr/share/libretro/assets'

    # Adaptation for small resolution (GPICase)
    if isLowResolution(gameResolution):
        retroarchConfig['menu_enable_widgets'] = 'false'
        retroarchConfig['video_msg_bgcolor_enable'] = 'true'
        retroarchConfig['video_font_size'] = '11'

    # AI option (service for game translations)
    if system.config.get_bool('ai_service_enabled'):
        retroarchConfig['ai_service_enable'] = 'true'
        retroarchConfig['ai_service_mode'] = '0'
        retroarchConfig['ai_service_source_lang'] = '0'
        chosen_lang = system.config.get('ai_target_lang', 'En')
        retroarchConfig['ai_service_url'] = f'{system.config.get("ai_service_url", "http://ztranslate.net/service?api_key=BATOCERA")}&mode=Fast&output=png&target_lang={chosen_lang}'
        retroarchConfig['ai_service_pause'] = system.config.get_bool('ai_service_pause', return_values=('true', 'false'))
    else:
        retroarchConfig['ai_service_enable'] = 'false'

    # Guns
    # clear premapping for each player gun to make new one. Useful for libretro-mame and flycast-dreamcast
    if system.config.use_guns:
        for g in range(len(guns)):
            clearGunInputsForPlayer(g+1, retroarchConfig)

    gun_mapping: dict[str, dict[str, _GunMappingItem]] = {
        "bsnes"         : { "default" : { "device": 260,          "p2": 0,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" },
                                                             { "key": "reversedbuttons", "value": "true", "mapcorekey": "bsnes_touchscreen_lightgun_superscope_reverse", "mapcorevalue": "ON" } ] } },
        "mesen-s"       : { "default" : { "device": 262,          "p2": 0 } },
        "mesen"         : { "default" : { "device": 262,          "p1": 0 } },
        "snes9x"        : { "default" : { "device": 260,          "p2": 0, "p3": 1,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" },
                                                             { "key": "type", "value": "justifier", "mapkey": "device_p3", "mapvalue": "772" },
                                                             { "key": "type", "value": "macsrifle", "mapkey": "device", "mapvalue": "1028" },
                                                             { "key": "reversedbuttons", "value": "true", "mapcorekey": "snes9x_superscope_reverse_buttons", "mapcorevalue": "enabled" } ] } },
        "snes9x_next"   : { "default" : { "device": 260,          "p2": 0,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" } ]} },
        "nestopia"      : { "default" : { "device": 262,          "p2": 0 } },
        "fceumm"        : { "default" : { "device": 258,          "p2": 0 } },
        "genesisplusgx" : { "megadrive" : { "device": 516, "p2": 0,
                                            "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ] },
                            "mastersystem" : { "device": 260, "p1": 0, "p2": 1 },
                            "megacd" : { "device": 516, "p2": 0,
                                         "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ]} },
        "genesisplusgx-expanded" : { "megadrive" : { "device": 516, "p2": 0,
                                            "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ] } },
        "fbneo"         : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "mame"          : { "default" : { "p1": 0, "p2": 1, "p3": 2 } },
        "mame078plus"   : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "flycast"       : { "default" : { "device":   4, "p1": 0, "p2": 1, "p3": 2, "p4": 3 } },
        "flycastvl"     : { "default" : { "device":   4, "p1": 0, "p2": 1, "p3": 2, "p4": 3 } },
        "mednafen_psx"  : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "pcsx_rearmed"  : { "default" : { "device": 260, "p1": 0, "p2": 1,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" } ]} },
        "swanstation"   : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "beetle-saturn" : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "opera"         : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "stella"        : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "vice_x64"      : { "default" : { "gameDependant": [ { "key": "type", "value": "stack_light_rifle", "mapcorekey": "vice_joyport_type", "mapcorevalue": "15" } ] } }
    }

    # apply mapping
    if system.config.use_guns:
        if system.config.core in gun_mapping:
            # conf from general mapping
            if system.name in gun_mapping[system.config.core]:
                ragunconf = gun_mapping[system.config.core][system.name]
            else:
                ragunconf = gun_mapping[system.config.core]["default"]
            raguncoreconf: dict[str, str] = {}

            # overwrite configuration by gungames.xml
            if "gameDependant" in ragunconf:
                for gd in ragunconf["gameDependant"]:
                    if f'gun_{gd["key"]}' in metadata and metadata[f'gun_{gd["key"]}'] == gd["value"] and "mapkey" in gd and "mapvalue" in gd:
                        ragunconf[gd["mapkey"]] = gd["mapvalue"]
                    if f'gun_{gd["key"]}' in metadata and metadata[f'gun_{gd["key"]}'] == gd["value"] and "mapcorekey" in gd and "mapcorevalue" in gd:
                        raguncoreconf[gd["mapcorekey"]] = gd["mapcorevalue"]

            for nplayer in range(1, 4):
                if f"p{nplayer}" in ragunconf and len(guns)-1 >= ragunconf[f"p{nplayer}"]:
                    if f"device_p{nplayer}" in ragunconf:
                        retroarchConfig[f'input_libretro_device_p{nplayer}'] = ragunconf[f"device_p{nplayer}"]
                    else:
                        if "device" in ragunconf:
                            retroarchConfig[f'input_libretro_device_p{nplayer}'] = ragunconf["device"]
                        else:
                            retroarchConfig[f'input_libretro_device_p{nplayer}'] = ""
                    configureGunInputsForPlayer(nplayer, guns[ragunconf[f"p{nplayer}"]], controllers, retroarchConfig, system.config.core, metadata, system)

            # override core settings
            for key in raguncoreconf:
                coreSettings.save(key, f'"{raguncoreconf[key]}"')

            # hide the mouse pointer with gun games
            retroarchConfig['input_overlay_show_mouse_cursor'] = "false"
    else:
        retroarchConfig['input_overlay_show_mouse_cursor'] = "true"

    # write coreSettings a bit late while guns configs can modify it
    coreSettings.write()

    # Bezel option
    try:
        writeBezelConfig(generator, bezel, shaderBezel, retroarchConfig, rom, gameResolution, system, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
    except Exception as e:
        # error with bezels, disabling them
        writeBezelConfig(generator, None, shaderBezel, retroarchConfig, rom, gameResolution, system, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
        _logger.error("Error with bezel %s: %s", bezel, e, exc_info=e, stack_info=True)

    # custom : allow the user to configure directly retroarch.cfg via batocera.conf via lines like : snes.retroarch.menu_driver=rgui
    retroarchConfig.update(system.config.items(starts_with='retroarch.'))

    return retroarchConfig

def clearGunInputsForPlayer(n: int, retroarchConfig: dict[str, object], /) -> None:
    # mapping
    keys = [ "gun_trigger", "gun_offscreen_shot", "gun_aux_a", "gun_aux_b", "gun_aux_c", "gun_start", "gun_select", "gun_dpad_up", "gun_dpad_down", "gun_dpad_left", "gun_dpad_right" ]
    for key in keys:
        for type in ["btn", "mbtn"]:
            retroarchConfig[f'input_player{n}_{key}_{type}'] = ''

def configureGunInputsForPlayer(
    n: int,
    gun: Gun,
    controllers: Controllers,
    retroarchConfig: dict[str, object],
    core: str,
    metadata: Mapping[str, str],
    system: Emulator,
    /,
) -> None:
    # find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
    pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
    pedalcname = f"controllers.pedals{n}"
    pedalkey = None
    if pedalcname in system.config:
        pedalkey = system.config[pedalcname]
    else:
        if n in pedalsKeys:
            pedalkey = pedalsKeys[n]
    pedalconfig = None

    # gun mapping
    retroarchConfig[f'input_player{n}_mouse_index'            ] = gun.mouse_index
    retroarchConfig[f'input_player{n}_gun_trigger_mbtn'       ] = 1
    retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = 2
    pedalconfig = f'input_player{n}_gun_offscreen_shot'
    retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = 3

    retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = 4
    retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 5
    retroarchConfig[f'input_player{n}_gun_aux_b_mbtn'         ] = 6
    retroarchConfig[f'input_player{n}_gun_aux_c_mbtn'         ] = 7
    retroarchConfig[f'input_player{n}_gun_dpad_up_mbtn'       ] = 8
    retroarchConfig[f'input_player{n}_gun_dpad_down_mbtn'     ] = 9
    retroarchConfig[f'input_player{n}_gun_dpad_left_mbtn'     ] = 10
    retroarchConfig[f'input_player{n}_gun_dpad_right_mbtn'    ] = 11

    # custom mapping by core to match more with avaible gun batocera buttons
    # different mapping for ps1 which has only 3 buttons and maps on aux_a and aux_b not available on all guns
    if core == "pcsx_rearmed":
        if "gun_type" in metadata and metadata["gun_type"] == "justifier":
            retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
            retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
            pedalconfig = f'input_player{n}_gun_aux_a'
        else:
            retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
            retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = ''
            retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
            pedalconfig = f'input_player{n}_gun_aux_a'
            retroarchConfig[f'input_player{n}_gun_aux_b_mbtn'         ] = 3

    if core == "fbneo":
        retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
        retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
        pedalconfig = f'input_player{n}_gun_aux_a'

    if core == "snes9x":
        if "gun_type" in metadata and metadata["gun_type"] == "justifier":
            retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
            retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = 2
            pedalconfig = f'input_player{n}_gun_start'
        else:
            retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
            retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = ''
            retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = ''
            retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
            pedalconfig = f'input_player{n}_gun_aux_a'
            retroarchConfig[f'input_player{n}_gun_aux_b_mbtn'         ] = 3
            retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = 4

    if core == "genesisplusgx" or core == "genesisplusgx-expanded":
        retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
        retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = ''
        retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = ''
        retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
        pedalconfig = f'input_player{n}_gun_aux_a'
        retroarchConfig[f'input_player{n}_gun_aux_b_mbtn'         ] = 3
        retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = 4

    if core == "flycast":
        if system.config.get_bool('flycast_offscreen_reload'):
            retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = ''
            retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = ''
            retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = ''
            retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 3
            retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = 4
            retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = 5
        else:
            retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
            retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
            pedalconfig = f'input_player{n}_gun_aux_a'

    if core == "mame":
        retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
        retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = ''
        retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
        pedalconfig = f'input_player{n}_gun_aux_a'
        retroarchConfig[f'input_player{n}_start_mbtn'             ] = 3
        retroarchConfig[f'input_player{n}_select_mbtn'            ] = 4

    if core == "mame078plus":
        retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
        retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = ''
        retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = ''
        retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = ''
        retroarchConfig[f'input_player{n}_gun_aux_b_mbtn'         ] = ''
        retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = 3
        retroarchConfig[f'input_player{n}_gun_select_mbtn'        ] = 4

    if core == "swanstation":
        retroarchConfig[f'input_player{n}_gun_offscreen_shot_mbtn'] = ''
        retroarchConfig[f'input_player{n}_gun_start_mbtn'         ] = ''
        retroarchConfig[f'input_player{n}_gun_aux_a_mbtn'         ] = 2
        pedalconfig = f'input_player{n}_gun_aux_a'
        retroarchConfig[f'input_player{n}_gun_aux_b_mbtn'         ] = 3

    # pedal
    if pedalconfig is not None and pedalkey is not None:
        retroarchConfig[pedalconfig] = pedalkey

    # mapping
    mapping = {
        "gun_trigger"        : "b",
        "gun_offscreen_shot" : "a",
        "gun_aux_a"          : "x",
        "gun_aux_b"          : "y",
        "gun_aux_c"          : "pageup",
        "gun_start"          : "start",
        "gun_select"         : "select",
        "gun_dpad_up"        : "up",
        "gun_dpad_down"      : "down",
        "gun_dpad_left"      : "left",
        "gun_dpad_right"     : "right"
    }

    # controller mapping
    hatstoname = {'1': 'up', '2': 'right', '4': 'down', '8': 'left'}
    if pad := Controller.find_player_number(controllers, n):
        for m in mapping:
            if mapping[m] in pad.inputs:
                if pad.inputs[mapping[m]].type == "button":
                    retroarchConfig[f'input_player{n}_{m}_btn'] = pad.inputs[mapping[m]].id
                elif pad.inputs[mapping[m]].type == "hat":
                    retroarchConfig[f'input_player{n}_{m}_btn'] = f"h0{hatstoname[pad.inputs[mapping[m]].value]}"
                elif pad.inputs[mapping[m]].type == "axis":
                    aval = "+"
                    if int(pad.inputs[mapping[m]].value) < 0:
                        aval = "-"
                    retroarchConfig[f'input_player{n}_{m}_axis'] = aval + pad.inputs[mapping[m]].id

def writeLibretroConfigToFile(retroconfig: UnixSettings, config: Mapping[str, object], /) -> None:
    for setting in config:
        retroconfig.save(setting, config[setting])

def writeBezelConfig(
    generator: Generator,
    bezel: str | None,
    shaderBezel: bool,
    retroarchConfig: dict[str, object],
    rom: Path,
    gameResolution: Resolution,
    system: Emulator,
    gunsBordersSize: str | None,
    gunsBordersRatio: str | None,
    /,
) -> None:
    # disable the overlay
    # if all steps are passed, enable them
    retroarchConfig['input_overlay_hide_in_menu'] = "false"

    # bezel are disabled
    # default values in case something wrong append
    retroarchConfig['input_overlay_enable'] = "false"
    retroarchConfig['video_message_pos_x']  = 0.05
    retroarchConfig['video_message_pos_y']  = 0.05

    # special text...
    if bezel == "none" or bezel == "":
        bezel = None

    _logger.debug("libretro bezel: %s", bezel)

    # create a fake bezel if guns need it
    if bezel is None and gunsBordersSize is not None:
        _logger.debug("guns need border")
        gunBezelFile     = Path("/tmp/bezel_gun_black.png")
        gunBezelInfoFile = Path("/tmp/bezel_gun_black.info")

        w = gameResolution["width"]
        h = gameResolution["height"]
        innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
        h5 = bezelsUtil.gunsBorderSize(w, h, innerSize, outerSize)

        # could be better to compute the ratio while on ra it is forced to 4/3...
        ratio = generator.getInGameRatio(system.config, gameResolution, rom)
        top    = h5
        left   = h5
        bottom = h5
        right  = h5
        if ratio == 4/3:
            left = (w-(h*4/3)) // 2 + h5
            right = left

        with gunBezelInfoFile.open("w") as fd:
            fd.write(f'{{ "width":{w}, "height":{h}, "top":{top}, "left":{left}, "bottom":{bottom}, "right":{right}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000}}')
        bezelsUtil.createTransparentBezel(gunBezelFile, gameResolution["width"], gameResolution["height"])
        # if the game needs a specific bezel, to draw border, consider it as a specific game bezel, like for thebezelproject to avoir caches
        bz_infos = { "png": gunBezelFile, "info": gunBezelInfoFile, "layout": None, "mamezip": None, "specific_to_game": True }
    else:
        if bezel is None:
            return
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name, 'retroarch')
        if bz_infos is None:
            return

    overlay_info_file: Path = cast("Path", bz_infos["info"])
    overlay_png_file: Path  = cast("Path", bz_infos["png"])
    bezel_game: bool  = cast("bool", bz_infos["specific_to_game"])

    # only the png file is mandatory
    if overlay_info_file.exists():
        try:
            with overlay_info_file.open() as f:
                infos = cast('BezelInfo', json.load(f))
        except Exception:
            infos = {}
    else:
        infos = {}

    # if image is not at the correct size, find the correct size
    bezelNeedAdaptation = False
    viewPortUsed = True
    if "width" not in infos or "height" not in infos or "top" not in infos or "left" not in infos or "bottom" not in infos or "right" not in infos or shaderBezel:
        viewPortUsed = False

    gameRatio = float(gameResolution["width"]) / float(gameResolution["height"])

    if viewPortUsed:
        if gameResolution["width"] != infos["width"] or gameResolution["height"] != infos["height"]:
            if gameRatio < 1.6 and gunsBordersSize is None: # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios ; don't skip if gun borders are needed
                return

            bezelNeedAdaptation = True
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("custom")) # overwritten from the beginning of this file
        if defined('ratio', system.config) and system.config['ratio'] in ratioIndexes:
            retroarchConfig['aspect_ratio_index'] = ratioIndexes.index(system.config['ratio'])
            retroarchConfig['video_aspect_ratio_auto'] = 'false'

    else:
        # when there is no information about width and height in the .info, assume that the tv is HD 16/9 and infos are core provided
        if gameRatio < 1.6 and gunsBordersSize is None: # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios ; don't skip if gun borders are needed
            return

        # No info on the bezel, let's get the bezel image width and height and apply the
        # ratios from usual 16:9 1920x1080 bezels (example: theBezelProject)
        try:
            infos["width"], infos["height"] = bezelsUtil.fast_image_size(overlay_png_file)
            infos["top"]    = int(infos["height"] * 2 / 1080)
            infos["left"]   = int(infos["width"] * 241 / 1920) # 241 = (1920 - (1920 / (4:3))) / 2 + 1 pixel = where viewport start
            infos["bottom"] = int(infos["height"] * 2 / 1080)
            infos["right"]  = int(infos["width"] * 241 / 1920)
            bezelNeedAdaptation = True
        except Exception:
            pass # outch, no ratio will be applied.
        if gameResolution["width"] == infos["width"] and gameResolution["height"] == infos["height"]:
            bezelNeedAdaptation = False
        if not shaderBezel:
            retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("custom"))
            if defined('ratio', system.config) and system.config['ratio'] in ratioIndexes:
                retroarchConfig['aspect_ratio_index'] = ratioIndexes.index(system.config['ratio'])
                retroarchConfig['video_aspect_ratio_auto'] = 'false'


    if not shaderBezel:
        retroarchConfig['input_overlay_enable']       = "true"
    retroarchConfig['input_overlay_scale']        = "1.0"
    retroarchConfig['input_overlay']              = RETROARCH_OVERLAY_CONFIG
    retroarchConfig['input_overlay_hide_in_menu'] = "true"

    if "opacity" not in infos:
        infos["opacity"] = 1.0
    if "messagex" not in infos:
        infos["messagex"] = 0.0
    if "messagey" not in infos:
        infos["messagey"] = 0.0

    retroarchConfig['input_overlay_opacity'] = infos["opacity"]

    bias = True
    if retroarchConfig["aspect_ratio_index"] == str(ratioIndexes.index("custom")):
        bias = False

    if bias:
        retroarchConfig["video_viewport_bias_x"] = "0.500000"
        retroarchConfig["video_viewport_bias_y"] = "0.500000"
    else:
        retroarchConfig["video_viewport_bias_x"] = "0.000000"
        retroarchConfig["video_viewport_bias_y"] = "1.000000"

    # stretch option
    bezel_stretch = system.config.get_bool('bezel_stretch')

    tattoo_output_png = Path("/tmp/bezel_tattooed.png")
    qrcode_output_png = Path("/tmp/bezel_qrcode.png")
    if bezelNeedAdaptation:
        wratio = gameResolution["width"] / float(infos["width"])
        hratio = gameResolution["height"] / float(infos["height"])

        # Stretch also takes care of cutting off the bezel and adapting viewport, if aspect ratio is < 16:9
        if gameResolution["width"] < infos["width"] or gameResolution["height"] < infos["height"]:
            _logger.debug("Screen resolution smaller than bezel: forcing stretch")
            bezel_stretch = True
        if bezel_game is True:
            output_png_file = Path("/tmp/bezel_per_game.png")
            create_new_bezel_file = True
        else:
            # The logic to cache system bezels is not always true anymore now that we have tattoos
            output_png_file = Path("/tmp") / f"{overlay_png_file.stem}_adapted.png"
            if system.config.get('bezel.tattoo', '0') != "0" or system.config.get('bezel.qrcode', '0') != "0":
                create_new_bezel_file = True
            else:
                if not tattoo_output_png.exists() and not qrcode_output_png.exists() and output_png_file.exists():
                    create_new_bezel_file = False
                    _logger.debug("Using cached bezel file %s", output_png_file)
                else:
                    try:
                        tattoo_output_png.unlink()
                        qrcode_output_png.unlink()
                    except Exception:
                        pass
                    create_new_bezel_file = True
            if create_new_bezel_file:
                fadapted = [ f for f in Path("/tmp").iterdir() if f.name.endswith('_adapted.png') ]
                fadapted.sort(key=lambda x: x.stat().st_mtime)
                # Keep only last 10 generated bezels to save space on tmpfs /tmp
                if len(fadapted) >= 10:
                    for _ in range(10):
                        fadapted.pop()
                    _logger.debug("Removing unused bezel file: %s", fadapted)
                    for fr in fadapted:
                        try:
                            fr.unlink()
                        except Exception:
                            pass

        if bezel_stretch:
            borderx = 0
            viewportRatio = (float(infos["width"])/float(infos["height"]))
            if viewportRatio - gameRatio > 0.01:
                new_x = int(infos["width"]*gameRatio/viewportRatio)
                delta = int(infos["width"]-new_x)
                borderx = delta//2
            _logger.debug("Bezel_stretch: need to cut off %s pixels", borderx)
            retroarchConfig['custom_viewport_x']      = (infos["left"] - borderx/2) * wratio
            retroarchConfig['custom_viewport_y']      = infos["top"] * hratio
            retroarchConfig['custom_viewport_width']  = (infos["width"]  - infos["left"] - infos["right"] + borderx)  * wratio
            retroarchConfig['custom_viewport_height'] = (infos["height"] - infos["top"]  - infos["bottom"]) * hratio
            retroarchConfig['video_message_pos_x']    = infos["messagex"] * wratio
            retroarchConfig['video_message_pos_y']    = infos["messagey"] * hratio
        else:
            xoffset = gameResolution["width"]  - infos["width"]
            yoffset = gameResolution["height"] - infos["height"]
            retroarchConfig['custom_viewport_x']      = infos["left"] + xoffset/2
            retroarchConfig['custom_viewport_y']      = infos["top"] + yoffset/2
            retroarchConfig['custom_viewport_width']  = infos["width"]  - infos["left"] - infos["right"]
            retroarchConfig['custom_viewport_height'] = infos["height"] - infos["top"]  - infos["bottom"]
            retroarchConfig['video_message_pos_x']    = infos["messagex"] + xoffset/2
            retroarchConfig['video_message_pos_y']    = infos["messagey"] + yoffset/2

        if create_new_bezel_file is True:
            # Padding left and right borders for ultrawide screens (larger than 16:9 aspect ratio)
            # or up/down for 4K
            _logger.debug("Generating a new adapted bezel file %s", output_png_file)
            try:
                bezelsUtil.padImage(overlay_png_file, output_png_file, gameResolution["width"], gameResolution["height"], infos["width"], infos["height"], bezel_stretch)
            except Exception as e:
                _logger.debug("Failed to create the adapated image: %s", e)
                return
        overlay_png_file = output_png_file # replace by the new file (recreated or cached in /tmp)
        if system.config.get('bezel.tattoo', '0') != "0":
            bezelsUtil.tatooImage(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png
        if system.config.get('bezel.qrcode', '0') != "0" and (cheevos_id := system.es_game_info.get("cheevosId", "0")) != "0":
            bezelsUtil.addQRCode(overlay_png_file, qrcode_output_png, cheevos_id, system)
            overlay_png_file = qrcode_output_png
    else:
        if viewPortUsed:
            retroarchConfig['custom_viewport_x']      = infos["left"]
            retroarchConfig['custom_viewport_y']      = infos["top"]
            retroarchConfig['custom_viewport_width']  = infos["width"]  - infos["left"] - infos["right"]
            retroarchConfig['custom_viewport_height'] = infos["height"] - infos["top"]  - infos["bottom"]
        retroarchConfig['video_message_pos_x']    = infos["messagex"]
        retroarchConfig['video_message_pos_y']    = infos["messagey"]
        if system.config.get('bezel.tattoo', '0') != "0":
            bezelsUtil.tatooImage(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png
        if system.config.get('bezel.qrcode', '0') != "0" and (cheevos_id := system.es_game_info.get("cheevosId", "0")) != "0":
            bezelsUtil.addQRCode(overlay_png_file, qrcode_output_png, cheevos_id, system)
            overlay_png_file = qrcode_output_png

    if gunsBordersSize is not None:
        _logger.debug("Draw gun borders")
        output_png_file = Path("/tmp/bezel_gunborders.png")
        innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
        bezelsUtil.gunBorderImage(overlay_png_file, output_png_file, gunsBordersRatio, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
        overlay_png_file = output_png_file

    _logger.debug("Bezel file set to %s", overlay_png_file)
    writeBezelCfgConfig(RETROARCH_OVERLAY_CONFIG, overlay_png_file)

    # For shaders that will want to use Batocera's decoration as part of the shader instead of an overlay
    if shaderBezel:
        # Create path if needed, clear old bezels
        shaderBezelPath = Path('/var/run/shader_bezels')
        shaderBezelFile = shaderBezelPath / 'bezel.png'
        if not shaderBezelPath.exists():
            shaderBezelPath.mkdir(parents=True)
            _logger.debug("Creating shader bezel path %s", overlay_png_file)
        if shaderBezelFile.exists():
            _logger.debug("Removing old shader bezel %s", shaderBezelFile)
            shaderBezelFile.unlink()

        # Link bezel png file to the fixed path.
        # Shaders should use this path to find the art.
        shaderBezelFile.symlink_to(overlay_png_file)
        _logger.debug("Symlinked bezel file %s to %s for selected shader", overlay_png_file, shaderBezelFile)

def isLowResolution(gameResolution: Resolution, /) -> bool:
    return gameResolution["width"] < 480 or gameResolution["height"] < 480

def writeBezelCfgConfig(cfgFile: Path, overlay_png_file: Path, /) -> None:
    fd = cfgFile.open("w")
    fd.write("overlays = 1\n")
    fd.write(f'overlay0_overlay = "{overlay_png_file}"\n')
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()
