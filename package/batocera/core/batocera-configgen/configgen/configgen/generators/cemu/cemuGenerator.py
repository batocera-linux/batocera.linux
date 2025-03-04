from __future__ import annotations

import codecs
import logging
import os
import subprocess
from os import environ
from typing import TYPE_CHECKING
from xml.dom import minidom

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, configure_emulator, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils import vulkan
from ..Generator import Generator
from . import cemuControllers
from .cemuPaths import CEMU_BIOS, CEMU_CONFIG, CEMU_CONTROLLER_PROFILES, CEMU_ROMDIR, CEMU_SAVES

if TYPE_CHECKING:
    from pathlib import Path

    from ...Emulator import Emulator
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class CemuGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "cemu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    # disable hud & bezels for now - causes game issues
    def hasInternalMangoHUDCall(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # in case of squashfs, the root directory is passed
        paths = list(rom.glob('**/code/*.rpx'))
        if len(paths) >= 1:
            rom = paths[0]

        mkdir_if_not_exists(CEMU_BIOS)
        mkdir_if_not_exists(CEMU_CONFIG)

        #graphic packs
        mkdir_if_not_exists(CEMU_SAVES / "graphicPacks")
        mkdir_if_not_exists(CEMU_CONTROLLER_PROFILES)

        # Create the settings file
        CemuGenerator.CemuConfig(CEMU_CONFIG / "settings.xml", system)

        # Set-up the controllers
        cemuControllers.generateControllerConfig(system, playersControllers)

        if configure_emulator(rom):
            commandArray = ["/usr/bin/cemu/cemu"]
        else:
            commandArray = ["/usr/bin/cemu/cemu", "-f", "-g", rom]
            # force no menubar
            commandArray.append("--force-no-menubar")

        return Command.Command(
            array=commandArray,
            env={"XDG_CONFIG_HOME":CONFIGS, "XDG_CACHE_HOME":CACHE,
                "XDG_DATA_HOME":SAVES,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    @staticmethod
    def CemuConfig(configFile: Path, system: Emulator) -> None:
        # Config file
        config = minidom.Document()
        if configFile.exists():
            try:
                config = minidom.parse(str(configFile))
            except Exception:
                pass # reinit the file

        ## [ROOT]
        xml_root = CemuGenerator.getRoot(config, "content")
        # Default mlc path
        CemuGenerator.setSectionConfig(config, xml_root, "mlc_path", str(CEMU_SAVES))
        # Remove auto updates
        CemuGenerator.setSectionConfig(config, xml_root, "check_update", "false")
        # Avoid the welcome window
        CemuGenerator.setSectionConfig(config, xml_root, "gp_download", "true")
        # Other options
        CemuGenerator.setSectionConfig(config, xml_root, "logflag", "0")
        CemuGenerator.setSectionConfig(config, xml_root, "advanced_ppc_logging", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "use_discord_presence", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "fullscreen_menubar", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "vk_warning", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "fullscreen", "true")
        # Language
        if (console_language := system.config.get("cemu_console_language", "ui")) == "ui":
            lang = getLangFromEnvironment()
        else:
            lang = console_language
        CemuGenerator.setSectionConfig(config, xml_root, "console_language", str(getCemuLang(lang)))

        ## [WINDOWS]
        # Position
        CemuGenerator.setSectionConfig(config, xml_root, "window_position", "")
        window_position = CemuGenerator.getRoot(config, "window_position")
        CemuGenerator.setSectionConfig(config, window_position, "x", "0")
        CemuGenerator.setSectionConfig(config, window_position, "y", "0")
        # Size
        CemuGenerator.setSectionConfig(config, xml_root, "window_size", "")
        window_size = CemuGenerator.getRoot(config, "window_size")
        CemuGenerator.setSectionConfig(config, window_size, "x", "640")
        CemuGenerator.setSectionConfig(config, window_size, "y", "480")

        ## [GAMEPAD]
        CemuGenerator.setSectionConfig(config, xml_root, "open_pad", system.config.get_bool("cemu_gamepad", return_values=("true", "false")))
        CemuGenerator.setSectionConfig(config, xml_root, "pad_position", "")
        pad_position = CemuGenerator.getRoot(config, "pad_position")
        CemuGenerator.setSectionConfig(config, pad_position, "x", "0")
        CemuGenerator.setSectionConfig(config, pad_position, "y", "0")
        # Size
        CemuGenerator.setSectionConfig(config, xml_root, "pad_size", "")
        pad_size = CemuGenerator.getRoot(config, "pad_size")
        CemuGenerator.setSectionConfig(config, pad_size, "x", "640")
        CemuGenerator.setSectionConfig(config, pad_size, "y", "480")

        ## [GAME PATH]
        CemuGenerator.setSectionConfig(config, xml_root, "GamePaths", "")
        game_root = CemuGenerator.getRoot(config, "GamePaths")
        # Default games path
        CemuGenerator.setSectionConfig(config, game_root, "Entry", str(CEMU_ROMDIR))

        ## [GRAPHICS]
        CemuGenerator.setSectionConfig(config, xml_root, "Graphic", "")
        graphic_root = CemuGenerator.getRoot(config, "Graphic")
        # Graphical backend
        api_value = system.config.get("cemu_gfxbackend", "1")  # 1 = Vulkan
        CemuGenerator.setSectionConfig(config, graphic_root, "api", api_value)
        # Only set the graphics `device` if Vulkan
        if api_value == "1":
            # Check if we have a discrete GPU & if so, set the UUID
            if vulkan.is_available():
                _logger.debug("Vulkan driver is available on the system.")
                if vulkan.has_discrete_gpu():
                    discrete_uuid = vulkan.get_discrete_gpu_uuid()
                    if discrete_uuid:
                        discrete_uuid_num = discrete_uuid.replace("-", "")
                        _logger.debug("Using Discrete GPU UUID: %s for Cemu", discrete_uuid_num)
                        CemuGenerator.setSectionConfig(config, graphic_root, "device", discrete_uuid_num)
                    else:
                        _logger.debug("Couldn't get discrete GPU UUID!")
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
            else:
                _logger.debug("Vulkan driver is not available on the system. Falling back to OpenGL")
                CemuGenerator.setSectionConfig(config, graphic_root, "api", "0")

        # Async VULKAN Shader compilation
        CemuGenerator.setSectionConfig(config, graphic_root, "AsyncCompile", system.config.get_bool("cemu_async", True, return_values=("true", "false")))
        # Vsync
        CemuGenerator.setSectionConfig(config, graphic_root, "VSync", system.config.get("cemu_vsync", "0"))  # 0 = Off
        # Upscale Filter
        CemuGenerator.setSectionConfig(config, graphic_root, "UpscaleFilter", system.config.get("cemu_upscale", "2"))  # 2 = Hermite
        # Downscale Filter
        CemuGenerator.setSectionConfig(config, graphic_root, "DownscaleFilter", system.config.get("cemu_downscale", "0"))  # 0 = Bilinear
        # Aspect Ratio
        CemuGenerator.setSectionConfig(config, graphic_root, "FullscreenScaling", system.config.get("cemu_aspect", "0"))  # 0 = Bilinear

        ## [GRAPHICS OVERLAYS] - Currently disbaled! Causes crash
        # Performance - alternative to MongHud
        CemuGenerator.setSectionConfig(config, graphic_root, "Overlay", "")
        overlay_root = CemuGenerator.getRoot(config, "Overlay")
        # Display FPS / CPU / GPU / RAM
        if system.config.get_bool("cemu_overlay"):
            CemuGenerator.setSectionConfig(config, overlay_root, "Position",        "3")
            CemuGenerator.setSectionConfig(config, overlay_root, "TextColor",       "4294967295")
            CemuGenerator.setSectionConfig(config, overlay_root, "TextScale",       "100")
            CemuGenerator.setSectionConfig(config, overlay_root, "FPS",             "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "DrawCalls",       "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "CPUUsage",        "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "CPUPerCoreUsage", "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "RAMUsage",        "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "VRAMUsage",       "true")
        else:
            CemuGenerator.setSectionConfig(config, overlay_root, "Position",        "3")
            CemuGenerator.setSectionConfig(config, overlay_root, "TextColor",       "4294967295")
            CemuGenerator.setSectionConfig(config, overlay_root, "TextScale",       "100")
            CemuGenerator.setSectionConfig(config, overlay_root, "FPS",             "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "DrawCalls",       "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "CPUUsage",        "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "CPUPerCoreUsage", "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "RAMUsage",        "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "VRAMUsage",       "false")
        # Notifications
        CemuGenerator.setSectionConfig(config, graphic_root, "Notification", "")
        notification_root = CemuGenerator.getRoot(config, "Notification")
        if system.config.get_bool("cemu_notifications"):
            CemuGenerator.setSectionConfig(config, notification_root, "Position", "1")
            CemuGenerator.setSectionConfig(config, notification_root, "TextColor", "4294967295")
            CemuGenerator.setSectionConfig(config, notification_root, "TextScale", "100")
            CemuGenerator.setSectionConfig(config, notification_root, "ControllerProfiles", "true")
            CemuGenerator.setSectionConfig(config, notification_root, "ControllerBattery",  "true")
            CemuGenerator.setSectionConfig(config, notification_root, "ShaderCompiling",    "true")
            CemuGenerator.setSectionConfig(config, notification_root, "FriendService",      "true")
        else:
            CemuGenerator.setSectionConfig(config, notification_root, "Position", "1")
            CemuGenerator.setSectionConfig(config, notification_root, "TextColor", "4294967295")
            CemuGenerator.setSectionConfig(config, notification_root, "TextScale", "100")
            CemuGenerator.setSectionConfig(config, notification_root, "ControllerProfiles", "false")
            CemuGenerator.setSectionConfig(config, notification_root, "ControllerBattery",  "false")
            CemuGenerator.setSectionConfig(config, notification_root, "ShaderCompiling",    "false")
            CemuGenerator.setSectionConfig(config, notification_root, "FriendService",      "false")

        ## [AUDIO]
        CemuGenerator.setSectionConfig(config, xml_root, "Audio", "")
        audio_root = CemuGenerator.getRoot(config, "Audio")
        # Use cubeb (curently the only option for linux)
        CemuGenerator.setSectionConfig(config, audio_root, "api", "3")
        # Turn audio ONLY on TV
        CemuGenerator.setSectionConfig(config, audio_root, "TVChannels", system.config.get("cemu_audio_channels", "1"))  # 1 = Stereo
        # Set volume to the max
        CemuGenerator.setSectionConfig(config, audio_root, "TVVolume", "100")
        # Set the audio device - we choose the 1st device as this is more likely the answer
        # pactl list sinks-raw | sed -e s+"^sink=[0-9]* name=\([^ ]*\) .*"+"\1"+ | sed 1q | tr -d '\n'
        proc = subprocess.run(["/usr/bin/cemu/get-audio-device"], stdout=subprocess.PIPE)
        cemuAudioDevice = proc.stdout.decode('utf-8')
        _logger.debug("*** audio device = %s ***", cemuAudioDevice)
        if system.config.get_bool("cemu_audio_config", True):
            CemuGenerator.setSectionConfig(config, audio_root, "TVDevice", cemuAudioDevice)
        else:
            # don't change the config setting
            _logger.debug("*** use config audio device ***")

        # Save the config file
        # TODO: python 3 - workaround to encode files in utf-8
        with codecs.open(str(configFile), "w", "utf-8") as xml:
            dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            xml.write(dom_string)

    # Show mouse for touchscreen actions
    def getMouseMode(self, config, rom):
        return config.get_bool('cemu_touchpad')

    @staticmethod
    def getRoot(config: minidom.Document, name: str) -> minidom.Element:
        xml_section = config.getElementsByTagName(name)

        if len(xml_section) == 0:
            xml_section = config.createElement(name)
            config.appendChild(xml_section)
        else:
            xml_section = xml_section[0]

        return xml_section

    @staticmethod
    def setSectionConfig(config: minidom.Document, xml_section: minidom.Element, name: str, value: str) -> None:
        xml_elt = xml_section.getElementsByTagName(name)
        if len(xml_elt) == 0:
            xml_elt = config.createElement(name)
            xml_section.appendChild(xml_elt)
        else:
            xml_elt = xml_elt[0]

        if xml_elt.hasChildNodes():
            xml_elt.firstChild.data = value
        else:
            xml_elt.appendChild(config.createTextNode(value))

# Language setting
def getLangFromEnvironment() -> str:
    if 'LANG' in environ:
        return environ['LANG'][:5]
    return "en_US"

def getCemuLang(lang: str) -> int:
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "zh_CN": 6, "ko_KR": 7, "nl_NL": 8, "pt_PT": 9, "ru_RU": 10, "zh_TW": 11 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
