from __future__ import annotations

import logging
import re
import shutil
import time
from pathlib import Path
from typing import Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS
from batocera_common.vulkan import get_discrete_gpu_name, has_discrete_gpu, is_available
from batocera_launch import Command, Emulator, HotkeysContext, Input
from batocera_launch.paths import DATAINIT_DIR, configure_emulator

_logger = logging.getLogger(__name__)

_PCSX2_BIN_DIR: Final = Path('/usr/pcsx2/bin')
_PCSX2_RESOURCES_DIR: Final = _PCSX2_BIN_DIR / 'resources'

# PCSX2/Pad.cpp Pad_subtype values for the wheel devices we support
_WHEEL_TYPE_MAPPING: Final = {
    'DrivingForce': '0',
    'DrivingForcePro': '1',
    'GTForce': '3',
}

_VALID_SONY_GUIDS: Final = (
    # ds3
    '030000004c0500006802000011010000',
    '030000004c0500006802000011810000',
    '050000004c0500006802000000800000',
    '050000004c0500006802000000000000',
    # ds4
    '030000004c050000c405000011810000',
    '050000004c050000c405000000810000',
    '030000004c050000cc09000011010000',
    '050000004c050000cc09000000010000',
    '030000004c050000cc09000011810000',
    '050000004c050000cc09000000810000',
    '030000004c050000a00b000011010000',
    '030000004c050000a00b000011810000',
    # ds5
    '030000004c050000e60c000011810000',
    '050000004c050000e60c000000810000',
)

_WHEEL_MAPPING: Final = {
    'DrivingForcePro': {
        'up': 'Pad_DPadUp',
        'down': 'Pad_DPadDown',
        'left': 'Pad_DPadLeft',
        'right': 'Pad_DPadRight',
        'start': 'Pad_Start',
        'select': 'Pad_Select',
        'a': 'Pad_Circle',
        'b': 'Pad_Cross',
        'x': 'Pad_Triangle',
        'y': 'Pad_Square',
        'pageup': 'Pad_L1',
        'pagedown': 'Pad_R1',
    },
    'DrivingForce': {
        'up': 'Pad_DPadUp',
        'down': 'Pad_DPadDown',
        'left': 'Pad_DPadLeft',
        'right': 'Pad_DPadRight',
        'start': 'Pad_Start',
        'select': 'Pad_Select',
        'a': 'Pad_Circle',
        'b': 'Pad_Cross',
        'x': 'Pad_Triangle',
        'y': 'Pad_Square',
        'pageup': 'Pad_L1',
        'pagedown': 'Pad_R1',
    },
    'GTForce': {
        'a': 'Pad_Y',
        'b': 'Pad_B',
        'x': 'Pad_X',
        'y': 'Pad_A',
        'pageup': 'Pad_MenuDown',
        'pagedown': 'Pad_MenuUp',
    },
}


def _input_to_wheel(inp: Input, reversed_axis: bool | None = False) -> str | None:
    if inp.type == 'button':
        pcsx2_magic_button_offset = (
            21  # PCSX2/SDLInputSource.cpp : const u32 button = ev->button + std::size(s_sdl_button_names)
        )
        return f'Button{int(inp.id) + pcsx2_magic_button_offset}'
    if inp.type == 'hat':
        direction = 'unknown'
        if inp.value == '1':
            direction = 'North'
        elif inp.value == '2':
            direction = 'East'
        elif inp.value == '4':
            direction = 'South'
        elif inp.value == '8':
            direction = 'West'
        return f'Hat{inp.id}{direction}'
    if inp.type == 'axis':
        pcsx2_magic_axis_offset = (
            6  # PCSX2/SDLInputSource.cpp : const u32 axis = ev->axis + std::size(s_sdl_axis_names);
        )
        if reversed_axis is None:
            return f'FullAxis{int(inp.id) + pcsx2_magic_axis_offset}~'
        direction = '+' if reversed_axis else '-'
        return f'{direction}Axis{int(inp.id) + pcsx2_magic_axis_offset}'
    return None


@cached_dataclass
class Pcsx2(Emulator):
    needs_sdl_controller_db = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'pcsx2',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F1',
                'restore_state': 'KEY_F3',
                'previous_slot': ['KEY_LEFTSHIFT', 'KEY_F2'],
                'next_slot': 'KEY_F2',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        # the folder is historically mixed-case on disk; keep it as-is
        return CONFIGS / 'PCSX2'

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.config_dir / 'game_controller_db.txt'

    @cached_property
    def in_game_ratio(self) -> float:
        config_ratio = self.config.get('pcsx2_ratio')
        if config_ratio == '16:9' or (
            config_ratio == 'Stretch' and self.resolution.width / float(self.resolution.height) > ((16.0 / 9.0) - 0.1)
        ):
            return 16 / 9
        return 4 / 3

    @cached_property
    def _playing_with_wheel(self) -> bool:
        return bool(self.config.use_wheels and self.wheels)

    @cached_property
    def _wheel_type(self) -> str:
        if not self._playing_with_wheel:
            return 'Virtual'
        wheel_type = self.metadata.get('wheel_type', 'Virtual')
        if config_wheel_type := self.config.get('pcsx2_wheel_type'):
            wheel_type = config_wheel_type
        if wheel_type not in _WHEEL_TYPE_MAPPING:
            wheel_type = 'Virtual'
        return wheel_type

    @cached_property
    def _use_emulator_wheels(self) -> bool:
        # the virtual type is the virtual wheel that use a physical wheel to manipulate the pad
        return self._playing_with_wheel and self._wheel_type != 'Virtual'

    async def configure(self) -> Command:
        pcsx2_patches = self.bios_dir / 'patches.zip'

        # Remove older config files if present
        inis_dir = self.config_dir / 'inis'
        for filename in ('PCSX2_ui.ini', 'PCSX2_vm.ini', 'GS.ini'):
            file_path = inis_dir / filename
            if file_path.exists():
                file_path.unlink()

        # Config files
        self._configure_reg()
        self._configure_ini()
        self._configure_audio()

        command_array: list[str | Path] = (
            ['/usr/pcsx2/bin/pcsx2-qt']
            if configure_emulator(self.rom)
            else ['/usr/pcsx2/bin/pcsx2-qt', '-nogui', self.rom]
        )

        with Path('/proc/cpuinfo').open() as cpuinfo:
            if not re.search(r'^flags\s*:.*\ssse4_1\W', cpuinfo.read(), re.MULTILINE):
                _logger.warning(
                    'CPU does not support SSE4.1 which is required by pcsx2.  '
                    'The emulator will likely crash with SIGILL (illegal instruction).'
                )

        envcmd: dict[str, str | Path] = {'XDG_CONFIG_HOME': CONFIGS}

        # wheels won't work correctly when SDL_GAMECONTROLLERCONFIG is set. excluding wheels
        # from SDL_GAMECONTROLLERCONFIG doesn't fix too.
        if not self._use_emulator_wheels:
            envcmd['SDL_GAMECONTROLLERCONFIG'] = self.get_sdl_game_controller_config()

        # ensure we have the patches.zip file to avoid message.
        pcsx2_patches.parent.mkdir(parents=True, exist_ok=True)
        if not pcsx2_patches.exists():
            shutil.copy(DATAINIT_DIR / 'bios' / 'ps2' / 'patches.zip', pcsx2_patches)

        # state_slot option
        if state_filename := self.config.get('state_filename'):
            command_array.extend(['-statefile', state_filename])

        if state_slot := self.config.get_str('state_slot'):
            command_array.extend(['-stateindex', state_slot])

        return Command(command_array, env=envcmd)

    def _configure_reg(self) -> None:
        config_directory = self.config_dir
        config_directory.mkdir(parents=True, exist_ok=True)
        with (config_directory / 'PCSX2-reg.ini').open('w') as f:
            f.write('DocumentsFolderMode=User\n')
            f.write(f'CustomDocumentsFolder={_PCSX2_BIN_DIR}\n')
            f.write('UseDefaultSettingsFolder=enabled\n')
            f.write(f'SettingsFolder={config_directory / "inis"}\n')
            f.write(f'Install_Dir={_PCSX2_BIN_DIR}\n')
            f.write('RunWizard=0\n')

    def _configure_audio(self) -> None:
        config_file_name = self.config_dir / 'inis' / 'spu2-x.ini'
        config_file_name.parent.mkdir(parents=True, exist_ok=True)

        # Keep the custom files
        if config_file_name.exists():
            return

        with config_file_name.open('w') as f:
            f.write('[MIXING]\n')
            f.write('Interpolation=1\n')
            f.write('Disable_Effects=0\n')
            f.write('[OUTPUT]\n')
            f.write('Output_Module=SDLAudio\n')
            f.write('[PORTAUDIO]\n')
            f.write('HostApi=ALSA\n')
            f.write('Device=default\n')
            f.write('[SDL]\n')
            f.write('HostApi=alsa\n')

    def _configure_ini(self) -> None:
        config_directory = self.config_dir
        config_file_name = config_directory / 'inis' / 'PCSX2.ini'

        config_file_name.parent.mkdir(parents=True, exist_ok=True)

        if not config_file_name.is_file():
            with config_file_name.open('w') as f:
                f.write('[UI]\n')

        pcsx2_ini_config = CaseSensitiveConfigParser(interpolation=None)
        pcsx2_ini_config.read(config_file_name)

        ## [UI]
        if not pcsx2_ini_config.has_section('UI'):
            pcsx2_ini_config.add_section('UI')

        # set the settings we want always enabled
        pcsx2_ini_config.set('UI', 'SettingsVersion', '1')
        pcsx2_ini_config.set('UI', 'InhibitScreensaver', 'true')
        pcsx2_ini_config.set('UI', 'ConfirmShutdown', 'false')
        pcsx2_ini_config.set('UI', 'StartPaused', 'false')
        pcsx2_ini_config.set('UI', 'PauseOnFocusLoss', 'false')
        pcsx2_ini_config.set('UI', 'StartFullscreen', 'true')
        pcsx2_ini_config.set('UI', 'HideMouseCursor', 'true')
        pcsx2_ini_config.set('UI', 'RenderToSeparateWindow', 'false')
        pcsx2_ini_config.set('UI', 'HideMainWindowWhenRunning', 'true')
        pcsx2_ini_config.set('UI', 'DoubleClickTogglesFullscreen', 'false')

        # clear to not have the window anywhere when switching from multi to single screen and vice and versa
        for opt in ('MainWindowGeometry', 'MainWindowState', 'DisplayWindowGeometry'):
            if pcsx2_ini_config.has_option('UI', opt):
                pcsx2_ini_config.remove_option('UI', opt)

        ## [Folders]
        if not pcsx2_ini_config.has_section('Folders'):
            pcsx2_ini_config.add_section('Folders')

        # remove inconsistent SaveStates casing if it exists
        pcsx2_ini_config.remove_option('Folders', 'SaveStates')

        # set the folders we want
        pcsx2_ini_config.set('Folders', 'Bios', '../../../bios/ps2')
        pcsx2_ini_config.set('Folders', 'Snapshots', '../../../screenshots')
        pcsx2_ini_config.set('Folders', 'Savestates', '../../../saves/ps2/pcsx2/sstates')
        pcsx2_ini_config.set('Folders', 'MemoryCards', '../../../saves/ps2/pcsx2')
        pcsx2_ini_config.set('Folders', 'Logs', '../../logs')
        pcsx2_ini_config.set('Folders', 'Cheats', '../../../cheats/ps2')
        pcsx2_ini_config.set('Folders', 'CheatsWS', '../../../cheats/ps2/cheats_ws')
        pcsx2_ini_config.set('Folders', 'CheatsNI', '../../../cheats/ps2/cheats_ni')
        pcsx2_ini_config.set('Folders', 'Cache', '../../cache/ps2')
        pcsx2_ini_config.set('Folders', 'Textures', 'textures')
        pcsx2_ini_config.set('Folders', 'InputProfiles', 'inputprofiles')
        pcsx2_ini_config.set('Folders', 'Videos', '../../../saves/ps2/pcsx2/videos')

        # create cache folder
        (CACHE / 'ps2').mkdir(parents=True, exist_ok=True)

        ## [EmuCore]
        if not pcsx2_ini_config.has_section('EmuCore'):
            pcsx2_ini_config.add_section('EmuCore')

        # set the settings we want always enabled
        pcsx2_ini_config.set('EmuCore', 'EnableDiscordPresence', 'false')

        # Fastboot
        pcsx2_ini_config.set(
            'EmuCore', 'EnableFastBoot', self.config.get_bool('pcsx2_fastboot', True, return_values=('false', 'true'))
        )

        # Cheats
        pcsx2_ini_config.set('EmuCore', 'EnableCheats', self.config.get('pcsx2_cheats', 'false'))

        # Widescreen Patches
        pcsx2_ini_config.set(
            'EmuCore', 'EnableWideScreenPatches', self.config.get('pcsx2_EnableWideScreenPatches', 'false')
        )

        # No-interlacing Patches
        pcsx2_ini_config.set(
            'EmuCore', 'EnableNoInterlacingPatches', self.config.get('pcsx2_interlacing_patches', 'false')
        )

        ## [Achievements]
        if not pcsx2_ini_config.has_section('Achievements'):
            pcsx2_ini_config.add_section('Achievements')
        pcsx2_ini_config.set('Achievements', 'Enabled', 'false')
        if self.config.get_bool('retroachievements'):
            username = self.config.get('retroachievements.username', '')
            token = self.config.get('retroachievements.token', '')
            pcsx2_ini_config.set('Achievements', 'Enabled', 'true')
            pcsx2_ini_config.set('Achievements', 'Username', username)
            pcsx2_ini_config.set('Achievements', 'Token', token)
            pcsx2_ini_config.set('Achievements', 'LoginTimestamp', str(int(time.time())))
            pcsx2_ini_config.set(
                'Achievements',
                'ChallengeMode',
                self.config.get_bool('retroachievements.hardcore', return_values=('true', 'false')),
            )
            pcsx2_ini_config.set(
                'Achievements',
                'PrimedIndicators',
                self.config.get_bool('retroachievements.challenge_indicators', return_values=('true', 'false')),
            )
            pcsx2_ini_config.set(
                'Achievements',
                'RichPresence',
                self.config.get_bool('retroachievements.richpresence', return_values=('true', 'false')),
            )
            pcsx2_ini_config.set(
                'Achievements',
                'Leaderboards',
                self.config.get_bool('retroachievements.leaderboards', return_values=('true', 'false')),
            )
            pcsx2_ini_config.set(
                'Achievements',
                'EncoreMode',
                self.config.get_bool('retroachievements.encore', return_values=('true', 'false')),
            )
            pcsx2_ini_config.set(
                'Achievements',
                'UnofficialTestMode',
                self.config.get_bool('retroachievements.unofficial', return_values=('true', 'false')),
            )
        # set other settings
        pcsx2_ini_config.set('Achievements', 'TestMode', 'false')
        pcsx2_ini_config.set('Achievements', 'UnofficialTestMode', 'false')
        pcsx2_ini_config.set('Achievements', 'Notifications', 'true')
        pcsx2_ini_config.set('Achievements', 'SoundEffects', 'true')

        ## [Filenames]
        if not pcsx2_ini_config.has_section('Filenames'):
            pcsx2_ini_config.add_section('Filenames')

        ## [EmuCore/GS]
        if not pcsx2_ini_config.has_section('EmuCore/GS'):
            pcsx2_ini_config.add_section('EmuCore/GS')

        ## [EmuCore/Speedhacks]
        if not pcsx2_ini_config.has_section('EmuCore/Speedhacks'):
            pcsx2_ini_config.add_section('EmuCore/Speedhacks')

        # Renderer
        # Check Vulkan first to be sure
        if is_available():
            _logger.debug('Vulkan driver is available on the system.')
            renderer = '-1'

            if gfxbackend := self.config.get('pcsx2_gfxbackend'):
                if gfxbackend == '12':
                    _logger.debug('User selected OpenGL')
                if gfxbackend == '13':
                    _logger.debug('User selected Software! Man you must have a fast CPU!')
                elif gfxbackend == '14':
                    _logger.debug('User selected Vulkan')
                    if has_discrete_gpu():
                        _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                        discrete_name = get_discrete_gpu_name()
                        if discrete_name:
                            _logger.debug('Using Discrete GPU Name: %s for PCSX2', discrete_name)
                            pcsx2_ini_config.set('EmuCore/GS', 'Adapter', discrete_name)
                        else:
                            _logger.debug("Couldn't get discrete GPU Name")
                            pcsx2_ini_config.set('EmuCore/GS', 'Adapter', '(Default)')
                    else:
                        _logger.debug('Discrete GPU is not available on the system. Using default.')
                        pcsx2_ini_config.set('EmuCore/GS', 'Adapter', '(Default)')
                renderer = gfxbackend
            else:
                _logger.debug('User selected to Automatic')

            pcsx2_ini_config.set('EmuCore/GS', 'Renderer', renderer)
        else:
            _logger.debug('Vulkan driver is not available on the system. Falling back to Automatic')
            pcsx2_ini_config.set('EmuCore/GS', 'Renderer', '-1')

        # Ratio
        pcsx2_ini_config.set('EmuCore/GS', 'AspectRatio', self.config.get('pcsx2_ratio', 'Auto 4:3/3:2'))

        # Vsync
        pcsx2_ini_config.set('EmuCore/GS', 'VsyncEnable', self.config.get('pcsx2_vsync', '0'))

        # Resolution
        pcsx2_ini_config.set('EmuCore/GS', 'upscale_multiplier', self.config.get('pcsx2_resolution', '1'))

        # FXAA
        pcsx2_ini_config.set('EmuCore/GS', 'fxaa', self.config.get('pcsx2_fxaa', 'false'))

        # FMV Ratio
        pcsx2_ini_config.set('EmuCore/GS', 'FMVAspectRatioSwitch', self.config.get('pcsx2_fmv_ratio', 'Auto 4:3/3:2'))

        # Mipmapping
        # Upstream collapsed the old 3-way "mipmap_hw" (Off/Basic/Full) setting into a plain
        # on/off "hw_mipmap" boolean (PCSX2 v2.8.x) -- the "Basic" vs "Full" distinction this
        # custom_feature's choices still expose no longer has an upstream equivalent, so any
        # non-"Off" choice just enables hardware mipmapping.
        pcsx2_ini_config.set(
            'EmuCore/GS', 'hw_mipmap', 'false' if self.config.get('pcsx2_mipmapping') == '0' else 'true'
        )

        # Trilinear Filtering
        pcsx2_ini_config.set('EmuCore/GS', 'TriFilter', self.config.get('pcsx2_trilinear_filtering', '-1'))

        # Anisotropic Filtering
        pcsx2_ini_config.set('EmuCore/GS', 'MaxAnisotropy', self.config.get('pcsx2_anisotropic_filtering', '0'))

        # Dithering
        pcsx2_ini_config.set('EmuCore/GS', 'dithering_ps2', self.config.get('pcsx2_dithering', '2'))

        # Texture Preloading
        pcsx2_ini_config.set('EmuCore/GS', 'texture_preloading', self.config.get('pcsx2_texture_loading', '2'))

        # Deinterlacing
        pcsx2_ini_config.set('EmuCore/GS', 'deinterlace_mode', self.config.get('pcsx2_deinterlacing', '0'))

        # Anti-Blur
        pcsx2_ini_config.set('EmuCore/GS', 'pcrtc_antiblur', self.config.get('pcsx2_blur', 'true'))

        # Integer Scaling
        pcsx2_ini_config.set('EmuCore/GS', 'IntegerScaling', self.config.get('pcsx2_scaling', 'false'))

        # Blending Accuracy
        pcsx2_ini_config.set('EmuCore/GS', 'accurate_blending_unit', self.config.get('pcsx2_blending', '1'))

        # Texture Filtering
        pcsx2_ini_config.set('EmuCore/GS', 'filter', self.config.get('pcsx2_texture_filtering', '2'))

        # Bilinear Filtering
        pcsx2_ini_config.set('EmuCore/GS', 'linear_present_mode', self.config.get('pcsx2_bilinear_filtering', '1'))

        # Load Texture Replacements
        pcsx2_ini_config.set(
            'EmuCore/GS', 'LoadTextureReplacements', self.config.get('pcsx2_texture_replacements', 'false')
        )

        # OSD messages
        # "OsdShowMessages" no longer exists upstream; disabling now works purely through
        # OsdMessagesPos below (None == 0 == disabled), same value this already computes.
        osd_enabled = self.config.get('pcsx2_osd_messages', 'true')

        # OSD Messages Position
        pcsx2_ini_config.set(
            'EmuCore/GS',
            'OsdMessagesPos',
            '0' if osd_enabled == 'false' else self.config.get('pcsx2_osd_messages_position', '2'),
        )

        # OSD Performance Position
        pcsx2_ini_config.set('EmuCore/GS', 'OsdPerformancePos', self.config.get('pcsx2_osd_performance_position', '0'))

        # Crop Overscan
        crop_overscan = '3' if self.config.get_bool('pcsx2_overscan') else '0'

        pcsx2_ini_config.set('EmuCore/GS', 'CropLeft', crop_overscan)
        pcsx2_ini_config.set('EmuCore/GS', 'CropTop', crop_overscan)
        pcsx2_ini_config.set('EmuCore/GS', 'CropRight', crop_overscan)
        pcsx2_ini_config.set('EmuCore/GS', 'CropBottom', crop_overscan)

        # TV Shader
        pcsx2_ini_config.set('EmuCore', 'TVShader', self.config.get('pcsx2_shaderset', '0'))

        pcsx2_ini_config.set(
            'EmuCore',
            'AutoIncrementSlot',
            self.config.get_bool('incrementalsavestates', True, return_values=('true', 'false')),
        )

        pcsx2_ini_config.set(
            'EmuCore', 'SaveStateOnShutdown', self.config.get_bool('autosave', return_values=('true', 'false'))
        )

        # VU thread speedhack
        pcsx2_ini_config.set(
            'EmuCore/Speedhacks', 'vuThread', self.config.get_bool('pcsx2_vuthread', return_values=('true', 'false'))
        )

        # EE Cycle Rate speedhack
        pcsx2_ini_config.set('EmuCore/Speedhacks', 'EECycleRate', self.config.get('pcsx2_eecyclerate', '0'))

        ## [InputSources]
        if not pcsx2_ini_config.has_section('InputSources'):
            pcsx2_ini_config.add_section('InputSources')

        pcsx2_ini_config.set('InputSources', 'Keyboard', 'true')
        pcsx2_ini_config.set('InputSources', 'Mouse', 'true')
        pcsx2_ini_config.set('InputSources', 'SDL', 'true')

        ## [Hotkeys]
        if not pcsx2_ini_config.has_section('Hotkeys'):
            pcsx2_ini_config.add_section('Hotkeys')

        pcsx2_ini_config.set('Hotkeys', 'ToggleFullscreen', 'Keyboard/Alt & Keyboard/Return')
        pcsx2_ini_config.set('Hotkeys', 'CycleAspectRatio', 'Keyboard/F6')
        pcsx2_ini_config.set('Hotkeys', 'CycleInterlaceMode', 'Keyboard/F5')
        pcsx2_ini_config.set('Hotkeys', 'CycleMipmapMode', 'Keyboard/Insert')
        pcsx2_ini_config.set('Hotkeys', 'GSDumpMultiFrame', 'Keyboard/Control & Keyboard/Shift & Keyboard/F8')
        pcsx2_ini_config.set('Hotkeys', 'Screenshot', 'Keyboard/F8')
        pcsx2_ini_config.set('Hotkeys', 'GSDumpSingleFrame', 'Keyboard/Shift & Keyboard/F8')
        pcsx2_ini_config.set('Hotkeys', 'ToggleSoftwareRendering', 'Keyboard/F9')
        pcsx2_ini_config.set('Hotkeys', 'ZoomIn', 'Keyboard/Control & Keyboard/Plus')
        pcsx2_ini_config.set('Hotkeys', 'ZoomOut', 'Keyboard/Control & Keyboard/Minus')
        pcsx2_ini_config.set('Hotkeys', 'InputRecToggleMode', 'Keyboard/Shift & Keyboard/R')
        pcsx2_ini_config.set('Hotkeys', 'LoadStateFromSlot', 'Keyboard/F3')
        pcsx2_ini_config.set('Hotkeys', 'SaveStateToSlot', 'Keyboard/F1')
        pcsx2_ini_config.set('Hotkeys', 'NextSaveStateSlot', 'Keyboard/F2')
        pcsx2_ini_config.set('Hotkeys', 'PreviousSaveStateSlot', 'Keyboard/Shift & Keyboard/F2')
        pcsx2_ini_config.set('Hotkeys', 'OpenPauseMenu', 'Keyboard/Escape')
        pcsx2_ini_config.set('Hotkeys', 'ToggleFrameLimit', 'Keyboard/F4')
        pcsx2_ini_config.set('Hotkeys', 'TogglePause', 'Keyboard/Space')
        pcsx2_ini_config.set('Hotkeys', 'ToggleSlowMotion', 'Keyboard/Shift & Keyboard/Backtab')
        pcsx2_ini_config.set('Hotkeys', 'ToggleTurbo', 'Keyboard/Tab')
        pcsx2_ini_config.set('Hotkeys', 'HoldTurbo', 'Keyboard/Period')

        # clean gun sections
        for usb in ('USB1', 'USB2'):
            if pcsx2_ini_config.has_section(usb) and pcsx2_ini_config.get(usb, 'Type', fallback=None) == 'guncon2':
                pcsx2_ini_config.remove_option(usb, 'Type')
            for opt in ('guncon2_Start', 'guncon2_C', 'guncon2_numdevice'):
                if pcsx2_ini_config.has_section(usb) and pcsx2_ini_config.has_option(usb, opt):
                    pcsx2_ini_config.remove_option(usb, opt)

        # clean wheel sections
        for usb in ('USB1', 'USB2'):
            if (
                pcsx2_ini_config.has_section(usb)
                and pcsx2_ini_config.get(usb, 'Type', fallback=None) == 'Pad'
                and pcsx2_ini_config.get(usb, 'Pad_subtype', fallback=None) == '1'
            ):
                pcsx2_ini_config.remove_option(usb, 'Type')
        ###

        controllers = self.controllers
        guns = self.guns
        metadata = self.metadata

        # guns
        if self.config.use_guns and guns:
            gun1onport2 = len(guns) == 1 and metadata.get('gun_gun1port') == '2'
            pedals_keys = {1: 'c', 2: 'v', 3: 'b', 4: 'n'}

            if guns and not gun1onport2:
                if not pcsx2_ini_config.has_section('USB1'):
                    pcsx2_ini_config.add_section('USB1')
                pcsx2_ini_config.set('USB1', 'Type', 'guncon2')
                for nc, pad in enumerate(controllers, start=1):
                    if nc == 1 and not gun1onport2 and 'start' in pad.inputs:
                        pcsx2_ini_config.set('USB1', 'guncon2_Start', f'SDL-{pad.index}/Start')

                ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
                pedalkey = self.config.get('controllers.pedals1', pedals_keys[1])
                pcsx2_ini_config.set('USB1', 'guncon2_C', f'Keyboard/{pedalkey.upper()}')
                ###
            if len(guns) >= 2 or gun1onport2:
                if not pcsx2_ini_config.has_section('USB2'):
                    pcsx2_ini_config.add_section('USB2')
                pcsx2_ini_config.set('USB2', 'Type', 'guncon2')
                for nc, pad in enumerate(controllers, start=1):
                    if (nc == 2 or gun1onport2) and 'start' in pad.inputs:
                        pcsx2_ini_config.set('USB2', 'guncon2_Start', f'SDL-{pad.index}/Start')
                ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
                pedalkey = self.config.get('controllers.pedals2', pedals_keys[2])
                pcsx2_ini_config.set('USB2', 'guncon2_C', f'Keyboard/{pedalkey.upper()}')
                ###
                if gun1onport2:
                    pcsx2_ini_config.set('USB2', 'guncon2_numdevice', '0')
        # Gun crosshairs
        if pcsx2_ini_config.has_section('USB1'):
            if self.config.get('pcsx2_crosshairs') == '1':
                pcsx2_ini_config.set(
                    'USB1', 'guncon2_cursor_path', str(_PCSX2_RESOURCES_DIR / 'crosshairs' / 'default.png')
                )
                pcsx2_ini_config.set('USB1', 'guncon2_cursor_color', '#0000ff')  # blue
            else:
                pcsx2_ini_config.set('USB1', 'guncon2_cursor_path', '')
        if pcsx2_ini_config.has_section('USB2'):
            if self.config.get('pcsx2_crosshairs') == '1':
                pcsx2_ini_config.set(
                    'USB2', 'guncon2_cursor_path', str(_PCSX2_RESOURCES_DIR / 'crosshairs' / 'default.png')
                )
                pcsx2_ini_config.set('USB2', 'guncon2_cursor_color', '#ff0000')  # red
            else:
                pcsx2_ini_config.set('USB2', 'guncon2_cursor_path', '')
        # hack for the fog bug for guns (time crisis - crisis zone)
        fog_files = (
            _PCSX2_RESOURCES_DIR
            / 'textures'
            / 'SCES-52530'
            / 'replacements'
            / 'c321d53987f3986d-eadd4df7c9d76527-00005dd4.png',
            _PCSX2_RESOURCES_DIR
            / 'textures'
            / 'SLUS-20927'
            / 'replacements'
            / 'c321d53987f3986d-eadd4df7c9d76527-00005dd4.png',
        )
        texture_dir = config_directory / 'textures'
        # copy textures if necessary to PCSX2 config folder
        if self.config.get('pcsx2_crisis_fog') == 'true':
            for file_path in fog_files:
                parent_directory_name = file_path.parent.parent.name
                file_name = file_path.name
                texture_directory_path = texture_dir / parent_directory_name / 'replacements'
                texture_directory_path.mkdir(parents=True, exist_ok=True)

                destination_file_path = texture_directory_path / file_name

                shutil.copyfile(file_path, destination_file_path)
            # set texture replacement on regardless of previous setting
            pcsx2_ini_config.set('EmuCore/GS', 'LoadTextureReplacements', 'true')
        else:
            for file_path in fog_files:
                parent_directory_name = file_path.parent.parent.name
                file_name = file_path.name
                texture_directory_path = texture_dir / parent_directory_name / 'replacements'
                target_file_path = texture_directory_path / file_name

                if target_file_path.is_file():
                    target_file_path.unlink()

        # wheels
        wtype = self._wheel_type
        _logger.info('PS2 wheel type is %s', wtype)
        if self._use_emulator_wheels and self.wheels:
            usbx = 1
            for pad in controllers:
                if pad.device_path in self.wheels:
                    section = f'USB{usbx}'
                    if not pcsx2_ini_config.has_section(section):
                        pcsx2_ini_config.add_section(section)
                    pcsx2_ini_config.set(section, 'Type', 'Pad')

                    pcsx2_ini_config.set(section, 'Pad_subtype', _WHEEL_TYPE_MAPPING[wtype])

                    if pad.physical_device_path is not None:  # ffb on the real wheel
                        pcsx2_ini_config.set(section, 'Pad_FFDevice', f'SDL-{pad.physical_index}')
                    else:
                        pcsx2_ini_config.set(section, 'Pad_FFDevice', f'SDL-{pad.index}')

                    for key, inp in pad.inputs.items():
                        if key in _WHEEL_MAPPING[wtype]:
                            pcsx2_ini_config.set(
                                section, _WHEEL_MAPPING[wtype][key], f'SDL-{pad.index}/{_input_to_wheel(inp)}'
                            )
                    # wheel
                    if 'joystick1left' in pad.inputs:
                        pcsx2_ini_config.set(
                            section,
                            'Pad_SteeringLeft',
                            f'SDL-{pad.index}/{_input_to_wheel(pad.inputs["joystick1left"])}',
                        )
                        pcsx2_ini_config.set(
                            section,
                            'Pad_SteeringRight',
                            f'SDL-{pad.index}/{_input_to_wheel(pad.inputs["joystick1left"], reversed_axis=True)}',
                        )
                    # pedals
                    if 'l2' in pad.inputs:
                        pcsx2_ini_config.set(
                            section,
                            'Pad_Brake',
                            f'SDL-{pad.index}/{_input_to_wheel(pad.inputs["l2"], reversed_axis=None)}',
                        )
                    if 'r2' in pad.inputs:
                        pcsx2_ini_config.set(
                            section,
                            'Pad_Throttle',
                            f'SDL-{pad.index}/{_input_to_wheel(pad.inputs["r2"], reversed_axis=None)}',
                        )
                    usbx += 1

        ## [Pad]
        if not pcsx2_ini_config.has_section('Pad'):
            pcsx2_ini_config.add_section('Pad')

        pcsx2_ini_config.set('Pad', 'MultitapPort1', 'false')
        pcsx2_ini_config.set('Pad', 'MultitapPort2', 'false')

        # add multitap as needed
        multi_tap = 2
        joystick_count = len(controllers)
        _logger.debug('Number of Controllers = %s', joystick_count)
        multitap_config = self.config.get('pcsx2_multitap')
        if multitap_config == '4':
            if 2 < joystick_count < 5:
                pcsx2_ini_config.set('Pad', 'MultitapPort1', 'true')
                multi_tap = 4
            elif joystick_count > 4:
                pcsx2_ini_config.set('Pad', 'MultitapPort1', 'true')
                multi_tap = 4
                _logger.debug('*** You have too many connected controllers for this option, restricting to 4 ***')
            else:
                multi_tap = 2
                _logger.debug('*** You have the wrong number of connected controllers for this option ***')
        elif multitap_config == '8':
            if joystick_count > 4:
                pcsx2_ini_config.set('Pad', 'MultitapPort1', 'true')
                pcsx2_ini_config.set('Pad', 'MultitapPort2', 'true')
                multi_tap = 8
            elif 2 < joystick_count < 5:
                pcsx2_ini_config.set('Pad', 'MultitapPort1', 'true')
                multi_tap = 4
                _logger.debug("*** You don't have enough connected controllers for this option, restricting to 4 ***")
            else:
                multi_tap = 2
                _logger.debug("*** You don't have enough connected controllers for this option ***")
        else:
            multi_tap = 2

        # remove the previous [Padx] sections to avoid phantom controllers
        for section_name in ('Pad1', 'Pad2', 'Pad3', 'Pad4', 'Pad5', 'Pad6', 'Pad7', 'Pad8'):
            if pcsx2_ini_config.has_section(section_name):
                pcsx2_ini_config.remove_section(section_name)

        # Now add Controllers
        for nplayer, pad in enumerate(controllers, start=1):
            if pad.guid in _VALID_SONY_GUIDS:
                pcsx2_ini_config.set('InputSources', 'SDLControllerEnhancedMode', 'true')
            else:
                pcsx2_ini_config.set('InputSources', 'SDLControllerEnhancedMode', 'false')

            # only configure the number of controllers set
            if nplayer <= multi_tap:
                pad_index = nplayer
                if multi_tap == 4 and pad.index != 0:
                    # Skip Pad2 in the ini file when MultitapPort1 only
                    pad_index = nplayer + 1
                pad_num = f'Pad{pad_index}'
                sdl_num = f'SDL-{pad.index}'

                if not pcsx2_ini_config.has_section(pad_num):
                    pcsx2_ini_config.add_section(pad_num)

                pcsx2_ini_config.set(pad_num, 'Type', 'DualShock2')
                pcsx2_ini_config.set(pad_num, 'InvertL', '0')
                pcsx2_ini_config.set(pad_num, 'InvertR', '0')
                pcsx2_ini_config.set(pad_num, 'Deadzone', '0')
                pcsx2_ini_config.set(pad_num, 'AxisScale', '1.33')
                pcsx2_ini_config.set(pad_num, 'TriggerDeadzone', '0')
                pcsx2_ini_config.set(pad_num, 'TriggerScale', '1')
                pcsx2_ini_config.set(pad_num, 'LargeMotorScale', '1')
                pcsx2_ini_config.set(pad_num, 'SmallMotorScale', '1')
                pcsx2_ini_config.set(pad_num, 'ButtonDeadzone', '0')
                pcsx2_ini_config.set(pad_num, 'PressureModifier', '0.5')
                pcsx2_ini_config.set(pad_num, 'Up', sdl_num + '/DPadUp')
                pcsx2_ini_config.set(pad_num, 'Right', sdl_num + '/DPadRight')
                pcsx2_ini_config.set(pad_num, 'Down', sdl_num + '/DPadDown')
                pcsx2_ini_config.set(pad_num, 'Left', sdl_num + '/DPadLeft')
                pcsx2_ini_config.set(pad_num, 'Triangle', sdl_num + '/FaceNorth')
                pcsx2_ini_config.set(pad_num, 'Circle', sdl_num + '/FaceEast')
                pcsx2_ini_config.set(pad_num, 'Cross', sdl_num + '/FaceSouth')
                pcsx2_ini_config.set(pad_num, 'Square', sdl_num + '/FaceWest')
                pcsx2_ini_config.set(pad_num, 'Select', sdl_num + '/Back')
                pcsx2_ini_config.set(pad_num, 'Start', sdl_num + '/Start')
                pcsx2_ini_config.set(pad_num, 'L1', sdl_num + '/LeftShoulder')
                pcsx2_ini_config.set(pad_num, 'L2', sdl_num + '/+LeftTrigger')
                pcsx2_ini_config.set(pad_num, 'R1', sdl_num + '/RightShoulder')
                pcsx2_ini_config.set(pad_num, 'R2', sdl_num + '/+RightTrigger')
                pcsx2_ini_config.set(pad_num, 'L3', sdl_num + '/LeftStick')
                pcsx2_ini_config.set(pad_num, 'R3', sdl_num + '/RightStick')
                pcsx2_ini_config.set(pad_num, 'LUp', sdl_num + '/-LeftY')
                pcsx2_ini_config.set(pad_num, 'LRight', sdl_num + '/+LeftX')
                pcsx2_ini_config.set(pad_num, 'LDown', sdl_num + '/+LeftY')
                pcsx2_ini_config.set(pad_num, 'LLeft', sdl_num + '/-LeftX')
                pcsx2_ini_config.set(pad_num, 'RUp', sdl_num + '/-RightY')
                pcsx2_ini_config.set(pad_num, 'RRight', sdl_num + '/+RightX')
                pcsx2_ini_config.set(pad_num, 'RDown', sdl_num + '/+RightY')
                pcsx2_ini_config.set(pad_num, 'RLeft', sdl_num + '/-RightX')
                pcsx2_ini_config.set(pad_num, 'Analog', sdl_num + '/Guide')
                pcsx2_ini_config.set(pad_num, 'LargeMotor', sdl_num + '/LargeMotor')
                pcsx2_ini_config.set(pad_num, 'SmallMotor', sdl_num + '/SmallMotor')

        ## [GameList]
        if not pcsx2_ini_config.has_section('GameList'):
            pcsx2_ini_config.add_section('GameList')

        pcsx2_ini_config.set('GameList', 'RecursivePaths', str(self.roms_dir))

        with config_file_name.open('w') as configfile:
            pcsx2_ini_config.write(configfile)
