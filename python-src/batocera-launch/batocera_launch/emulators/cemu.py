from __future__ import annotations

import logging
import subprocess
import xml.etree.ElementTree as ET
from os import environ
from typing import TYPE_CHECKING, Final, cast
from xml.dom import minidom

import pyudev

from batocera_common import vulkan
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CACHE, CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext
from batocera_launch.paths import configure_emulator

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controller

_logger: Final = logging.getLogger(__name__)

# -= Wii U controller types =-
_GAMEPAD: Final = 'Wii U GamePad'
_PRO: Final = 'Wii U Pro Controller'
_CLASSIC: Final = 'Wii U Classic Controller'
_WIIMOTE: Final = 'Wiimote'

_API_SDL: Final = 'SDLController'
_API_WIIMOTE: Final = 'Wiimote'

# from https://github.com/cemu-project/Cemu/blob/main/src/input/emulated/WPADController.h
_WIIMOTE_TYPE_CORE: Final = '0'
_WIIMOTE_TYPE_NUNCHUK: Final = '1'
_WIIMOTE_TYPE_CLASSIC: Final = '2'
_WIIMOTE_TYPE_MOTIONPLUS: Final = '5'
_WIIMOTE_TYPE_MOTIONPLUS_NUNCHUK: Final = '6'
_WIIMOTE_TYPE_MOTIONPLUS_CLASSIC: Final = '7'

# from https://github.com/xwiimote/xwiimote/blob/master/lib/xwiimote.h
_WIIMOTE_NAME: Final = 'Nintendo Wii Remote'
_WIIMOTE_NAME_MOTIONPLUS: Final = f'{_WIIMOTE_NAME} Motion Plus'
_WIIMOTE_NAME_NUNCHUK: Final = f'{_WIIMOTE_NAME} Nunchuk'
_WIIMOTE_NAME_CLASSIC: Final = f'{_WIIMOTE_NAME} Classic Controller'

_DEFAULT_DEADZONE: Final = '0.25'
_DEFAULT_RANGE: Final = '1'

_BUTTON_MAPPINGS_SDL: Final = {
    _GAMEPAD: {  # excludes show screen
        '1': '1',
        '2': '0',
        '3': '3',
        '4': '2',
        '5': '9',
        '6': '10',
        '7': '42',
        '8': '43',
        '9': '6',
        '10': '4',
        '11': '11',
        '12': '12',
        '13': '13',
        '14': '14',
        '15': '7',
        '16': '8',
        '17': '45',
        '18': '39',
        '19': '44',
        '20': '38',
        '21': '47',
        '22': '41',
        '23': '46',
        '24': '40',
        '25': '7',
    },
    _PRO: {
        '1': '1',
        '2': '0',
        '3': '3',
        '4': '2',
        '5': '9',
        '6': '10',
        '7': '42',
        '8': '43',
        '9': '6',
        '10': '4',
        # 11 is excluded
        '12': '11',
        '13': '12',
        '14': '13',
        '15': '14',
        '16': '7',
        '17': '8',
        '18': '45',
        '19': '39',
        '20': '44',
        '21': '38',
        '22': '47',
        '23': '41',
        '24': '46',
        '25': '40',
    },
    _CLASSIC: {
        '1': '13',
        '2': '12',
        '3': '15',
        '4': '14',
        '5': '8',
        '6': '9',
        '7': '42',
        '8': '43',
        '9': '4',
        '10': '5',
        # 11 is excluded
        '12': '0',
        '13': '1',
        '14': '2',
        '15': '3',
        '16': '39',
        '17': '45',
        '18': '44',
        '19': '38',
        '20': '41',
        '21': '47',
        '22': '46',
        '23': '40',
    },
    _WIIMOTE: {  # with MotionPlus & Nunchuk, excludes Home button
        '1': '0',
        '2': '43',
        '3': '2',
        '4': '1',
        '5': '42',
        '6': '9',
        '7': '6',
        '8': '4',
        '9': '11',
        '10': '12',
        '11': '13',
        '12': '14',
        '13': '45',
        '14': '39',
        '15': '44',
        '16': '38',
    },
}

_BUTTON_MAPPINGS_WIIMOTE: Final = {
    _WIIMOTE: {
        '1': '11',
        '2': '10',
        '3': '9',
        '4': '8',
        '5': '17',
        '6': '16',
        '7': '4',
        '8': '12',
        '9': '3',
        '10': '2',
        '11': '0',
        '12': '1',
        '13': '39',
        '14': '45',
        '15': '44',
        '16': '38',
        '17': '15',
    },
}

_AVAILABLE_LANGUAGES: Final = {
    'ja_JP': 0,
    'en_US': 1,
    'fr_FR': 2,
    'de_DE': 3,
    'it_IT': 4,
    'es_ES': 5,
    'zh_CN': 6,
    'ko_KR': 7,
    'nl_NL': 8,
    'pt_PT': 9,
    'ru_RU': 10,
    'zh_TW': 11,
}


def _lang_from_environment() -> str:
    if 'LANG' in environ:
        return environ['LANG'][:5]
    return 'en_US'


def _cemu_lang(lang: str) -> int:
    return _AVAILABLE_LANGUAGES.get(lang, _AVAILABLE_LANGUAGES['en_US'])


def _is_wiimote(pad: Controller) -> bool:
    return pad.real_name == _WIIMOTE_NAME


def _find_wiimote_type(pad: Controller) -> str:
    context = pyudev.Context()
    device = pyudev.Devices.from_device_file(context, pad.device_path)
    names: list[str] = []
    for input_device in context.list_devices(parent=device.find_parent('hid')).match_subsystem('input'):
        if 'NAME' in input_device.properties:
            names += [input_device.properties['NAME'].strip('"')]
    if _WIIMOTE_NAME_MOTIONPLUS in names:
        if _WIIMOTE_NAME_NUNCHUK in names:
            return _WIIMOTE_TYPE_MOTIONPLUS_NUNCHUK
        if _WIIMOTE_NAME_CLASSIC in names:
            return _WIIMOTE_TYPE_MOTIONPLUS_CLASSIC
        return _WIIMOTE_TYPE_MOTIONPLUS
    if _WIIMOTE_NAME_NUNCHUK in names:
        return _WIIMOTE_TYPE_NUNCHUK
    if _WIIMOTE_NAME_CLASSIC in names:
        return _WIIMOTE_TYPE_CLASSIC
    return _WIIMOTE_TYPE_CORE


def _xml_root(config: minidom.Document, name: str) -> minidom.Element:
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        element = config.createElement(name)
        config.appendChild(element)
        return element

    return xml_section[0]


def _set_xml_value(config: minidom.Document, xml_section: minidom.Element, name: str, value: str) -> None:
    xml_elt = xml_section.getElementsByTagName(name)
    if len(xml_elt) == 0:
        element = config.createElement(name)
        xml_section.appendChild(element)
    else:
        element = xml_elt[0]

    if element.hasChildNodes():
        cast('minidom.Text', element.firstChild).data = value
    else:
        element.appendChild(config.createTextNode(value))


@cached_dataclass
class Cemu(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'cemu',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'swap_screen': ['KEY_LEFTCTRL', 'KEY_TAB']},
        }

    # disable hud & bezels for now - causes game issues
    @property
    def handles_hud(self) -> bool:
        return True

    @property
    def needs_mouse(self) -> bool:
        # Show mouse for touchscreen actions
        return self.config.get_bool('cemu_touchpad')

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @cached_property
    def bios_dir(self) -> Path:
        return BIOS / 'cemu'

    @cached_property
    def controller_profiles_dir(self) -> Path:
        return self.config_dir / 'controllerProfiles'

    def _write_settings_xml(self) -> None:
        config_file = self.config_dir / 'settings.xml'

        config = minidom.Document()
        if config_file.exists():
            try:
                config = minidom.parse(str(config_file))
            except Exception:
                pass  # reinit the file

        ## [ROOT]
        xml_root = _xml_root(config, 'content')
        # Default mlc path
        _set_xml_value(config, xml_root, 'mlc_path', str(self.saves_dir))
        # Remove auto updates
        _set_xml_value(config, xml_root, 'check_update', 'false')
        # Avoid the welcome window
        _set_xml_value(config, xml_root, 'gp_download', 'true')
        # Other options
        _set_xml_value(config, xml_root, 'logflag', '0')
        _set_xml_value(config, xml_root, 'advanced_ppc_logging', 'false')
        _set_xml_value(config, xml_root, 'use_discord_presence', 'false')
        _set_xml_value(config, xml_root, 'fullscreen_menubar', 'false')
        _set_xml_value(config, xml_root, 'vk_warning', 'false')
        _set_xml_value(config, xml_root, 'fullscreen', 'true')
        # Language
        if (console_language := self.config.get_str('cemu_console_language', 'ui')) == 'ui':
            lang = _lang_from_environment()
        else:
            lang = console_language
        _set_xml_value(config, xml_root, 'console_language', str(_cemu_lang(lang)))

        ## [WINDOWS]
        # Position
        _set_xml_value(config, xml_root, 'window_position', '')
        window_position = _xml_root(config, 'window_position')
        _set_xml_value(config, window_position, 'x', '0')
        _set_xml_value(config, window_position, 'y', '0')
        # Size
        _set_xml_value(config, xml_root, 'window_size', '')
        window_size = _xml_root(config, 'window_size')
        _set_xml_value(config, window_size, 'x', '640')
        _set_xml_value(config, window_size, 'y', '480')

        ## [GAMEPAD]
        _set_xml_value(
            config, xml_root, 'open_pad', self.config.get_bool('cemu_gamepad', return_values=('true', 'false'))
        )
        _set_xml_value(config, xml_root, 'pad_position', '')
        pad_position = _xml_root(config, 'pad_position')
        _set_xml_value(config, pad_position, 'x', '0')
        _set_xml_value(config, pad_position, 'y', '0')
        # Size
        _set_xml_value(config, xml_root, 'pad_size', '')
        pad_size = _xml_root(config, 'pad_size')
        _set_xml_value(config, pad_size, 'x', '640')
        _set_xml_value(config, pad_size, 'y', '480')

        ## [GAME PATH]
        _set_xml_value(config, xml_root, 'GamePaths', '')
        game_root = _xml_root(config, 'GamePaths')
        # Default games path
        _set_xml_value(config, game_root, 'Entry', str(self.roms_dir))

        ## [GRAPHICS]
        _set_xml_value(config, xml_root, 'Graphic', '')
        graphic_root = _xml_root(config, 'Graphic')
        # Graphical backend
        api_value = self.config.get_str('cemu_gfxbackend', '1')  # 1 = Vulkan
        _set_xml_value(config, graphic_root, 'api', api_value)
        # Only set the graphics `device` if Vulkan
        if api_value == '1':
            # Check if we have a discrete GPU & if so, set the UUID
            if vulkan.is_available():
                _logger.debug('Vulkan driver is available on the system.')
                if vulkan.has_discrete_gpu():
                    discrete_uuid = vulkan.get_discrete_gpu_uuid()
                    if discrete_uuid:
                        discrete_uuid_num = discrete_uuid.replace('-', '')
                        _logger.debug('Using Discrete GPU UUID: %s for Cemu', discrete_uuid_num)
                        _set_xml_value(config, graphic_root, 'device', discrete_uuid_num)
                    else:
                        _logger.debug("Couldn't get discrete GPU UUID!")
                else:
                    _logger.debug('Discrete GPU is not available on the system. Using default.')
            else:
                _logger.debug('Vulkan driver is not available on the system. Falling back to OpenGL')
                _set_xml_value(config, graphic_root, 'api', '0')

        # Async VULKAN Shader compilation
        _set_xml_value(
            config,
            graphic_root,
            'AsyncCompile',
            self.config.get_bool('cemu_async', True, return_values=('true', 'false')),
        )
        # Full sync at GX2DrawDone()
        _set_xml_value(
            config,
            graphic_root,
            'GX2DrawdoneSync',
            self.config.get_bool('cemu_gx2drawdone', False, return_values=('true', 'false')),
        )
        # Vsync
        _set_xml_value(config, graphic_root, 'VSync', self.config.get_str('cemu_vsync', '1'))  # 1 = On
        # Upscale Filter
        _set_xml_value(
            config, graphic_root, 'UpscaleFilter', self.config.get_str('cemu_upscale', '2')
        )  # 2 = Hermite
        # Downscale Filter
        _set_xml_value(
            config, graphic_root, 'DownscaleFilter', self.config.get_str('cemu_downscale', '0')
        )  # 0 = Bilinear
        # Fullscreen Scaling (Aspect Ratio fitting)
        _set_xml_value(
            config, graphic_root, 'FullscreenScaling', self.config.get_str('cemu_aspect', '0')
        )  # 0 = Keep Aspect Ratio

        ## [GRAPHICS OVERLAYS] - Currently disabled! Causes crash
        # Performance - alternative to MangoHud
        _set_xml_value(config, graphic_root, 'Overlay', '')
        overlay_root = _xml_root(config, 'Overlay')
        # Display FPS / CPU / GPU / RAM
        if self.config.get_bool('cemu_overlay'):
            _set_xml_value(config, overlay_root, 'Position', '3')
            _set_xml_value(config, overlay_root, 'TextColor', '4294967295')
            _set_xml_value(config, overlay_root, 'TextScale', '100')
            _set_xml_value(config, overlay_root, 'FPS', 'true')
            _set_xml_value(config, overlay_root, 'DrawCalls', 'true')
            _set_xml_value(config, overlay_root, 'CPUUsage', 'true')
            _set_xml_value(config, overlay_root, 'CPUPerCoreUsage', 'true')
            _set_xml_value(config, overlay_root, 'RAMUsage', 'true')
            _set_xml_value(config, overlay_root, 'VRAMUsage', 'true')
        else:
            _set_xml_value(config, overlay_root, 'Position', '3')
            _set_xml_value(config, overlay_root, 'TextColor', '4294967295')
            _set_xml_value(config, overlay_root, 'TextScale', '100')
            _set_xml_value(config, overlay_root, 'FPS', 'false')
            _set_xml_value(config, overlay_root, 'DrawCalls', 'false')
            _set_xml_value(config, overlay_root, 'CPUUsage', 'false')
            _set_xml_value(config, overlay_root, 'CPUPerCoreUsage', 'false')
            _set_xml_value(config, overlay_root, 'RAMUsage', 'false')
            _set_xml_value(config, overlay_root, 'VRAMUsage', 'false')
        # Notifications
        _set_xml_value(config, graphic_root, 'Notification', '')
        notification_root = _xml_root(config, 'Notification')
        if self.config.get_bool('cemu_notifications'):
            _set_xml_value(config, notification_root, 'Position', '1')
            _set_xml_value(config, notification_root, 'TextColor', '4294967295')
            _set_xml_value(config, notification_root, 'TextScale', '100')
            _set_xml_value(config, notification_root, 'ControllerProfiles', 'true')
            _set_xml_value(config, notification_root, 'ControllerBattery', 'true')
            _set_xml_value(config, notification_root, 'ShaderCompiling', 'true')
            _set_xml_value(config, notification_root, 'FriendService', 'true')
        else:
            _set_xml_value(config, notification_root, 'Position', '1')
            _set_xml_value(config, notification_root, 'TextColor', '4294967295')
            _set_xml_value(config, notification_root, 'TextScale', '100')
            _set_xml_value(config, notification_root, 'ControllerProfiles', 'false')
            _set_xml_value(config, notification_root, 'ControllerBattery', 'false')
            _set_xml_value(config, notification_root, 'ShaderCompiling', 'false')
            _set_xml_value(config, notification_root, 'FriendService', 'false')

        ## [AUDIO]
        _set_xml_value(config, xml_root, 'Audio', '')
        audio_root = _xml_root(config, 'Audio')
        # Use cubeb (currently the only option for linux)
        _set_xml_value(config, audio_root, 'api', '3')
        # Turn audio ONLY on TV
        _set_xml_value(config, audio_root, 'TVChannels', self.config.get_str('cemu_audio_channels', '1'))  # 1 = Stereo
        # Set volume to the max
        _set_xml_value(config, audio_root, 'TVVolume', '100')
        # Set the audio device - we choose the 1st device as this is more likely the answer
        proc = subprocess.run(['/usr/bin/cemu/get-audio-device'], stdout=subprocess.PIPE, check=False)
        cemu_audio_device = proc.stdout.decode('utf-8')
        _logger.debug('*** audio device = %s ***', cemu_audio_device)
        if self.config.get_bool('cemu_audio_config', True):
            _set_xml_value(config, audio_root, 'TVDevice', cemu_audio_device)
        else:
            # don't change the config setting
            _logger.debug('*** use config audio device ***')

        # Save the config file
        with config_file.open('w', encoding='utf-8') as xml:
            dom_string = '\n'.join(
                s for s in config.toprettyxml().splitlines() if s.strip()
            )  # remove ugly empty lines while minidom adds them...
            xml.write(dom_string)

    def _write_controller_config(self) -> None:
        # Purge old controller files
        for counter in range(8):
            config_file_name = self.controller_profiles_dir / f'controller{counter}.xml'
            if config_file_name.is_file():
                config_file_name.unlink()

        ## CONTROLLER: Create the config xml files

        # cemu assign pads by uuid then by index with the same uuid
        # so, if 2 pads have the same uuid, the index is not 0 but 1 for the 2nd one
        # sort pads by index
        pads_by_index = sorted(self.controllers, key=lambda pad: pad.index)
        guid_n: dict[int, int] = {}
        guid_count: dict[str, int] = {}
        for pad in pads_by_index:
            if pad.guid in guid_count:
                guid_count[pad.guid] += 1
            else:
                guid_count[pad.guid] = 0
            guid_n[pad.index] = guid_count[pad.guid]

        for nplayer, pad in enumerate(self.controllers):
            root = ET.Element('emulated_controller')

            # Set type from controller combination
            controller_type = _PRO  # default
            match self.config.get_str('cemu_controller_combination'):
                case '1':
                    controller_type = _GAMEPAD if nplayer == 0 else _WIIMOTE
                case '2':
                    controller_type = _PRO
                case '3':
                    controller_type = _WIIMOTE
                case '4':
                    controller_type = _CLASSIC
                case '0' | None:
                    if nplayer == 0:
                        controller_type = _GAMEPAD
            ET.SubElement(root, 'type').text = controller_type

            if _is_wiimote(pad):
                api = _API_WIIMOTE
                ET.SubElement(root, 'device_type').text = _find_wiimote_type(pad)
            else:
                api = _API_SDL

            # Create controller configuration
            controller_node = ET.SubElement(root, 'controller')
            ET.SubElement(controller_node, 'api').text = api
            ET.SubElement(controller_node, 'uuid').text = f'{guid_n[pad.index]}_{pad.guid}'  # controller guid
            ET.SubElement(controller_node, 'display_name').text = pad.real_name  # controller name
            ET.SubElement(controller_node, 'rumble').text = self.config.get_str(
                'cemu_rumble', '0'
            )  # % chosen
            for name in ('axis', 'rotation', 'trigger'):
                analog = ET.SubElement(controller_node, name)
                ET.SubElement(analog, 'deadzone').text = _DEFAULT_DEADZONE
                ET.SubElement(analog, 'range').text = _DEFAULT_RANGE

            # Apply the appropriate button mappings
            mappings_node = ET.SubElement(controller_node, 'mappings')
            mapping = (_BUTTON_MAPPINGS_SDL, _BUTTON_MAPPINGS_WIIMOTE)[_is_wiimote(pad)][controller_type]
            for key, value in mapping.items():
                entry_node = ET.SubElement(mappings_node, 'entry')
                ET.SubElement(entry_node, 'mapping').text = key
                ET.SubElement(entry_node, 'button').text = value

            # Save to file
            with (self.controller_profiles_dir / f'controller{nplayer}.xml').open('wb') as handle:
                tree = ET.ElementTree(root)
                ET.indent(tree, space='  ', level=0)
                tree.write(handle, encoding='UTF-8', xml_declaration=True)

    async def configure(self) -> Command:
        # in case of squashfs, the root directory is passed
        rom_paths = list(self.rom.glob('**/code/*.rpx'))
        rom: Path = rom_paths[0] if rom_paths else self.rom

        self.bios_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # graphic packs
        (self.saves_dir / 'graphicPacks').mkdir(parents=True, exist_ok=True)
        self.controller_profiles_dir.mkdir(parents=True, exist_ok=True)

        # Create the settings file
        self._write_settings_xml()

        # Set-up the controllers
        self._write_controller_config()

        if configure_emulator(rom):
            args: list[str | Path] = ['/usr/bin/cemu/cemu']
        else:
            # No menubar is forced via the persisted 'fullscreen_menubar' setting in settings.xml
            # (see _write_settings_xml): the old '--force-no-menubar' CLI flag was dropped
            # upstream and is now silently ignored (boost::program_options allow_unregistered()).
            args = ['/usr/bin/cemu/cemu', '-f', '-g', rom]

        return Command(
            args,
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'XDG_DATA_HOME': SAVES,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
