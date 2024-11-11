from __future__ import annotations

import json
import logging
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ... import controllersConfig
from ...batoceraPaths import DEFAULTS_DIR, ES_SETTINGS, SAVES, mkdir_if_not_exists
from ...settings.unixSettings import UnixSettings
from ...utils import bezels as bezelsUtil, videoMode as videoMode
from ..hatari.hatariGenerator import HATARI_CONFIG
from . import libretroMAMEConfig, libretroOptions
from .libretroPaths import (
    RETROARCH_CONFIG,
    RETROARCH_CORE_CUSTOM,
    RETROARCH_OVERLAY_CONFIG,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...controller import ControllerMapping
    from ...Emulator import Emulator
    from ...generators.Generator import Generator
    from ...types import DeviceInfoMapping, GunMapping, Resolution

eslog = logging.getLogger(__name__)


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
    except:
        return False # when file is not yet here or malformed

# return true if the option is considered defined
def defined(key: str, dict: Mapping[str, Any]) -> bool:
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0


# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L188
ratioIndexes = ["4/3", "16/9", "16/10", "16/15", "21/9", "1/1", "2/1", "3/2", "3/4", "4/1", "9/16", "5/4", "6/5", "7/9", "8/3",
                "8/7", "19/12", "19/14", "30/17", "32/9", "config", "squarepixel", "core", "custom", "full"]

# Define system emulated by bluemsx core
systemToBluemsx = {'msx': '"MSX2"', 'msx1': '"MSX2"', 'msx2': '"MSX2"', 'colecovision': '"COL - ColecoVision"' };

# Define Retroarch Core compatible with retroachievements
# List taken from https://docs.libretro.com/guides/retroachievements/#cores-compatibility
coreToRetroachievements = {'arduous', 'beetle-saturn', 'blastem', 'bluemsx', 'bsnes', 'bsnes_hd', 'cap32', 'desmume', 'duckstation', 'fbneo', 'fceumm', 'flycast', 'flycastvl', 'freechaf', 'freeintv', 'gambatte', 'genesisplusgx', 'genesisplusgx-wide', 'handy', 'kronos', 'mednafen_lynx', 'mednafen_ngp', 'mednafen_psx', 'mednafen_supergrafx', 'mednafen_wswan', 'melonds', 'mesen', 'mesens', 'mgba', 'mupen64plus-next', 'neocd', 'o2em', 'opera', 'parallel_n64', 'pce', 'pce_fast', 'pcfx', 'pcsx_rearmed', 'picodrive', 'pokemini', 'potator', 'ppsspp', 'prosystem', 'quasi88', 'snes9x', 'sameduck', 'snes9x_next', 'stella', 'stella2014', 'swanstation', 'uzem', 'vb', 'vba-m', 'vecx', 'virtualjaguar', 'wasm4'}

# Define systems NOT compatible with rewind option
systemNoRewind = {'sega32x', 'psx', 'zxspectrum', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'saturn'};
# 'o2em', 'mame', 'neogeocd', 'fbneo'

# Define systems NOT compatible with run-ahead option (warning: this option is CPU intensive!)
systemNoRunahead = {'sega32x', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'neogeocd', 'saturn'};

# Define the libretro device type corresponding to the libretro CORE (when needed)
coreToP1Device = {'atari800': '513', 'cap32': '513', '81': '259', 'fuse': '769'};
coreToP2Device = {'atari800': '513', 'fuse': '513'};

# Define the libretro device type corresponding to the libretro SYSTEM (when needed)
systemToP1Device = {'msx': '1', 'msx1': '1', 'msx2': '1', 'colecovision': '1' };
systemToP2Device = {'msx': '1', 'msx1': '1', 'msx2': '1', 'colecovision': '1' };

# Netplay modes
systemNetplayModes = {'host', 'client', 'spectator'}

# Cores that require .slang shaders (even on OpenGL, not only Vulkan)
coreForceSlangShaders = { 'mupen64plus-next' }

def connected_to_internet() -> bool:
    # Try 1.1.1.1 first
    cmd = ["timeout", "1", "ping", "-c", "1", "-t", "255", "1.1.1.1"]
    process = subprocess.Popen(cmd)
    process.wait()
    if process.returncode == 0:
        eslog.debug("Connected to the internet")
        return True
    else:
        # Try 8.8.8.8 if 1.1.1.1 fails
        cmd = ["timeout", "1", "ping", "-c", "1", "-t", "255", "8.8.8.8"]
        process = subprocess.Popen(cmd)
        process.wait()
        if process.returncode == 0:
            eslog.debug("Connected to the internet")
            return True
        else:
            eslog.error("Not connected to the internet")
            return False

def writeLibretroConfig(generator: Generator, retroconfig: UnixSettings, system: Emulator, controllers: ControllerMapping, metadata: Mapping[str, str], guns: GunMapping, wheels: DeviceInfoMapping, rom: Path, bezel: str | None, shaderBezel: bool, gameResolution: Resolution, gfxBackend: str) -> None:
    writeLibretroConfigToFile(retroconfig, createLibretroConfig(generator, system, controllers, metadata, guns, wheels, rom, bezel, shaderBezel, gameResolution, gfxBackend))

# Take a system, and returns a dict of retroarch.cfg compatible parameters
def createLibretroConfig(generator: Generator, system: Emulator, controllers: ControllerMapping, metadata: Mapping[str, str], guns: GunMapping, wheels: DeviceInfoMapping, rom: Path, bezel: str | None, shaderBezel: bool, gameResolution: Resolution, gfxBackend: str) -> dict[str, object]:

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

    if system.config['core'] in [ 'mame', 'mess', 'mamevirtual', 'same_cdi' ]:
        libretroMAMEConfig.generateMAMEConfigs(controllers, system, rom, guns)

    retroarchConfig: dict[str, object] = {}
    systemConfig = system.config
    renderConfig = system.renderconfig
    systemCore = system.config['core']
    # Get value from ES settings
    swapButtons = '"false"' if getInvertButtonsValue() else '"true"'

    # Basic configuration
    retroarchConfig['quit_press_twice'] = 'false'                 # not aligned behavior on other emus
    retroarchConfig['menu_show_restart_retroarch'] = 'false'      # this option messes everything up on Batocera if ever clicked
    retroarchConfig['menu_show_load_content_animation'] = 'false' # hide popup when starting a game
    retroarchConfig['menu_swap_ok_cancel_buttons'] = swapButtons  # Set the correct value to match ES confirm /cancel inputs

    retroarchConfig['video_driver'] = '"' + gfxBackend + '"'  # needed for the ozone menu
    # Set Vulkan
    if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == "vulkan":
        try:
            have_vulkan = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasVulkan"], text=True).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    have_discrete = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasDiscrete"], text=True).strip()
                    if have_discrete == "true":
                        eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                        try:
                            discrete_index = subprocess.check_output(["/usr/bin/batocera-vulkan", "discreteIndex"], text=True).strip()
                            if discrete_index != "":
                                eslog.debug("Using Discrete GPU Index: {} for RetroArch".format(discrete_index))
                                retroarchConfig["vulkan_gpu_index"] = '"' + discrete_index + '"'
                            else:
                                eslog.debug("Couldn't get discrete GPU index")
                        except subprocess.CalledProcessError:
                            eslog.debug("Error getting discrete GPU index")
                    else:
                        eslog.debug("Discrete GPU is not available on the system. Using default.")
                except subprocess.CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
        except subprocess.CalledProcessError:
            eslog.debug("Error executing batocera-vulkan script.")

    retroarchConfig['audio_driver'] = '"pulse"'
    if (system.isOptSet("audio_driver")):
        retroarchConfig['audio_driver'] = system.config['audio_driver']

    retroarchConfig['audio_latency'] = '64'                     # best balance with audio perf
    if (system.isOptSet("audio_latency")):
        retroarchConfig['audio_latency'] = system.config['audio_latency']

    retroarchConfig['audio_volume'] = '0'
    if (system.isOptSet("audio_volume")):
        retroarchConfig['audio_volume'] = system.config['audio_volume']

    if system.isOptSet("display.rotate") and not videoMode.supportSystemRotation(): # only for systems that don't support global rotation (xorg, wayland, ...)
        # 0 => 0 ; 1 => 270; 2 => 180 ; 3 => 90
        if system.config["display.rotate"] == "0":
            retroarchConfig['video_rotation'] = "0"
        elif system.config["display.rotate"] == "1":
            retroarchConfig['video_rotation'] = "3"
        elif system.config["display.rotate"] == "2":
            retroarchConfig['video_rotation'] = "2"
        elif system.config["display.rotate"] == "3":
            retroarchConfig['video_rotation'] = "1"
    else:
        retroarchConfig['video_rotation'] = '0'

    if system.isOptSet('video_threaded') and system.getOptBoolean('video_threaded') == True:
        retroarchConfig['video_threaded'] = 'true'
    else:
        retroarchConfig['video_threaded'] = 'false'

    if system.isOptSet('video_allow_rotate') and system.getOptBoolean('video_allow_rotate') == False:
        retroarchConfig['video_allow_rotate'] = 'false'
    else:
        retroarchConfig['video_allow_rotate'] = 'true'

    # variable refresh rate
    if system.isOptSet("vrr_runloop_enable") and system.getOptBoolean("vrr_runloop_enable") == True:
        retroarchConfig['vrr_runloop_enable'] = 'true'
    else:
        retroarchConfig['vrr_runloop_enable'] = 'false'

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
    if system.config['core'] == 'tgbdual':
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
    if system.config['core'] == 'puae' or system.config['core'] == 'puae2021' or system.config['core'] == 'vice_x64':
        retroarchConfig['input_player1_analog_dpad_mode'] = '3'
        retroarchConfig['input_player2_analog_dpad_mode'] = '3'

    # force notification messages, but not the "remap" one
    retroarchConfig['video_font_enable'] = '"true"'
    retroarchConfig['notification_show_remap_load'] = '"false"'

    # prevent displaying "QUICK MENU" with "No Items" after DOSBox Pure, TyrQuake and PrBoom games exit
    retroarchConfig['load_dummy_on_core_shutdown'] = '"false"'

    ## Specific choices
    if(system.config['core'] in coreToP1Device):
        retroarchConfig['input_libretro_device_p1'] = coreToP1Device[system.config['core']]
    if(system.config['core'] in coreToP2Device):
        retroarchConfig['input_libretro_device_p2'] = coreToP2Device[system.config['core']]

    ## AMIGA BIOS files are in /userdata/bios/amiga
    if (system.config['core'] == 'puae') or (system.config['core'] == 'puae2021') or (system.config['core'] == 'uae4arm'):
        retroarchConfig['system_directory'] = '"/userdata/bios/amiga/"'

    ## AMIGA OCS-ECS/AGA/CD32
    if system.config['core'] == 'puae' or system.config['core'] == 'puae2021':
        if system.name != 'amigacd32':
            if system.isOptSet('controller1_puae'):
                retroarchConfig['input_libretro_device_p1'] = system.config['controller1_puae']
            else:
                retroarchConfig['input_libretro_device_p1'] = '1'
            if system.isOptSet('controller2_puae'):
                retroarchConfig['input_libretro_device_p2'] = system.config['controller2_puae']
            else:
                retroarchConfig['input_libretro_device_p2'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '517'     # CD 32 Pad

    ## BlueMSX choices by System
    if(system.name in systemToBluemsx):
        if system.config['core'] == 'bluemsx':
            retroarchConfig['input_libretro_device_p1'] = systemToP1Device[system.name]
            retroarchConfig['input_libretro_device_p2'] = systemToP2Device[system.name]

    ## SNES9x and SNES9x_next (2010) controller
    if system.config['core'] == 'snes9x' or system.config['core'] == 'snes9x_next':
        if system.isOptSet('controller1_snes9x'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_snes9x']
        elif system.isOptSet('controller1_snes9x_next'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_snes9x_next']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        # Player 2
        if system.isOptSet('controller2_snes9x'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_snes9x']
        elif system.isOptSet('controller2_snes9x_next'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_snes9x_next']
        elif len(controllers) > 2:                              # More than 2 controller connected
            retroarchConfig['input_libretro_device_p2'] = '257'
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
        # Player 3
        if system.isOptSet('Controller3_snes9x'):
            retroarchConfig['input_libretro_device_p3'] = system.config['Controller3_snes9x']
        else:
            retroarchConfig['input_libretro_device_p3'] = '1'

    ## NES controller
    if system.config['core'] == 'fceumm':
        if system.isOptSet('controller1_nes'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_nes']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        if system.isOptSet('controller2_nes'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_nes']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'

    ## PlayStation controller
    if (system.config['core'] == 'mednafen_psx'):               # Madnafen
        if system.isOptSet('beetle_psx_hw_Controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['beetle_psx_hw_Controller1']
            if system.config['beetle_psx_hw_Controller1'] != '1':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        if system.isOptSet('beetle_psx_hw_Controller2'):
            retroarchConfig['input_libretro_device_p2'] = system.config['beetle_psx_hw_Controller2']
            if system.config['beetle_psx_hw_Controller2'] != '1':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '1'
    if (system.config['core'] == 'pcsx_rearmed'):               # PCSX Rearmed
        if system.isOptSet('controller1_pcsx'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_pcsx']
            if system.config['controller1_pcsx'] != '1':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        if system.isOptSet('controller2_pcsx'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_pcsx']
            if system.config['controller2_pcsx'] != '1':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '1'

        # wheel
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels'):
            deviceInfos = controllersConfig.getDevicesInformation()
            nplayer = 1
            for controller, pad in sorted(controllers.items()):
                if pad.device_path in deviceInfos:
                    if deviceInfos[pad.device_path]["isWheel"]:
                        retroarchConfig['input_player' + str(nplayer) + '_analog_dpad_mode'] = '1'
                        if "wheel_type" in metadata and metadata["wheel_type"] == "negcon" :
                            retroarchConfig['input_libretro_device_p' + str(nplayer)] = 773 # Negcon
                        else:
                            retroarchConfig['input_libretro_device_p' + str(nplayer)] = 517 # DualShock Controller
                nplayer += 1

    ## Sega Dreamcast controller
    if system.config['core'] == 'flycast':
        if system.isOptSet('controller1_dc'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_dc']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        if system.isOptSet('controller2_dc'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_dc']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
        if system.isOptSet('controller3_dc'):
            retroarchConfig['input_libretro_device_p3'] = system.config['controller3_dc']
        else:
            retroarchConfig['input_libretro_device_p3'] = '1'
        if system.isOptSet('controller4_dc'):
            retroarchConfig['input_libretro_device_p4'] = system.config['controller4_dc']
        else:
            retroarchConfig['input_libretro_device_p4'] = '1'

        # wheel
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels') and len(wheels) > 0:
            retroarchConfig['input_libretro_device_p1'] = '2049' # Race Controller

    ## Sega Megadrive controller
    if system.config['core'] == 'genesisplusgx' and system.name == 'megadrive':
        if system.isOptSet('controller1_md'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_md']
        else:
            retroarchConfig['input_libretro_device_p1'] = '513' # 6 button
        if system.isOptSet('controller2_md'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_md']
        else:
            retroarchConfig['input_libretro_device_p2'] = '513' # 6 button

    ## Sega Megadrive style controller remap
    if system.config['core'] in ['genesisplusgx', 'picodrive']:

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

        def update_megadrive_controller_config(controller_number):
            # Remaps for Megadrive style controllers
            remap_values = {
                'btn_a': '0', 'btn_b': '1', 'btn_x': '9', 'btn_y': '10',
                'btn_l': '11', 'btn_r': '8',
            }

            for btn, value in remap_values.items():
                retroarchConfig[f'input_player{controller_number}_{btn}'] = value

        if system.config['core'] == 'genesisplusgx':
            option = 'gx'
        if system.config['core'] == 'picodrive':
            option = 'pd'

        controller_list = sorted(controllers.items())
        for i in range(1, min(5, len(controller_list) + 1)):
            controller, pad = controller_list[i - 1]
            if (pad.guid in valid_megadrive_controller_guids and pad.name in valid_megadrive_controller_names) or (system.isOptSet(f'{option}_controller{i}_mapping') and system.config[f'{option}_controller{i}_mapping'] != 'retropad'):
                update_megadrive_controller_config(i)

    ## Sega Mastersystem controller
    if system.config['core'] == 'genesisplusgx' and system.name == 'mastersystem':
        if system.isOptSet('controller1_ms'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_ms']
        else:
            retroarchConfig['input_libretro_device_p1'] = '769'
        if system.isOptSet('controller2_ms'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_ms']
        else:
            retroarchConfig['input_libretro_device_p2'] = '769'

    ## Sega Saturn controller
    if system.config['core'] in ['yabasanshiro', 'beetle-saturn'] and system.name == 'saturn':
        if system.isOptSet('controller1_saturn'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_saturn']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1' # Saturn pad
        if system.isOptSet('controller2_saturn'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_saturn']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1' # Saturn pad

    # wheel
    if system.config['core'] == 'beetle-saturn' and system.name == 'saturn':
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels'):
            retroarchConfig['input_libretro_device_p1'] = '517' # Arcade Racer

    ## NEC PCEngine controller
    if system.config['core'] == 'pce' or system.config['core'] == 'pce_fast':
        if system.isOptSet('controller1_pce'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_pce']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'

    ## WII controller
    if system.config['core'] == 'dolphin' or system.config['core'] == 'dolphin':
        # Controller 1 Type
        if system.isOptSet('controller1_wii'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_wii']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        # Controller 2 Type
        if system.isOptSet('controller2_wii'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_wii']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
        # Controller 3 Type
        if system.isOptSet('controller3_wii'):
            retroarchConfig['input_libretro_device_p3'] = system.config['controller3_wii']
        else:
            retroarchConfig['input_libretro_device_p3'] = '1'
        # Controller 4 Type
        if system.isOptSet('controller4_wii'):
            retroarchConfig['input_libretro_device_p4'] = system.config['controller4_wii']
        else:
            retroarchConfig['input_libretro_device_p4'] = '1'

    ## MS-DOS controller
    if (system.config['core'] == 'dosbox_pure'):               # Dosbox-Pure
        if system.isOptSet('controller1_dosbox_pure'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_dosbox_pure']
            if system.config['controller1_dosbox_pure'] != '3':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '3'
        if system.isOptSet('controller2_dosbox_pure'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_dosbox_pure']
            if system.config['controller2_dosbox_pure'] != '3':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '3'

    ## PS1 Swanstation
    if (system.config['core'] == 'swanstation'):
        if system.isOptSet('swanstation_Controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['swanstation_Controller1']
            if system.config['swanstation_Controller1'] != '261' and system.config['swanstation_Controller1'] != '517':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
            retroarchConfig['input_player1_analog_dpad_mode'] = '0'
        if system.isOptSet('swanstation_Controller2'):
            retroarchConfig['input_libretro_device_p2'] = system.config['swanstation_Controller2']
            if system.config['swanstation_Controller2'] != '261' and system.config['swanstation_Controller2'] != '517':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '1'
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
            retroarchConfig['input_player2_analog_dpad_mode'] = '0'

    ## Wonder Swan & Wonder Swan Color
    if (system.config['core'] == "mednafen_wswan"):             # Beetle Wonderswan
        # If set manually, proritize that.
        # Otherwise, set to portrait for games listed as 90 degrees, manual (default) if not.
        if not system.isOptSet('wswan_rotate_display'):
            wswanGameRotation = videoMode.getAltDecoration(system.name, rom, 'retroarch')
            if wswanGameRotation == "90":
                wswanOrientation = "portrait"
            else:
                wswanOrientation = "manual"
        else:
            wswanOrientation = system.config['wswan_rotate_display']
        retroarchConfig['wswan_rotate_display'] = wswanOrientation

    ## N64 Controller Remap
    if system.config['core'] in ['mupen64plus-next', 'parallel_n64']:

        valid_n64_controller_guids = [
            # official nintendo switch n64 controller
            "050000007e0500001920000001800000",
            # 8bitdo n64 modkit
            "05000000c82d00006928000000010000",
            "030000007e0500001920000011810000",
        ]

        valid_n64_controller_names = [
            "N64 Controller",
            "Nintendo Co., Ltd. N64 Controller",
            "8BitDo N64 Modkit",
        ]

        def update_n64_controller_config(controller_number):
            # Remaps for N64 style controllers
            remap_values = {
                'btn_a': '1', 'btn_b': '0', 'btn_x': '23', 'btn_y': '21',
                'btn_l2': '22', 'btn_r2': '20', 'btn_select': '12',
            }

            for btn, value in remap_values.items():
                retroarchConfig[f'input_player{controller_number}_{btn}'] = value


        if system.config['core'] == 'mupen64plus-next':
            option = 'mupen64plus'
        elif system.config['core'] == 'parallel_n64':
            option = 'parallel-n64'

        controller_list = sorted(controllers.items())
        for i in range(1, min(5, len(controller_list) + 1)):
            controller, pad = controller_list[i - 1]
            if (pad.guid in valid_n64_controller_guids and pad.name in valid_n64_controller_names) or (system.isOptSet(f'{option}-controller{i}') and system.config[f'{option}-controller{i}'] != 'retropad'):
                update_n64_controller_config(i)

    ## PORTS
    ## Quake
    if (system.config['core'] == 'tyrquake'):
        if system.isOptSet('tyrquake_controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['tyrquake_controller1']
            if system.config['tyrquake_controller1'] == '773' or system.config['tyrquake_controller1'] == '3':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'

    ## DOOM
    if (system.config['core'] == 'prboom'):
        if system.isOptSet('prboom_controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['prboom_controller1']
            if system.config['prboom_controller1'] != '1' or system.config['prboom_controller1'] == '3':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'

    ## ZX Spectrum
    if (system.config['core'] == 'fuse'):
        if system.isOptSet('controller1_zxspec'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_zxspec']
        else:
            retroarchConfig['input_libretro_device_p1'] = '769'                               #Sinclair 1 controller - most used on games
        if system.isOptSet('controller2_zxspec'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_zxspec']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1025'                              #Sinclair 2 controller
        if system.isOptSet('controller3_zxspec'):
            retroarchConfig['input_libretro_device_p3'] = system.config['controller3_zxspec']
        else:
            retroarchConfig['input_libretro_device_p3'] = '259'

    ## Mr. Boom
    if system.config['core'] == 'mrboom':
        bezel = None

    # Smooth option
    if system.isOptSet('smooth') and system.getOptBoolean('smooth') == True:
        retroarchConfig['video_smooth'] = 'true'
    else:
        retroarchConfig['video_smooth'] = 'false'

    # Shader option
    if 'shader' in renderConfig:
        if renderConfig['shader'] != None and renderConfig['shader'] != "none":
            retroarchConfig['video_shader_enable'] = 'true'
            retroarchConfig['video_smooth']        = 'false'     # seems to be necessary for weaker SBCs
    else:
        retroarchConfig['video_shader_enable'] = 'false'

     # Ratio option
    retroarchConfig['aspect_ratio_index'] = ''              # reset in case config was changed (or for overlays)
    if defined('ratio', systemConfig):
        index = '22'    # default value (core)
        if systemConfig['ratio'] in ratioIndexes:
            index = ratioIndexes.index(systemConfig['ratio'])
        # Check if game natively supports widescreen from metadata (not widescreen hack) (for easy scalability ensure all values for respective systems start with core name and end with "-autowidescreen")
        elif system.isOptSet(f"{systemCore}-autowidescreen") and system.config[f"{systemCore}-autowidescreen"] == "True":
            metadata = controllersConfig.getGamesMetaData(system.name, rom)
            if metadata.get("video_widescreen") == "true":
                index = str(ratioIndexes.index("16/9"))
                # Easy way to disable bezels if setting to 16/9
                bezel = None

        retroarchConfig['video_aspect_ratio_auto'] = 'false'
        retroarchConfig['aspect_ratio_index'] = index

    # Rewind option
    retroarchConfig['rewind_enable'] = 'false'
    if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        if(not system.name in systemNoRewind):
            retroarchConfig['rewind_enable'] = 'true'
        else:
            retroarchConfig['rewind_enable'] = 'false'
    else:
        retroarchConfig['rewind_enable'] = 'false'

    # Run-ahead option (latency reduction)
    retroarchConfig['run_ahead_enabled'] = 'false'
    retroarchConfig['preemptive_frames_enable'] = 'false'
    retroarchConfig['run_ahead_frames'] = '0'
    retroarchConfig['run_ahead_secondary_instance'] = 'false'
    if system.isOptSet('runahead') and int(system.config['runahead']) >0:
       if (not system.name in systemNoRunahead):
          if system.isOptSet('preemptiveframes') and system.getOptBoolean('preemptiveframes') == True:
             retroarchConfig['preemptive_frames_enable'] = 'true'
          else:
             retroarchConfig['run_ahead_enabled'] = 'true'
          retroarchConfig['run_ahead_frames'] = system.config['runahead']
          if system.isOptSet('secondinstance') and system.getOptBoolean('secondinstance') == True:
              retroarchConfig['run_ahead_secondary_instance'] = 'true'

    # Auto frame delay (input delay reduction via frame timing)
    if system.isOptSet('video_frame_delay_auto') and system.getOptBoolean('video_frame_delay_auto') == True:
        retroarchConfig['video_frame_delay_auto'] = 'true'
    else:
        retroarchConfig['video_frame_delay_auto'] = 'false'

    # Retroachievement option
    if system.isOptSet("retroachievements.sound") and system.config["retroachievements.sound"] != "none":
        retroarchConfig['cheevos_unlock_sound_enable'] = 'true'
        retroarchConfig['cheevos_unlock_sound'] = system.config["retroachievements.sound"]
    else:
        retroarchConfig['cheevos_unlock_sound_enable'] = 'false'

    # Autosave option
    if system.isOptSet('autosave') and system.getOptBoolean('autosave') == True:
        retroarchConfig['savestate_auto_save'] = 'true'
        retroarchConfig['savestate_auto_load'] = 'true'
    else:
        retroarchConfig['savestate_auto_save'] = 'false'
        retroarchConfig['savestate_auto_load'] = 'false'

    if system.isOptSet('incrementalsavestates') and not system.getOptBoolean('incrementalsavestates'):
        retroarchConfig['savestate_auto_index'] = 'false'
        retroarchConfig['savestate_max_keep'] = '50'
    else:
        retroarchConfig['savestate_auto_index'] = 'true'
        retroarchConfig['savestate_max_keep'] = '0'

    # state_slot option
    if system.isOptSet('state_slot'):
        retroarchConfig['state_slot'] = system.config['state_slot']
    else:
        retroarchConfig['state_slot'] = '0'

    # in case of the auto state_filename, do an autoload
    if system.isOptSet('state_filename') and system.config['state_filename'][-5:] == ".auto":
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

    if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
        if (system.config['core'] in coreToRetroachievements) or (system.isOptSet('cheevos_force') and system.getOptBoolean('cheevos_force') == True):
            retroarchConfig['cheevos_enable'] = 'true'
            retroarchConfig['cheevos_username'] = systemConfig.get('retroachievements.username', "")
            retroarchConfig['cheevos_password'] = systemConfig.get('retroachievements.password', "")
            retroarchConfig['cheevos_cmd'] = DEFAULTS_DIR / "call_achievements_hooks.sh"
            retroarchConfig['cheevos_token'] = "" # clear the token, otherwise, it may fail (possibly a ra bug)
            # retroachievements_hardcore_mode
            if system.isOptSet('retroachievements.hardcore') and system.getOptBoolean('retroachievements.hardcore') == True:
                retroarchConfig['cheevos_hardcore_mode_enable'] = 'true'
            else:
                retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
            # retroachievements_leaderboards
            if system.isOptSet('retroachievements.leaderboards') and system.getOptBoolean('retroachievements.leaderboards') == True:
                retroarchConfig['cheevos_leaderboards_enable'] = 'true'
            else:
                retroarchConfig['cheevos_leaderboards_enable'] = 'false'
            # retroachievements_verbose_mode
            if system.isOptSet('retroachievements.verbose') and system.getOptBoolean('retroachievements.verbose') == True:
                retroarchConfig['cheevos_verbose_enable'] = 'true'
            else:
                retroarchConfig['cheevos_verbose_enable'] = 'false'
            # retroachievements_automatic_screenshot
            if system.isOptSet('retroachievements.screenshot') and system.getOptBoolean('retroachievements.screenshot') == True:
                retroarchConfig['cheevos_auto_screenshot'] = 'true'
            else:
                retroarchConfig['cheevos_auto_screenshot'] = 'false'
            # retroarchievements_challenge_indicators
            if system.isOptSet('retroachievements.challenge_indicators') and system.getOptBoolean('retroachievements.challenge_indicators') == True:
                retroarchConfig['cheevos_challenge_indicators'] = 'true'
            else:
                retroarchConfig['cheevos_challenge_indicators'] = 'false'
            # retroarchievements_encore_mode
            if system.isOptSet('retroachievements.encore') and system.getOptBoolean('retroachievements.encore') == True:
                retroarchConfig['cheevos_start_active'] = 'true'
            else:
                retroarchConfig['cheevos_start_active'] = 'false'
            # retroarchievements_rich_presence
            if system.isOptSet('retroachievements.richpresence') and system.getOptBoolean('retroachievements.richpresence') == True:
                retroarchConfig['cheevos_richpresence_enable'] = 'true'
            else:
                retroarchConfig['cheevos_richpresence_enable'] = 'false'
            if not connected_to_internet():
                retroarchConfig['cheevos_enable'] = 'false'
    else:
        retroarchConfig['cheevos_enable'] = 'false'

    if system.isOptSet('integerscale') and system.getOptBoolean('integerscale') == True:
        retroarchConfig['video_scale_integer'] = 'true'
    else:
        retroarchConfig['video_scale_integer'] = 'false'

    # Netplay management
    if 'netplay.mode' in system.config and system.config['netplay.mode'] in systemNetplayModes:
        # Security : hardcore mode disables save states, which would kill netplay
        retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
        # Quite strangely, host mode requires netplay_mode to be set to false when launched from command line
        retroarchConfig['netplay_mode']              = "false"
        retroarchConfig['netplay_ip_port']           = systemConfig.get('netplay.port', "")
        retroarchConfig['netplay_delay_frames']      = systemConfig.get('netplay.frames', "")
        retroarchConfig['netplay_nickname']          = systemConfig.get('netplay.nickname', "")
        retroarchConfig['netplay_client_swap_input'] = "false"
        if system.config['netplay.mode'] == 'client' or system.config['netplay.mode'] == 'spectator':
            # But client needs netplay_mode = true ... bug ?
            retroarchConfig['netplay_mode']              = "true"
            retroarchConfig['netplay_ip_address']        = systemConfig.get('netplay.server.ip', "")
            retroarchConfig['netplay_ip_port']           = systemConfig.get('netplay.server.port', "")
            retroarchConfig['netplay_client_swap_input'] = "true"

        # Connect as client
        if system.config['netplay.mode'] == 'client':
            if 'netplay.password' in system.config:
                retroarchConfig['netplay_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            else:
                retroarchConfig['netplay_password'] = ""

        # Connect as spectator
        if system.config['netplay.mode'] == 'spectator':
            retroarchConfig['netplay_start_as_spectator'] = "true"
            if 'netplay.password' in system.config:
                retroarchConfig['netplay_spectate_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            else:
                retroarchConfig['netplay_spectate_password'] = ""
        else:
            retroarchConfig['netplay_start_as_spectator'] = "false"

         # Netplay host passwords
        if system.config['netplay.mode'] == 'host':
            retroarchConfig['netplay_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            retroarchConfig['netplay_spectate_password'] = '"' + systemConfig.get("netplay.spectatepassword", "") + '"'

        # Netplay hide the gameplay
        if system.isOptSet('netplay_public_announce') and system.getOptBoolean('netplay_public_announce') == False:
            retroarchConfig['netplay_public_announce'] = 'false'
        else:
            retroarchConfig['netplay_public_announce'] = 'true'

        # Enable or disable server spectator mode
        if system.isOptSet('netplay.spectator') and system.getOptBoolean('netplay.spectator') == True:
            retroarchConfig['netplay_spectator_mode_enable'] = 'true'
        else:
            retroarchConfig['netplay_spectator_mode_enable'] = 'false'

        # Relay
        if 'netplay.relay' in system.config and system.config['netplay.relay'] != "" and system.config['netplay.relay'] != "none" :
            retroarchConfig['netplay_use_mitm_server'] = "true"
            retroarchConfig['netplay_mitm_server'] = systemConfig.get('netplay.relay', "")
            if system.config['netplay.relay'] == "custom" and system.isOptSet('netplay.customserver'):
                retroarchConfig['netplay_custom_mitm_server'] = systemConfig.get('netplay.customserver', "")
        else:
            retroarchConfig['netplay_use_mitm_server'] = "false"

    # Display FPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
        retroarchConfig['fps_show'] = 'true'
    else:
        retroarchConfig['fps_show'] = 'false'

    # rumble (to reduce force feedback on devices like RG552)
    if system.isOptSet('rumble_gain'):
        retroarchConfig['input_rumble_gain'] = systemConfig.get('rumble_gain', "")
    else:
        retroarchConfig['input_rumble_gain'] = ""

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
    if system.isOptSet('ai_service_enabled') and system.getOptBoolean('ai_service_enabled') == True:
        retroarchConfig['ai_service_enable'] = 'true'
        retroarchConfig['ai_service_mode'] = '0'
        retroarchConfig['ai_service_source_lang'] = '0'
        if system.isOptSet('ai_target_lang'):
            chosen_lang=system.config['ai_target_lang']
        else:
            chosen_lang='En'
        if system.isOptSet('ai_service_url') and system.config['ai_service_url']:
            retroarchConfig['ai_service_url'] = system.config['ai_service_url']+'&mode=Fast&output=png&target_lang='+chosen_lang
        else:
            retroarchConfig['ai_service_url'] = 'http://ztranslate.net/service?api_key=BATOCERA&mode=Fast&output=png&target_lang='+chosen_lang
        if system.isOptSet('ai_service_pause') and system.getOptBoolean('ai_service_pause') == True:
            retroarchConfig['ai_service_pause'] = 'true'
        else:
            retroarchConfig['ai_service_pause'] = 'false'
    else:
        retroarchConfig['ai_service_enable'] = 'false'

    # Guns
    # clear premapping for each player gun to make new one. Useful for libretro-mame and flycast-dreamcast
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
        for g in range(0, len(guns)):
            clearGunInputsForPlayer(g+1, retroarchConfig)

    gun_mapping = {
        "bsnes"         : { "default" : { "device": 260,          "p2": 0,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" },
                                                             { "key": "reversedbuttons", "value": "true", "mapcorekey": "bsnes_touchscreen_lightgun_superscope_reverse", "mapcorevalue": "ON" } ] } },
        "mesen-s"       : { "default" : { "device": 262,          "p2": 0 } },
        "mesen"         : { "default" : { "device": 262,          "p1": 0 } },
        "snes9x"        : { "default" : { "device": 260,          "p2": 0, "p3": 1,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" },
                                                             { "key": "type", "value": "justifier", "mapkey": "device_p3", "mapvalue": "772" },
                                                             { "key": "reversedbuttons", "value": "true", "mapcorekey": "snes9x_superscope_reverse_buttons", "mapcorevalue": "enabled" } ] } },
        "snes9x_next"   : { "default" : { "device": 260,          "p2": 0,
                                          "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "516" } ]} },
        "nestopia"      : { "default" : { "device": 262,          "p2": 0 } },
        "fceumm"        : { "default" : { "device": 258,          "p2": 0 } },
        "genesisplusgx" : { "megadrive" : { "device": 516, "p2": 0,
                                            "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ] },
                            "mastersystem" : { "device": 260, "p1": 0, "p2": 1 },
                            "segacd" : { "device": 516, "p2": 0,
                                         "gameDependant": [ { "key": "type", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ]} },
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
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
        if system.config['core'] in gun_mapping:
            # conf from general mapping
            if system.name in gun_mapping[system.config['core']]:
                ragunconf = gun_mapping[system.config['core']][system.name]
            else:
                ragunconf = gun_mapping[system.config['core']]["default"]
            raguncoreconf = {}

            # overwrite configuration by gungames.xml
            if "gameDependant" in ragunconf:
                for gd in ragunconf["gameDependant"]:
                    if "gun_"+gd["key"] in metadata and metadata["gun_"+gd["key"]] == gd["value"] and "mapkey" in gd and "mapvalue" in gd:
                        ragunconf[gd["mapkey"]] = gd["mapvalue"]
                    if "gun_"+gd["key"] in metadata and metadata["gun_"+gd["key"]] == gd["value"] and "mapcorekey" in gd and "mapcorevalue" in gd:
                        raguncoreconf[gd["mapcorekey"]] = gd["mapcorevalue"]

            for nplayer in range(1, 3+1):
                if "p"+str(nplayer) in ragunconf and len(guns)-1 >= ragunconf["p"+str(nplayer)]:
                    if "device_p"+str(nplayer) in ragunconf:
                        retroarchConfig['input_libretro_device_p'+str(nplayer)] = ragunconf["device_p"+str(nplayer)]
                    else:
                        if "device" in ragunconf:
                            retroarchConfig['input_libretro_device_p'+str(nplayer)] = ragunconf["device"]
                        else:
                            retroarchConfig['input_libretro_device_p'+str(nplayer)] = ""
                    configureGunInputsForPlayer(nplayer, guns[ragunconf["p"+str(nplayer)]], controllers, retroarchConfig, system.config['core'], metadata, system)

            # override core settings
            for key in raguncoreconf:
                coreSettings.save(key, '"' + raguncoreconf[key] + '"')

            # hide the mouse pointer with gun games
            retroarchConfig['input_overlay_show_mouse_cursor'] = "false"
    else:
        retroarchConfig['input_overlay_show_mouse_cursor'] = "true"

    # write coreSettings a bit late while guns configs can modify it
    coreSettings.write()

    # Bezel option
    try:
        writeBezelConfig(generator, bezel, shaderBezel, retroarchConfig, rom, gameResolution, system, controllersConfig.gunsBordersSizeName(guns, system.config), controllersConfig.gunsBorderRatioType(guns, system.config))
    except Exception as e:
        # error with bezels, disabling them
        writeBezelConfig(generator, None, shaderBezel, retroarchConfig, rom, gameResolution, system, controllersConfig.gunsBordersSizeName(guns, system.config), controllersConfig.gunsBorderRatioType(guns, system.config))
        eslog.error(f"Error with bezel {bezel}: {e}", exc_info=e, stack_info=True)

    # custom : allow the user to configure directly retroarch.cfg via batocera.conf via lines like : snes.retroarch.menu_driver=rgui
    for user_config in systemConfig:
        if user_config[:10] == "retroarch.":
            retroarchConfig[user_config[10:]] = systemConfig[user_config]

    return retroarchConfig

def clearGunInputsForPlayer(n: int, retroarchConfig: dict[str, object]) -> None:
    # mapping
    keys = [ "gun_trigger", "gun_offscreen_shot", "gun_aux_a", "gun_aux_b", "gun_aux_c", "gun_start", "gun_select", "gun_dpad_up", "gun_dpad_down", "gun_dpad_left", "gun_dpad_right" ]
    for key in keys:
        for type in ["btn", "mbtn"]:
            retroarchConfig['input_player{}_{}_{}'.format(n, key, type)] = ''

def configureGunInputsForPlayer(n, gun, controllers, retroarchConfig, core, metadata, system):

    # find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
    pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
    pedalcname = "controllers.pedals{}".format(n)
    pedalkey = None
    if pedalcname in system.config:
        pedalkey = system.config[pedalcname]
    else:
        if n in pedalsKeys:
            pedalkey = pedalsKeys[n]
    pedalconfig = None

    # gun mapping
    retroarchConfig['input_player{}_mouse_index'            .format(n)] = gun["id_mouse"]
    retroarchConfig['input_player{}_gun_trigger_mbtn'       .format(n)] = 1
    retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = 2
    pedalconfig = 'input_player{}_gun_offscreen_shot'.format(n)
    retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = 3

    retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = 4
    retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 5
    retroarchConfig['input_player{}_gun_aux_b_mbtn'         .format(n)] = 6
    retroarchConfig['input_player{}_gun_aux_c_mbtn'         .format(n)] = 7
    retroarchConfig['input_player{}_gun_dpad_up_mbtn'       .format(n)] = 8
    retroarchConfig['input_player{}_gun_dpad_down_mbtn'     .format(n)] = 9
    retroarchConfig['input_player{}_gun_dpad_left_mbtn'     .format(n)] = 10
    retroarchConfig['input_player{}_gun_dpad_right_mbtn'    .format(n)] = 11

    # custom mapping by core to match more with avaible gun batocera buttons
    # different mapping for ps1 which has only 3 buttons and maps on aux_a and aux_b not available on all guns
    if core == "pcsx_rearmed":
        if "gun_type" in metadata and metadata["gun_type"] == "justifier":
            retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
            retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
            pedalconfig = 'input_player{}_gun_aux_a'.format(n)
        else:
            retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
            retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = ''
            retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
            pedalconfig = 'input_player{}_gun_aux_a'.format(n)
            retroarchConfig['input_player{}_gun_aux_b_mbtn'         .format(n)] = 3

    if core == "fbneo":
        retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
        pedalconfig = 'input_player{}_gun_aux_a'.format(n)

    if core == "snes9x":
        if "gun_type" in metadata and metadata["gun_type"] == "justifier":
            retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
            retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = 2
            pedalconfig = 'input_player{}_gun_start'.format(n)
        else:
            retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
            retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = ''
            retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = ''
            retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
            pedalconfig = 'input_player{}_gun_aux_a'.format(n)
            retroarchConfig['input_player{}_gun_aux_b_mbtn'         .format(n)] = 3
            retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = 4

    if core == "genesisplusgx":
        retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
        retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = ''
        retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
        pedalconfig = 'input_player{}_gun_aux_a'.format(n)
        retroarchConfig['input_player{}_gun_aux_b_mbtn'         .format(n)] = 3
        retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = 4

    if core == "flycast":
        if system.isOptSet('flycast_offscreen_reload') and system.getOptBoolean('flycast_offscreen_reload') == 1:
            retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = ''
            retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = ''
            retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = ''
            retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 3
            retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = 4
            retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = 5
        else:
            retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
            retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
            pedalconfig = 'input_player{}_gun_aux_a'.format(n)

    if core == "mame":
        retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
        pedalconfig = 'input_player{}_gun_aux_a'.format(n)
        retroarchConfig['input_player{}_start_mbtn'             .format(n)] = 3
        retroarchConfig['input_player{}_select_mbtn'            .format(n)] = 4

    if core == "mame078plus":
        retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
        retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = ''
        retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_b_mbtn'         .format(n)] = ''
        retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = 3
        retroarchConfig['input_player{}_gun_select_mbtn'        .format(n)] = 4

    if core == "swanstation":
        retroarchConfig['input_player{}_gun_offscreen_shot_mbtn'.format(n)] = ''
        retroarchConfig['input_player{}_gun_start_mbtn'         .format(n)] = ''
        retroarchConfig['input_player{}_gun_aux_a_mbtn'         .format(n)] = 2
        pedalconfig = 'input_player{}_gun_aux_a'.format(n)
        retroarchConfig['input_player{}_gun_aux_b_mbtn'         .format(n)] = 3

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
    nplayer = 1
    for controller, pad in sorted(controllers.items()):
        if nplayer == n:
            for m in mapping:
                if mapping[m] in pad.inputs:
                    if pad.inputs[mapping[m]].type == "button":
                        retroarchConfig['input_player{}_{}_btn'.format(n, m)] = pad.inputs[mapping[m]].id
                    elif pad.inputs[mapping[m]].type == "hat":
                        retroarchConfig['input_player{}_{}_btn'.format(n, m)] = "h0" + hatstoname[pad.inputs[mapping[m]].value]
                    elif pad.inputs[mapping[m]].type == "axis":
                        aval = "+"
                        if int(pad.inputs[mapping[m]].value) < 0:
                            aval = "-"
                        retroarchConfig['input_player{}_{}_axis'.format(n, m)] = aval + pad.inputs[mapping[m]].id
        nplayer += 1

def writeLibretroConfigToFile(retroconfig: UnixSettings, config: Mapping[str, object]) -> None:
    for setting in config:
        retroconfig.save(setting, config[setting])

def writeBezelConfig(generator: Generator, bezel: str | None, shaderBezel: bool, retroarchConfig: dict[str, object], rom: Path, gameResolution: Resolution, system: Emulator, gunsBordersSize: str | None, gunsBordersRatio: str | None) -> None:
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

    eslog.debug("libretro bezel: {}".format(bezel))

    # create a fake bezel if guns need it
    if bezel is None and gunsBordersSize is not None:
        eslog.debug("guns need border")
        gunBezelFile     = Path("/tmp/bezel_gun_black.png")
        gunBezelInfoFile = Path("/tmp/bezel_gun_black.info")

        w = gameResolution["width"]
        h = gameResolution["height"]
        innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
        h5 = bezelsUtil.gunsBorderSize(w, h, innerSize, outerSize)

        # could be better to compute the ratio while on ra it is forced to 4/3...
        ratio = generator.getInGameRatio(system.config, gameResolution, str(rom))
        top    = h5
        left   = h5
        bottom = h5
        right  = h5
        if ratio == 4/3:
            left = (w-(h*4/3)) // 2 + h5
            right = left

        with gunBezelInfoFile.open("w") as fd:
            fd.write("{" + f' "width":{w}, "height":{h}, "top":{top}, "left":{left}, "bottom":{bottom}, "right":{right}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000' + "}")
        bezelsUtil.createTransparentBezel(gunBezelFile, gameResolution["width"], gameResolution["height"])
        # if the game needs a specific bezel, to draw border, consider it as a specific game bezel, like for thebezelproject to avoir caches
        bz_infos = { "png": gunBezelFile, "info": gunBezelInfoFile, "layout": None, "mamezip": None, "specific_to_game": True }
    else:
        if bezel is None:
            return
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name, 'retroarch')
        if bz_infos is None:
            return

    overlay_info_file: Path = cast(Path, bz_infos["info"])
    overlay_png_file: Path  = cast(Path, bz_infos["png"])
    bezel_game: bool  = bz_infos["specific_to_game"]

    # only the png file is mandatory
    if overlay_info_file.exists():
        try:
            with overlay_info_file.open() as f:
                infos = json.load(f)
        except:
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
            else:
                bezelNeedAdaptation = True
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("custom")) # overwritten from the beginning of this file
        if defined('ratio', system.config):
            if system.config['ratio'] in ratioIndexes:
                retroarchConfig['aspect_ratio_index'] = ratioIndexes.index(system.config['ratio'])
                retroarchConfig['video_aspect_ratio_auto'] = 'false'

    else:
        # when there is no information about width and height in the .info, assume that the tv is HD 16/9 and infos are core provided
        if gameRatio < 1.6 and gunsBordersSize is None: # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios ; don't skip if gun borders are needed
            return
        else:
            # No info on the bezel, let's get the bezel image width and height and apply the
            # ratios from usual 16:9 1920x1080 bezels (example: theBezelProject)
            try:
                infos["width"], infos["height"] = bezelsUtil.fast_image_size(overlay_png_file)
                infos["top"]    = int(infos["height"] * 2 / 1080)
                infos["left"]   = int(infos["width"] * 241 / 1920) # 241 = (1920 - (1920 / (4:3))) / 2 + 1 pixel = where viewport start
                infos["bottom"] = int(infos["height"] * 2 / 1080)
                infos["right"]  = int(infos["width"] * 241 / 1920)
                bezelNeedAdaptation = True
            except:
                pass # outch, no ratio will be applied.
        if gameResolution["width"] == infos["width"] and gameResolution["height"] == infos["height"]:
            bezelNeedAdaptation = False
        if not shaderBezel:
            retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("core"))
            if defined('ratio', system.config):
                if system.config['ratio'] in ratioIndexes:
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

    # stretch option
    if system.isOptSet('bezel_stretch') and system.getOptBoolean('bezel_stretch') == True:
        bezel_stretch = True
    else:
        bezel_stretch = False

    tattoo_output_png = Path("/tmp/bezel_tattooed.png")
    if bezelNeedAdaptation:
        wratio = gameResolution["width"] / float(infos["width"])
        hratio = gameResolution["height"] / float(infos["height"])

        # Stretch also takes care of cutting off the bezel and adapting viewport, if aspect ratio is < 16:9
        if gameResolution["width"] < infos["width"] or gameResolution["height"] < infos["height"]:
            eslog.debug("Screen resolution smaller than bezel: forcing stretch")
            bezel_stretch = True
        if bezel_game is True:
            output_png_file = Path("/tmp/bezel_per_game.png")
            create_new_bezel_file = True
        else:
            # The logic to cache system bezels is not always true anymore now that we have tattoos
            output_png_file = Path("/tmp") / f"{overlay_png_file.stem}_adapted.png"
            if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
                create_new_bezel_file = True
            else:
                if (not tattoo_output_png.exists()) and output_png_file.exists():
                    create_new_bezel_file = False
                    eslog.debug(f"Using cached bezel file {output_png_file}")
                else:
                    try:
                        tattoo_output_png.unlink()
                    except:
                        pass
                    create_new_bezel_file = True
            if create_new_bezel_file:
                fadapted = [ f for f in Path("/tmp").iterdir() if f.name.endswith('_adapted.png') ]
                fadapted.sort(key=lambda x: x.stat().st_mtime)
                # Keep only last 10 generated bezels to save space on tmpfs /tmp
                if len(fadapted) >= 10:
                    for i in range (10):
                        fadapted.pop()
                    eslog.debug(f"Removing unused bezel file: {fadapted}")
                    for fr in fadapted:
                        try:
                            fr.unlink()
                        except:
                            pass

        if bezel_stretch:
            borderx = 0
            viewportRatio = (float(infos["width"])/float(infos["height"]))
            if (viewportRatio - gameRatio > 0.01):
                new_x = int(infos["width"]*gameRatio/viewportRatio)
                delta = int(infos["width"]-new_x)
                borderx = delta//2
            eslog.debug(f"Bezel_stretch: need to cut off {borderx} pixels")
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
            eslog.debug(f"Generating a new adapted bezel file {output_png_file}")
            try:
                bezelsUtil.padImage(overlay_png_file, output_png_file, gameResolution["width"], gameResolution["height"], infos["width"], infos["height"], bezel_stretch)
            except Exception as e:
                eslog.debug(f"Failed to create the adapated image: {e}")
                return
        overlay_png_file = output_png_file # replace by the new file (recreated or cached in /tmp)
        if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
            bezelsUtil.tatooImage(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png
    else:
        if viewPortUsed:
            retroarchConfig['custom_viewport_x']      = infos["left"]
            retroarchConfig['custom_viewport_y']      = infos["top"]
            retroarchConfig['custom_viewport_width']  = infos["width"]  - infos["left"] - infos["right"]
            retroarchConfig['custom_viewport_height'] = infos["height"] - infos["top"]  - infos["bottom"]
        retroarchConfig['video_message_pos_x']    = infos["messagex"]
        retroarchConfig['video_message_pos_y']    = infos["messagey"]
        if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
            bezelsUtil.tatooImage(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png

    if gunsBordersSize is not None:
        eslog.debug("Draw gun borders")
        output_png_file = Path("/tmp/bezel_gunborders.png")
        innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
        borderSize = bezelsUtil.gunBorderImage(overlay_png_file, output_png_file, gunsBordersRatio, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
        overlay_png_file = output_png_file

    eslog.debug(f"Bezel file set to {overlay_png_file}")
    writeBezelCfgConfig(RETROARCH_OVERLAY_CONFIG, overlay_png_file)

    # For shaders that will want to use Batocera's decoration as part of the shader instead of an overlay
    if shaderBezel:
        # Create path if needed, clear old bezels
        shaderBezelPath = Path('/var/run/shader_bezels')
        shaderBezelFile = shaderBezelPath / 'bezel.png'
        if not shaderBezelPath.exists():
            shaderBezelPath.mkdir(parents=True)
            eslog.debug("Creating shader bezel path {}".format(overlay_png_file))
        if shaderBezelFile.exists():
            eslog.debug("Removing old shader bezel {}".format(shaderBezelFile))
            shaderBezelFile.unlink()

        # Link bezel png file to the fixed path.
        # Shaders should use this path to find the art.
        shaderBezelFile.symlink_to(overlay_png_file)
        eslog.debug("Symlinked bezel file {} to {} for selected shader".format(overlay_png_file, shaderBezelFile))

def isLowResolution(gameResolution: Resolution) -> bool:
    return gameResolution["width"] < 480 or gameResolution["height"] < 480

def writeBezelCfgConfig(cfgFile: Path, overlay_png_file: Path) -> None:
    fd = cfgFile.open("w")
    fd.write("overlays = 1\n")
    fd.write(f'overlay0_overlay = "{overlay_png_file}"\n')
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()
