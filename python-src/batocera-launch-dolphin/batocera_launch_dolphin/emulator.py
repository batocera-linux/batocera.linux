from __future__ import annotations

import logging
from os import environ
from pathlib import Path
from typing import Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, SAVES
from batocera_common.vulkan import get_discrete_gpu_index, has_discrete_gpu, is_available as vulkan_is_available
from batocera_launch import Command, Emulator, HotkeysContext

from . import controllers, sysconf
from .paths import (
    DOLPHIN_BIOS,
    DOLPHIN_CONFIG,
    DOLPHIN_GFX_INI,
    DOLPHIN_INI,
    DOLPHIN_QT_INI,
    DOLPHIN_SAVES,
    DOLPHIN_SYSCONF,
)

_logger = logging.getLogger(__name__)

_GAMECUBE_LANGUAGES: Final = {'en_US': 0, 'de_DE': 1, 'fr_FR': 2, 'es_ES': 3, 'it_IT': 4, 'nl_NL': 5}


def _gamecube_lang_from_environment() -> int:
    # Get the language from the environment if the user didn't set it in ES. Seems to be
    # only for the gamecube. However, since this isn't in a gamecube-only section, it may
    # be used for something else, so set it anyway.
    return _GAMECUBE_LANGUAGES.get(environ['LANG'][:5], _GAMECUBE_LANGUAGES['en_US'])


@cached_dataclass
class Dolphin(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dolphin',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'previous_slot': ['KEY_LEFTSHIFT', 'KEY_F2'],
                'next_slot': ['KEY_LEFTSHIFT', 'KEY_F1'],
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F8',
                'pause': 'KEY_F10',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        gfx = CaseSensitiveConfigParser(interpolation=None)
        gfx.read(DOLPHIN_GFX_INI)
        aspect_ratio = gfx.get('Settings', 'AspectRatio', fallback='0')

        try:
            wii_tv_mode = sysconf.get_ratio_from_config(self.config, self.resolution)
        except Exception:
            wii_tv_mode = self.config.get_bool('widescreen_hack', return_values=(1, 0))

        if aspect_ratio == '0':  # Auto
            return 16 / 9 if wii_tv_mode == 1 else 4 / 3
        if aspect_ratio == '1':  # Forced 16:9
            return 16 / 9
        if aspect_ratio == '2':  # Forced 4:3
            return 4 / 3
        if aspect_ratio == '3':  # Stretched (depends on physical screen geometry)
            return self.resolution.width / self.resolution.height
        return 4 / 3

    async def configure(self) -> Command:
        DOLPHIN_INI.parent.mkdir(parents=True, exist_ok=True)
        (DOLPHIN_SAVES / 'StateSaves').mkdir(parents=True, exist_ok=True)
        (DOLPHIN_SAVES / 'GameSettings').mkdir(parents=True, exist_ok=True)

        controllers.generate_controller_config(self, self.controllers, self.metadata, self.wheels, self.rom, self.guns)

        ## [ Qt.ini ] ##
        qt_ini = CaseSensitiveConfigParser(interpolation=None)
        if DOLPHIN_QT_INI.exists():
            qt_ini.read(DOLPHIN_QT_INI)

        if not qt_ini.has_section('Emulation'):
            qt_ini.add_section('Emulation')
        qt_ini.set('Emulation', 'StateSlot', self.config.get_str('state_slot', '1'))

        with DOLPHIN_QT_INI.open('w') as fp:
            qt_ini.write(fp)

        ## [ dolphin.ini ] ##
        settings = CaseSensitiveConfigParser(interpolation=None)
        if DOLPHIN_INI.exists():
            settings.read(DOLPHIN_INI)

        for section in ('General', 'Core', 'DSP', 'Interface', 'Analytics', 'Display', 'GBA'):
            if not settings.has_section(section):
                settings.add_section(section)

        # Define default games path
        if 'ISOPaths' not in settings['General']:
            settings.set('General', 'ISOPath0', '/userdata/roms/wii')
            settings.set('General', 'ISOPath1', '/userdata/roms/gamecube')
            settings.set('General', 'ISOPaths', '2')

        settings.set('General', 'AutoIncrementSlot', str(self.config.get_bool('incrementalsavestates', True)))
        settings.set('Analytics', 'PermissionAsked', 'True')  # don't ask about statistics
        settings.set('Interface', 'UsePanicHandlers', 'False')
        settings.set('Interface', 'OnScreenDisplayMessages', str(self.config.get_bool('ShowDpMsg')))
        settings.set('Interface', 'ConfirmStop', 'False')
        settings.remove_option('Display', 'RenderToMain')  # fixes exit and gui display
        settings.set('Display', 'Fullscreen', 'True')
        settings.set('Core', 'EnableCheats', str(self.config.get_bool('enable_cheats')))
        settings.set('Core', 'FastDiscSpeed', str(self.config.get_bool('enable_fastdisc')))
        settings.set('Core', 'CPUThread', str(self.config.get_bool('dual_core')))
        settings.set('Core', 'SyncGPU', str(self.config.get_bool('gpu_sync')))
        settings.set(
            'Core',
            'SelectedLanguage',
            self.config.get_str('gamecube_language') or str(_gamecube_lang_from_environment()),
        )
        settings.set('Core', 'MMU', str(self.config.get_bool('enable_mmu')))

        # Backend - Default OpenGL
        if self.config.get('gfxbackend') == 'Vulkan':
            settings.set('Core', 'GFXBackend', 'Vulkan')
            if not vulkan_is_available():
                _logger.debug('Vulkan driver is not available on the system. Using OpenGL instead.')
                settings.set('Core', 'GFXBackend', 'OGL')
        else:
            settings.set('Core', 'GFXBackend', 'OGL')

        settings.set('Core', 'WiimoteContinuousScanning', 'True')

        # Force OSD for RetroAchievements messages
        if self.config.get_bool('retroachievements'):
            settings.set('Interface', 'OnScreenDisplayMessages', 'True')

        # Gamecube ports
        for i in range(4):
            key = f'dolphin_port_{i + 1}_type'
            value = self.config.get(key)
            if value:
                # Set value to 6 if it is 6a or 6b/6c: differentiates Standard vs GameCube Controller type.
                value = '6' if value in ('6a', '6b', '6c') else value
                settings.set('Core', f'SIDevice{i}', value)
            elif (
                self.system == 'gamecube'
                and self.config.use_wheels
                and self.wheels
                and i < len(self.controllers)
                and self.controllers[i].device_path in self.wheels
            ):
                settings.set('Core', f'SIDevice{i}', '8')
            else:
                settings.set('Core', f'SIDevice{i}', '6')

        # Triforce wheel: both ports must be GC Steering (8) for baseboard detection.
        if self.system == 'triforce' and self.config.use_wheels and self.wheels:
            if not self.config.get('dolphin_port_1_type'):
                settings.set('Core', 'SIDevice0', '8')
            if not self.config.get('dolphin_port_2_type'):
                settings.set('Core', 'SIDevice1', '8')

        # [Light Gun] HiResTextures for crosshair (part 1/2)
        if self.config.use_guns and self.guns and not self.config.get_bool('dolphin_crosshair'):
            settings.set('General', 'CustomTexturesPath', '/usr/share/DolphinCrosshairsPack')
        else:
            settings.remove_option('General', 'CustomTexturesPath')

        settings.set('Core', 'AutoDiscChange', 'True')

        # Skip Menu
        if self.config.get_bool('dolphin_SkipIPL'):
            # check files exist to avoid crashes
            if any((DOLPHIN_BIOS / region / 'IPL.bin').exists() for region in ('USA', 'EUR', 'JAP')):
                settings.set('Core', 'SkipIPL', 'False')
            else:
                settings.set('Core', 'SkipIPL', 'True')
        else:
            settings.set('Core', 'SkipIPL', 'True')

        settings.set('DSP', 'Backend', 'Cubeb')

        # Dolby Pro Logic II for surround sound. DPL II requires DSPHLE to be disabled.
        if self.config.get_bool('dplii'):
            settings.set('Core', 'DPL2Decoder', 'True')
            settings.set('Core', 'DSPHLE', 'False')
            settings.set('DSP', 'EnableJIT', 'True')
        else:
            settings.set('Core', 'DPL2Decoder', 'False')
            settings.set('Core', 'DSPHLE', 'True')
            settings.set('DSP', 'EnableJIT', 'False')

        with DOLPHIN_INI.open('w') as fp:
            settings.write(fp)

        ## [ gfx.ini ] ##
        gfx = CaseSensitiveConfigParser(interpolation=None)
        gfx.read(DOLPHIN_GFX_INI)

        for section in ('Settings', 'Hacks', 'Enhancements', 'Hardware'):
            if not gfx.has_section(section):
                gfx.add_section(section)

        # Set Vulkan adapter
        if vulkan_is_available():
            _logger.debug('Vulkan driver is available on the system.')
            if has_discrete_gpu():
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                discrete_index = get_discrete_gpu_index()
                if discrete_index:
                    _logger.debug('Using Discrete GPU Index: %s for Dolphin', discrete_index)
                    gfx.set('Hardware', 'Adapter', discrete_index)
                else:
                    _logger.debug("Couldn't get discrete GPU index")
            else:
                _logger.debug('Discrete GPU is not available on the system. Using default.')

        # set to zero, which is 'Auto' in Dolphin & Batocera
        gfx.set('Settings', 'AspectRatio', self.config.get('dolphin_aspect_ratio', '0'))
        gfx.set('Settings', 'ShowFPS', str(self.config.show_fps))

        hires_textures = str(self.config.get_bool('hires_textures'))
        gfx.set('Settings', 'HiresTextures', hires_textures)
        gfx.set('Settings', 'CacheHiresTextures', hires_textures)

        # [Light Gun] HiResTextures for crosshair (part 2/2)
        if self.config.use_guns and self.guns and not self.config.get_bool('dolphin_crosshair'):
            # erase what can be set by the option hires_textures
            gfx.set('Settings', 'HiresTextures', 'True')
            gfx.set('Settings', 'CacheHiresTextures', 'True')

        # Widescreen Hack (prefer Cheats than Hack)
        gfx.set(
            'Settings',
            'wideScreenHack',
            str(self.config.get_bool('widescreen_hack') and not self.config.get_bool('enable_cheats')),
        )

        # Ubershaders (synchronous_ubershader by default)
        ubershader = self.config.get('ubershaders', 'no_ubershader')
        gfx.set('Settings', 'ShaderCompilationMode', ubershader if ubershader != 'no_ubershader' else '0')

        gfx.set(
            'Settings',
            'WaitForShadersBeforeStarting',
            str(self.config.get_bool('wait_for_shaders') and self.config.get('gfxbackend') == 'Vulkan'),
        )

        # Various performance hacks - Default Off
        if self.config.get_bool('perf_hacks'):
            gfx.set('Hacks', 'BBoxEnable', 'False')
            gfx.set('Hacks', 'DeferEFBCopies', 'True')
            gfx.set('Hacks', 'EFBEmulateFormatChanges', 'False')
            gfx.set('Hacks', 'EFBScaledCopy', 'True')
            gfx.set('Hacks', 'EFBToTextureEnable', 'True')
            gfx.set('Hacks', 'SkipDuplicateXFBs', 'True')
            gfx.set('Hacks', 'XFBToTextureEnable', 'True')
            gfx.set('Enhancements', 'ForceFiltering', 'True')
            gfx.set('Enhancements', 'ArbitraryMipmapDetection', 'True')
            gfx.set('Enhancements', 'DisableCopyFilter', 'True')
            gfx.set('Enhancements', 'ForceTrueColor', 'True')
        else:
            if gfx.has_section('Hacks'):
                for opt in (
                    'BBoxEnable',
                    'DeferEFBCopies',
                    'EFBEmulateFormatChanges',
                    'EFBScaledCopy',
                    'EFBToTextureEnable',
                    'SkipDuplicateXFBs',
                    'XFBToTextureEnable',
                ):
                    gfx.remove_option('Hacks', opt)
            if gfx.has_section('Enhancements'):
                for opt in ('ForceFiltering', 'ArbitraryMipmapDetection', 'DisableCopyFilter', 'ForceTrueColor'):
                    gfx.remove_option('Enhancements', opt)

        gfx.set('Hacks', 'VISkip', str(self.config.get_bool('vbi_hack')))
        gfx.set('Settings', 'InternalResolution', self.config.get('internal_resolution', '1'))
        gfx.set('Hardware', 'VSync', str(self.config.get_bool('vsync', True)))
        gfx.set('Enhancements', 'MaxAnisotropy', self.config.get('anisotropic_filtering', '0'))
        gfx.set('Settings', 'MSAA', self.config.get('antialiasing', '0'))
        gfx.set('Settings', 'SSAA', str(self.config.get_bool('use_ssaa')))
        # Manual texture sampling: on = speed hack off. off = speed hack on
        gfx.set('Hacks', 'FastTextureSampling', str(not self.config.get_bool('manual_texture_sampling')))

        with DOLPHIN_GFX_INI.open('w') as fp:
            gfx.write(fp)

        ## Hotkeys.ini - overwrite to avoid issues
        hotkeys = CaseSensitiveConfigParser(interpolation=None)
        hotkeys.add_section('Hotkeys')
        hotkeys.set('Hotkeys', 'Device', 'XInput2/0/Virtual core pointer')
        hotkeys.set('Hotkeys', 'General/Open', '@(Ctrl+O)')
        hotkeys.set('Hotkeys', 'General/Toggle Pause', 'F10')
        hotkeys.set('Hotkeys', 'General/Stop', 'Escape')
        hotkeys.set('Hotkeys', 'General/Toggle Fullscreen', '@(Alt+Return)')
        hotkeys.set('Hotkeys', 'General/Take Screenshot', 'F9')
        hotkeys.set('Hotkeys', 'General/Exit', '@(Shift+F11)')
        hotkeys.set('Hotkeys', 'Emulation Speed/Disable Emulation Speed Limit', 'Tab')
        hotkeys.set('Hotkeys', 'Stepping/Step Into', 'F11')
        hotkeys.set('Hotkeys', 'Stepping/Step Over', '@(Shift+F10)')
        hotkeys.set('Hotkeys', 'Stepping/Step Out', '@(Shift+F11)')
        hotkeys.set('Hotkeys', 'Breakpoint/Toggle Breakpoint', '@(Shift+F9)')
        hotkeys.set('Hotkeys', 'Wii/Connect Wii Remote 1', '@(Alt+F5)')
        hotkeys.set('Hotkeys', 'Wii/Connect Wii Remote 2', '@(Alt+F6)')
        hotkeys.set('Hotkeys', 'Wii/Connect Wii Remote 3', '@(Alt+F7)')
        hotkeys.set('Hotkeys', 'Wii/Connect Wii Remote 4', '@(Alt+F8)')
        hotkeys.set('Hotkeys', 'Wii/Connect Balance Board', '@(Alt+F9)')
        hotkeys.set('Hotkeys', 'Other State Hotkeys/Increase Selected State Slot', '@(Shift+F1)')
        hotkeys.set('Hotkeys', 'Other State Hotkeys/Decrease Selected State Slot', '@(Shift+F2)')
        hotkeys.set('Hotkeys', 'Load State/Load from Selected Slot', 'F8')
        hotkeys.set('Hotkeys', 'Save State/Save to Selected Slot', 'F5')
        hotkeys.set('Hotkeys', 'Other State Hotkeys/Undo Load State', '@(Shift+F12)')
        hotkeys.set('Hotkeys', 'GBA Core/Load ROM', '@(`Ctrl`+`Shift`+`O`)')
        hotkeys.set('Hotkeys', 'GBA Core/Unload ROM', '@(`Ctrl`+`Shift`+`W`)')
        hotkeys.set('Hotkeys', 'GBA Core/Reset', '@(`Ctrl`+`Shift`+`R`)')
        hotkeys.set('Hotkeys', 'GBA Volume/Volume Down', '`KP_Subtract`')
        hotkeys.set('Hotkeys', 'GBA Volume/Volume Up', '`KP_Add`')
        hotkeys.set('Hotkeys', 'GBA Volume/Volume Toggle Mute', '`M`')
        hotkeys.set('Hotkeys', 'GBA Window Size/1x', '`KP_1`')
        hotkeys.set('Hotkeys', 'GBA Window Size/2x', '`KP_2`')
        hotkeys.set('Hotkeys', 'GBA Window Size/3x', '`KP_3`')
        hotkeys.set('Hotkeys', 'GBA Window Size/4x', '`KP_4`')
        hotkeys.set('Hotkeys', 'USB Emulation Devices/Show Skylanders Portal', '@(Ctrl+P)')
        hotkeys.set('Hotkeys', 'USB Emulation Devices/Show Infinity Base', '@(Ctrl+I)')
        with (DOLPHIN_CONFIG / 'Hotkeys.ini').open('w') as fp:
            hotkeys.write(fp)

        ## RetroAchievements
        rac_config = CaseSensitiveConfigParser(interpolation=None)
        rac_config.add_section('Achievements')
        if self.config.get_bool('retroachievements'):
            rac_config.set('Achievements', 'Enabled', 'True')
            rac_config.set('Achievements', 'AchievementsEnabled', 'True')
            rac_config.set('Achievements', 'Username', self.config.get('retroachievements.username', ''))
            rac_config.set('Achievements', 'ApiToken', self.config.get('retroachievements.token', ''))
            rac_config.set('Achievements', 'HardcoreEnabled', self.config.get('retroachievements.hardcore', 'False'))
            rac_config.set('Achievements', 'BadgesEnabled', self.config.get('retroachievements.verbose', 'False'))
            rac_config.set('Achievements', 'EncoreEnabled', self.config.get('retroachievements.encore', 'False'))
            rac_config.set(
                'Achievements', 'ProgressEnabled', self.config.get('retroachievements.challenge_indicators', 'False')
            )
            rac_config.set(
                'Achievements', 'LeaderboardsEnabled', self.config.get('retroachievements.leaderboard', 'False')
            )
            rac_config.set(
                'Achievements', 'RichPresenceEnabled', self.config.get('retroachievements.richpresence', 'False')
            )
            rac_config.set(
                'Achievements', 'UnofficialEnabled', self.config.get('retroachievements.unofficial', 'False')
            )
        else:
            rac_config.set('Achievements', 'Enabled', 'False')
            rac_config.set('Achievements', 'AchievementsEnabled', 'False')
        with (DOLPHIN_CONFIG / 'RetroAchievements.ini').open('w') as fp:
            rac_config.write(fp)

        # Update SYSCONF
        try:
            sysconf.update(self.config, DOLPHIN_SYSCONF, self.resolution)
        except Exception:
            _logger.debug("couldn't update SYSCONF", exc_info=True)  # don't fail in case of SYSCONF update

        # Check what version we've got
        if Path('/usr/bin/dolphin-emu').is_file():
            # use the -b 'batch' option for nicer exit
            args: list[str | Path] = ['dolphin-emu', '-b', '-e', self.rom]
        else:
            args = ['dolphin-emu-nogui', '-e', self.rom]

        if state_filename := self.config.get('state_filename'):
            args.extend(['--save_state', state_filename])

        return Command(
            args,
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
                'XDG_CACHE_HOME': CACHE,
            },
        )
