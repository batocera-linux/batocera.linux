from __future__ import annotations

from os import environ
from typing import TYPE_CHECKING

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext

from . import controllers
from .paths import MUPEN64PLUS_CONFIG, MUPEN64PLUS_CUSTOM_CFG, MUPEN64PLUS_SAVES

if TYPE_CHECKING:
    from pathlib import Path


def _clean_hotkey_config(ini_config: CaseSensitiveConfigParser, /) -> None:
    if not ini_config.has_section('CoreEvents'):
        return  # nothing needs to be done

    ini_config.set('CoreEvents', 'Version', '1')
    ini_config.set('CoreEvents', 'Joy Mapping Stop', '')
    ini_config.set('CoreEvents', 'Joy Mapping Save State', '')
    ini_config.set('CoreEvents', 'Joy Mapping Load State', '')
    ini_config.set('CoreEvents', 'Joy Mapping Screenshot', '')
    ini_config.set('CoreEvents', 'Joy Mapping Increment Slot', '')
    ini_config.set('CoreEvents', 'Joy Mapping Fast Forward', '')
    ini_config.set('CoreEvents', 'Joy Mapping Reset', '')
    ini_config.set('CoreEvents', 'Joy Mapping Pause', '')


@cached_dataclass
class Mupen64Plus(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'mupen64',
            'keys': {
                'exit': 'KEY_ESC',
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F7',
                'menu': 'KEY_P',
                'pause': 'KEY_P',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        return MUPEN64PLUS_CONFIG

    @cached_property
    def saves_dir(self) -> Path:
        return MUPEN64PLUS_SAVES

    @cached_property
    def in_game_ratio(self) -> float:
        mupen_ratio = self.config.get('mupen64plus_ratio')
        if mupen_ratio == '16/9' or (not mupen_ratio and self.config.get('ratio') == '16/9'):
            return 16 / 9
        return 4 / 3

    async def configure(self) -> Command:
        # Read the configuration file
        ini_config = CaseSensitiveConfigParser(interpolation=None)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if MUPEN64PLUS_CUSTOM_CFG.exists():
            ini_config.read(MUPEN64PLUS_CUSTOM_CFG)

        self._set_mupen_config(ini_config)
        controllers.set_controllers_config(ini_config, self.controllers, self.config, self.wheels)

        # Save the ini file
        with MUPEN64PLUS_CUSTOM_CFG.open('w') as config_file:
            ini_config.write(config_file)

        # Command
        args: list[str | Path] = [
            '/usr/bin/mupen64plus',
            '--corelib',
            '/usr/lib/libmupen64plus.so.2.0.0',
            '--gfx',
            f'/usr/lib/mupen64plus/mupen64plus-video-{self.core}.so',
            '--configdir',
            MUPEN64PLUS_CONFIG,
            '--datadir',
            MUPEN64PLUS_CONFIG,
        ]

        # state_filename option
        if state_filename := self.config.get('state_filename'):
            args.extend(['--savestate', state_filename])

        # custom cheats option
        if cheats := self.config.get_str('mupen64plus_cheats', '').strip():
            args.extend(['--cheats', cheats])

        args.append(self.rom)

        return Command(args)

    def _set_mupen_config(self, ini_config: CaseSensitiveConfigParser, /) -> None:
        # Hotkeys
        _clean_hotkey_config(ini_config)

        # Paths
        if not ini_config.has_section('Core'):
            ini_config.add_section('Core')
        ini_config.set(
            'Core', 'Version', '1.01'
        )  # Version is important for the .ini creation otherwise, mupen remove the section
        ini_config.set('Core', 'ScreenshotPath', str(SCREENSHOTS))
        ini_config.set('Core', 'SaveStatePath', str(MUPEN64PLUS_SAVES))
        ini_config.set('Core', 'SaveSRAMPath', str(MUPEN64PLUS_SAVES))
        ini_config.set('Core', 'SharedDataPath', str(MUPEN64PLUS_CONFIG))
        ini_config.set('Core', 'SaveFilenameFormat', '1000')  # forces savesstates with rom name
        # TODO : Miss Mupen64Plus\hires_texture

        # 4MB RAM Extention Pack
        ini_config.set('Core', 'DisableExtraMem', str(self.config.get_bool('mupen64plus_DisableExtraMem')))

        # state_slot option, AutoStateSlotIncrement could be set too depending on the es option
        if state_slot := self.config.get_str('state_slot'):
            ini_config.set('Core', 'CurrentStateSlot', state_slot)

        # increment savestates
        ini_config.set('Core', 'AutoStateSlotIncrement', str(self.config.get_bool('incrementalsavestates', True)))

        # Create section for Audio-SDL
        if not ini_config.has_section('Audio-SDL'):
            ini_config.add_section('Audio-SDL')

        # Default to disable while it causes issues
        ini_config.set('Audio-SDL', 'AUDIO_SYNC', str(self.config.get_bool('mupen64plus_AudioSync')))

        # Audio buffer settings
        # In the future, add for Audio-OMX too?
        match self.config.get('mupen64plus_AudioBuffer'):
            case 'Very High':
                primary_buffer_size = '16384'
                primary_buffer_target = '4096'
                secondary_buffer_size = '2048'
            case 'High':  # (defaults provided by mupen64plus)
                primary_buffer_size = '16384'
                primary_buffer_target = '2048'
                secondary_buffer_size = '1024'
            case 'Low':
                primary_buffer_size = '4096'
                primary_buffer_target = '1024'
                secondary_buffer_size = '512'
            case _:  # Medium
                primary_buffer_size = '8192'
                primary_buffer_target = '2048'
                secondary_buffer_size = '1024'

        ini_config.set('Audio-SDL', 'PRIMARY_BUFFER_SIZE', primary_buffer_size)
        ini_config.set('Audio-SDL', 'PRIMARY_BUFFER_TARGET', primary_buffer_target)
        ini_config.set('Audio-SDL', 'SECONDARY_BUFFER_SIZE', secondary_buffer_size)

        # Invert required when screen is rotated
        if self.resolution.width < self.resolution.height:
            width = self.resolution.height
            height = self.resolution.width
        else:
            width = self.resolution.width
            height = self.resolution.height

        # Internal Resolution
        if not ini_config.has_section('Video-General'):
            ini_config.add_section('Video-General')
        ini_config.set('Video-General', 'Version', '1')
        ini_config.set('Video-General', 'ScreenWidth', str(width))
        ini_config.set('Video-General', 'ScreenHeight', str(height))

        # Set fullscreen to True on Wayland, False otherwise (due to issues on Xorg/DRM)
        fullscreen_val = 'True' if 'WAYLAND_DISPLAY' in environ else 'False'
        ini_config.set('Video-General', 'Fullscreen', fullscreen_val)
        ini_config.set('Video-General', 'VerticalSync', 'True')

        # Graphic Plugins
        # DOC : https://github.com/mupen64plus/mupen64plus-video-glide64mk2/blob/master/src/Glide64/Main.cpp
        if not ini_config.has_section('Video-Glide64mk2'):
            ini_config.add_section('Video-Glide64mk2')
        if not ini_config.has_section('Video-GLideN64'):
            ini_config.add_section('Video-GLideN64')
        # https://mupen64plus.org/wiki/index.php?title=Mupen64Plus_Plugin_Parameters
        # https://github.com/mupen64plus/mupen64plus-video-rice/blob/master/src/Config.cpp
        if not ini_config.has_section('Video-Rice'):
            ini_config.add_section('Video-Rice')

        ini_config.set('Video-Rice', 'Version', '1')
        ini_config.set('Video-Glide64mk2', 'Version', '1')

        # Widescreen Mode -> ONLY for GLIDE64 & MK2
        mupen_ratio = self.config.get('mupen64plus_ratio')
        ratio = self.config.get('ratio')

        if mupen_ratio == '16/9' or (not mupen_ratio and ratio == '16/9'):
            adjust_aspect = '1'
            aspect = '1'
            aspect_ratio = '2'
        elif mupen_ratio == '4/3' or (not mupen_ratio and ratio == '4/3'):
            adjust_aspect = '0'
            aspect = '0'
            aspect_ratio = '1'
        else:
            adjust_aspect = '-1'
            aspect = '-1'
            aspect_ratio = '3'

        # Glide64mk2.: Adjust screen aspect for wide screen mode: -1=Game default, 0=disable. 1=enable
        ini_config.set('Video-Glide64mk2', 'adjust_aspect', adjust_aspect)
        # Glide64mk2.: Aspect ratio: -1=Game default, 0=Force 4:3, 1=Force 16:9, 2=Stretch, 3=Original
        ini_config.set('Video-Glide64mk2', 'aspect', aspect)
        # GLideN64.: Screen aspect ratio (0=stretch, 1=force 4:3, 2=force 16:9, 3=adjust)
        ini_config.set('Video-GLideN64', 'AspectRatio', aspect_ratio)

        # Textures Mip-Mapping (Filtering)
        match mipmapping := self.config.get('mupen64plus_Mipmapping', '0'):
            case '1':
                filtering = '0'
            case '2':
                filtering = '1'
            case '3':
                filtering = '2'
                mipmapping = '3'
            case _:
                filtering = '-1'

        ini_config.set('Video-Rice', 'Mipmapping', mipmapping)  # 0=no, 1=nearest, 2=bilinear, 3=trilinear
        ini_config.set(
            'Video-Glide64mk2', 'filtering', filtering
        )  # -1=Game default, 0=automatic, 1=force bilinear, 2=force point sampled

        # Anisotropic Filtering
        anisotropic = self.config.get('mupen64plus_Anisotropic', '0')

        # Enable/Disable Anisotropic Filtering for Mipmapping (0=no filtering, 2-16=quality).
        ini_config.set('Video-Rice', 'AnisotropicFiltering', anisotropic)
        # Wrapper Anisotropic Filtering
        # This is uneffective if Mipmapping is false.
        ini_config.set('Video-Glide64mk2', 'wrpAnisotropic', '1' if anisotropic == '0' else anisotropic)

        # Anti-aliasing MSAA
        antialiasing = self.config.get('mupen64plus_AntiAliasing', '0')
        ini_config.set('Video-Rice', 'MultiSampling', antialiasing)  # 0=off, 2, 4, 8, 16=quality
        ini_config.set(
            'Video-Glide64mk2', 'wrpAntiAliasing', antialiasing
        )  # Enable full-scene anti-aliasing by setting this to a value greater than 1

        # Hires textures
        load_hires_textures = self.config.get_bool('mupen64plus_LoadHiResTextures')
        ini_config.set('Video-Rice', 'LoadHiResTextures', str(load_hires_textures))
        ini_config.set(
            'Video-Glide64mk2', 'ghq_hirs', '1' if load_hires_textures else '0'
        )  # Hi-res texture pack format (0 for none, 1 for Rice)

        # Texture Enhencement XBRZ -> ONLY for RICE
        # 0=None, 1=2X, 2=2XSAI, 3=HQ2X, 4=LQ2X, 5=HQ4X, 6=Sharpen, 7=Sharpen More, 8=External, 9=Mirrored
        ini_config.set('Video-Rice', 'TextureEnhancement', self.config.get('mupen64plus_TextureEnhancement', '0'))

        # Frameskip -> ONLY for GLIDE64MK2
        autoframeskip = '0'
        ini_config.set('Video-Glide64mk2', 'autoframeskip', '0')
        match self.config.get('mupen64plus_frameskip', '0'):
            case 'automatic':
                # If true, skip up to maxframeskip frames to maintain clock schedule; if false, skip exactly maxframeskip frames
                autoframeskip = '1'
                maxframeskip = '5'
            case '0':
                maxframeskip = '0'
            case _ as frameskip:
                # If autoframeskip is false, skip exactly this many frames
                maxframeskip = frameskip

        ini_config.set('Video-Glide64mk2', 'autoframeskip', autoframeskip)
        ini_config.set('Video-Glide64mk2', 'maxframeskip', maxframeskip)

        # Read framebuffer always -> for GLIDE64MK2
        ini_config.set('Video-Glide64mk2', 'fb_read_always', self.config.get('mupen64plus_fb_read_always', '-1'))

        # 64DD
        if not ini_config.has_section('64DD'):
            ini_config.add_section('64DD')
        # Filename of the 64DD IPL ROM
        if self.system == 'n64dd':
            ini_config.set('64DD', 'IPL-ROM', str(BIOS / '64DD_IPL.bin'))
        else:
            ini_config.set('64DD', 'IPL-ROM', '')
        ini_config.set('64DD', 'Disk', '')

        # Display FPS
        if self.config.show_fps:
            ini_config.set('Video-Rice', 'ShowFPS', 'True')
            ini_config.set('Video-Glide64mk2', 'show_fps', '4')
        else:
            ini_config.set('Video-Rice', 'ShowFPS', 'False')
            ini_config.set(
                'Video-Glide64mk2', 'show_fps', '8'
            )  # 1=FPS counter, 2=VI/s counter, 4=% speed, 8=FPS transparent

            # Custom : allow the user to configure directly mupen64plus.cfg via batocera.conf via lines like : n64.mupen64plus.section.option=value
            # NOTE: ported as-is from the old configgen generator, including this indentation - the custom-override
            # loop below only runs when show_fps is False there too. This looks like a pre-existing bug (the loop
            # is almost certainly meant to be unconditional), kept unchanged here to preserve exact behavior; flagged
            # for the user to decide whether to fix separately.
            for section_option, user_config_value in self.config.items(starts_with='mupen64plus.'):
                custom_section, _, custom_option = section_option.partition('.')
                if not ini_config.has_section(custom_section):
                    ini_config.add_section(custom_section)
                ini_config.set(custom_section, custom_option, str(user_config_value))
