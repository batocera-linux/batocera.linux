from __future__ import annotations

import logging
import re
import shutil
import time
from pathlib import Path
from typing import Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CACHE, CONFIGS, ROMS
from batocera_common.vulkan import get_discrete_gpu_name, has_discrete_gpu, is_available
from batocera_launch import Command, Controllers, Emulator, HotkeysContext, SystemConfig
from batocera_launch.paths import DATAINIT_DIR, configure_emulator

_logger = logging.getLogger(__name__)

_PCSX2X6_BIN_DIR: Final = Path('/usr/pcsx2x6/bin')
_PCSX2X6_RESOURCES_DIR: Final = _PCSX2X6_BIN_DIR / 'resources'
_PCSX2X6_BIOS: Final = BIOS / 'namco2x6'


def _gfx_ratio_from_config(config: SystemConfig) -> str:
    # 2: 4:3 ; 1: 16:9
    ratio = config.get('pcsx2x6_ratio')
    if ratio == '16:9':
        return '16:9'
    if ratio == 'full':
        return 'Stretch'
    return '4:3'


@cached_dataclass
class Pcsx2x6(Emulator):
    needs_sdl_controller_db = True
    needs_sdl_game_controller_config = True

    @cached_property
    def config_dir(self) -> Path:
        # kept as the historical mixed-case name for on-disk config compatibility;
        # self.name would give the lowercase package name ("pcsx2x6") instead.
        return CONFIGS / 'PCSX2x6'

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.config_dir / 'game_controller_db.txt'

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'pcsx2x6',
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
    def in_game_ratio(self) -> float:
        config_ratio = _gfx_ratio_from_config(self.config)
        if config_ratio == '16:9' or (
            config_ratio == 'Stretch' and self.resolution.width / float(self.resolution.height) > ((16.0 / 9.0) - 0.1)
        ):
            return 16 / 9
        return 4 / 3

    async def configure(self) -> Command:
        pcsx2_patches = _PCSX2X6_BIOS / 'patches.zip'

        # Remove older config files if present
        inis_dir = self.config_dir / 'inis'
        for filename in ('PCSX2_ui.ini', 'PCSX2_vm.ini', 'GS.ini'):
            (inis_dir / filename).unlink(missing_ok=True)

        # Config files
        _configure_reg(self.config_dir)
        _configure_ini(self.config_dir, self.config, self.rom, self.controllers)
        _configure_audio(self.config_dir)

        command_array: list[str | Path] = (
            ['/usr/pcsx2x6/bin/pcsx2x6-qt']
            if configure_emulator(self.rom)
            else ['/usr/pcsx2x6/bin/pcsx2x6-qt', '-nogui', self.rom]
        )

        with Path('/proc/cpuinfo').open() as cpuinfo:
            if not re.search(r'^flags\s*:.*\ssse4_1\W', cpuinfo.read(), re.MULTILINE):
                _logger.warning(
                    'CPU does not support SSE4.1 which is required by pcsx2x6. '
                    'The emulator will likely crash with SIGILL (illegal instruction).'
                )

        # ensure we have the patches.zip file to avoid message.
        pcsx2_patches.parent.mkdir(parents=True, exist_ok=True)
        if not pcsx2_patches.exists():
            shutil.copy(DATAINIT_DIR / 'bios' / 'namco2x6' / 'patches.zip', pcsx2_patches)

        # state_slot option
        if state_filename := self.config.get('state_filename'):
            command_array.extend(['-statefile', state_filename])

        if state_slot := self.config.get_str('state_slot'):
            command_array.extend(['-stateindex', state_slot])

        return Command(
            command_array,
            env={'XDG_CONFIG_HOME': CONFIGS},
        )


def _configure_reg(config_directory: Path) -> None:
    config_directory.mkdir(parents=True, exist_ok=True)
    with (config_directory / 'PCSX2-reg.ini').open('w') as f:
        f.write('DocumentsFolderMode=User\n')
        f.write(f'CustomDocumentsFolder={_PCSX2X6_BIN_DIR}\n')
        f.write('UseDefaultSettingsFolder=enabled\n')
        f.write(f'SettingsFolder={config_directory / "inis"}\n')
        f.write(f'Install_Dir={_PCSX2X6_BIN_DIR}\n')
        f.write('RunWizard=0\n')


def _configure_audio(config_directory: Path) -> None:
    config_file_name = config_directory / 'inis' / 'spu2-x.ini'
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


def _configure_ini(
    config_directory: Path,
    config: SystemConfig,
    rom: Path,
    controllers: Controllers,
) -> None:
    config_file_name = config_directory / 'inis' / 'PCSX2.ini'

    config_file_name.parent.mkdir(parents=True, exist_ok=True)

    if not config_file_name.is_file():
        with config_file_name.open('w') as f:
            f.write('[UI]\n')

    pcsx2x6_ini_config = CaseSensitiveConfigParser(interpolation=None)

    if config_file_name.is_file():
        pcsx2x6_ini_config.read(config_file_name)

    ## [UI]
    if not pcsx2x6_ini_config.has_section('UI'):
        pcsx2x6_ini_config.add_section('UI')

    # set the settings we want always enabled
    pcsx2x6_ini_config.set('UI', 'SettingsVersion', '1')
    pcsx2x6_ini_config.set('UI', 'InhibitScreensaver', 'true')
    pcsx2x6_ini_config.set('UI', 'ConfirmShutdown', 'false')
    pcsx2x6_ini_config.set('UI', 'StartPaused', 'false')
    pcsx2x6_ini_config.set('UI', 'PauseOnFocusLoss', 'false')
    pcsx2x6_ini_config.set('UI', 'StartFullscreen', 'true')
    pcsx2x6_ini_config.set('UI', 'HideMouseCursor', 'true')
    pcsx2x6_ini_config.set('UI', 'RenderToSeparateWindow', 'false')
    pcsx2x6_ini_config.set('UI', 'HideMainWindowWhenRunning', 'true')
    pcsx2x6_ini_config.set('UI', 'DoubleClickTogglesFullscreen', 'false')

    # clear to not have the window anywhere when switching from multi to single screen and vice and versa
    for opt in ('MainWindowGeometry', 'MainWindowState', 'DisplayWindowGeometry'):
        if pcsx2x6_ini_config.has_section('UI') and pcsx2x6_ini_config.has_option('UI', opt):
            pcsx2x6_ini_config.remove_option('UI', opt)

    ## [Folders]
    if not pcsx2x6_ini_config.has_section('Folders'):
        pcsx2x6_ini_config.add_section('Folders')

    # remove inconsistent SaveStates casing if it exists
    pcsx2x6_ini_config.remove_option('Folders', 'SaveStates')

    # set the folders we want
    pcsx2x6_ini_config.set('Folders', 'Bios', '../../../bios/namco2x6')
    pcsx2x6_ini_config.set('Folders', 'Snapshots', '../../../screenshots')
    pcsx2x6_ini_config.set('Folders', 'Savestates', '../../../saves/namco2x6/pcsx2x6/sstates')
    pcsx2x6_ini_config.set('Folders', 'MemoryCards', '../../../saves/namco2x6/pcsx2x6')
    pcsx2x6_ini_config.set('Folders', 'Logs', '../../logs')
    pcsx2x6_ini_config.set('Folders', 'Cheats', '../../../cheats/namco2x6')
    pcsx2x6_ini_config.set('Folders', 'CheatsWS', '../../../cheats/namco2x6/cheats_ws')
    pcsx2x6_ini_config.set('Folders', 'CheatsNI', '../../../cheats/namco2x6/cheats_ni')
    pcsx2x6_ini_config.set('Folders', 'Cache', '../../cache/namco2x6')
    pcsx2x6_ini_config.set('Folders', 'Textures', 'textures')
    pcsx2x6_ini_config.set('Folders', 'InputProfiles', 'inputprofiles')
    pcsx2x6_ini_config.set('Folders', 'Videos', '../../../saves/namco2x6/pcsx2x6/videos')

    # create cache folder
    (CACHE / 'namco2x6').mkdir(parents=True, exist_ok=True)

    ## [EmuCore]
    if not pcsx2x6_ini_config.has_section('EmuCore'):
        pcsx2x6_ini_config.add_section('EmuCore')

    # set the settings we want always enabled
    pcsx2x6_ini_config.set('EmuCore', 'EnableDiscordPresence', 'false')

    # Cheats
    # pcsx2x6_ini_config.set('EmuCore', 'EnableCheats', config.get('pcsx2x6_cheats', 'false'))

    # Widescreen Patches
    # pcsx2x6_ini_config.set('EmuCore', 'EnableWideScreenPatches', config.get('pcsx2x6_EnableWideScreenPatches', 'false'))

    # No-interlacing Patches
    # pcsx2x6_ini_config.set('EmuCore', 'EnableNoInterlacingPatches', config.get('pcsx2x6_interlacing_patches', 'false'))

    ## [Achievements]
    if not pcsx2x6_ini_config.has_section('Achievements'):
        pcsx2x6_ini_config.add_section('Achievements')
    pcsx2x6_ini_config.set('Achievements', 'Enabled', 'false')
    if config.get_bool('retroachievements'):
        username = config.get('retroachievements.username', '')
        token = config.get('retroachievements.token', '')
        pcsx2x6_ini_config.set('Achievements', 'Enabled', 'true')
        pcsx2x6_ini_config.set('Achievements', 'Username', username)
        pcsx2x6_ini_config.set('Achievements', 'Token', token)
        pcsx2x6_ini_config.set('Achievements', 'LoginTimestamp', str(int(time.time())))
        pcsx2x6_ini_config.set(
            'Achievements',
            'ChallengeMode',
            config.get_bool('retroachievements.hardcore', return_values=('true', 'false')),
        )
        pcsx2x6_ini_config.set(
            'Achievements',
            'PrimedIndicators',
            config.get_bool('retroachievements.challenge_indicators', return_values=('true', 'false')),
        )
        pcsx2x6_ini_config.set(
            'Achievements',
            'RichPresence',
            config.get_bool('retroachievements.richpresence', return_values=('true', 'false')),
        )
        pcsx2x6_ini_config.set(
            'Achievements',
            'Leaderboards',
            config.get_bool('retroachievements.leaderboards', return_values=('true', 'false')),
        )
        pcsx2x6_ini_config.set(
            'Achievements', 'EncoreMode', config.get_bool('retroachievements.encore', return_values=('true', 'false'))
        )
        pcsx2x6_ini_config.set(
            'Achievements',
            'UnofficialTestMode',
            config.get_bool('retroachievements.unofficial', return_values=('true', 'false')),
        )
    # set other settings
    pcsx2x6_ini_config.set('Achievements', 'TestMode', 'false')
    pcsx2x6_ini_config.set('Achievements', 'UnofficialTestMode', 'false')
    pcsx2x6_ini_config.set('Achievements', 'Notifications', 'true')
    pcsx2x6_ini_config.set('Achievements', 'SoundEffects', 'true')

    ## [Filenames]
    if not pcsx2x6_ini_config.has_section('Filenames'):
        pcsx2x6_ini_config.add_section('Filenames')

    # Read rom metadata/info file to find the platform value
    platform = '256'
    if rom.is_file():
        try:
            with rom.open('r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned.startswith('platform'):
                        parts = [p.strip() for p in cleaned.split('=', 1)]
                        if len(parts) == 2 and parts[0] == 'platform':
                            platform = parts[1]
                            break
        except Exception as e:
            _logger.warning('Could not read platform from ROM file %s: %s', rom, e)

    # Use r27v1602f.7d for 246 platform, default to r27v1602f.8g (for 256 or others)
    bios_file = 'r27v1602f.7d' if platform == '246' else 'r27v1602f.8g'
    pcsx2x6_ini_config.set('Filenames', 'BIOS', bios_file)

    ## [EMUCORE/GS]
    if not pcsx2x6_ini_config.has_section('EmuCore/GS'):
        pcsx2x6_ini_config.add_section('EmuCore/GS')

    ## [EMUCORE/Speedhacks]
    if not pcsx2x6_ini_config.has_section('EmuCore/Speedhacks'):
        pcsx2x6_ini_config.add_section('EmuCore/Speedhacks')

    # Renderer
    # Check Vulkan first to be sure
    if is_available():
        _logger.debug('Vulkan driver is available on the system.')
        renderer = '-1'

        if gfxbackend := config.get('pcsx2x6_gfxbackend'):
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
                        _logger.debug('Using Discrete GPU Name: %s for PCSX2x6', discrete_name)
                        pcsx2x6_ini_config.set('EmuCore/GS', 'Adapter', discrete_name)
                    else:
                        _logger.debug("Couldn't get discrete GPU Name")
                        pcsx2x6_ini_config.set('EmuCore/GS', 'Adapter', '(Default)')
                else:
                    _logger.debug('Discrete GPU is not available on the system. Using default.')
                    pcsx2x6_ini_config.set('EmuCore/GS', 'Adapter', '(Default)')
            renderer = gfxbackend
        else:
            _logger.debug('User selected to Automatic')

        pcsx2x6_ini_config.set('EmuCore/GS', 'Renderer', renderer)
    else:
        _logger.debug('Vulkan driver is not available on the system. Falling back to Automatic')
        pcsx2x6_ini_config.set('EmuCore/GS', 'Renderer', '-1')

    # Ratio
    pcsx2x6_ini_config.set('EmuCore/GS', 'AspectRatio', config.get('pcsx2x6_ratio', 'Auto 4:3/3:2'))

    # Vsync
    pcsx2x6_ini_config.set('EmuCore/GS', 'VsyncEnable', config.get('pcsx2x6_vsync', '0'))

    # Resolution
    pcsx2x6_ini_config.set('EmuCore/GS', 'upscale_multiplier', config.get('pcsx2x6_resolution', '1'))

    # FXAA
    pcsx2x6_ini_config.set('EmuCore/GS', 'fxaa', config.get('pcsx2x6_fxaa', 'false'))

    # FMV Ratio
    pcsx2x6_ini_config.set('EmuCore/GS', 'FMVAspectRatioSwitch', config.get('pcsx2x6_fmv_ratio', 'Auto 4:3/3:2'))

    # Mipmapping
    # Upstream split the old tri-state "mipmap_hw" int setting (Off/Basic/Full) into two
    # independent bools: "hw_mipmap" (hardware-renderer mip generation) and "mipmap" (use the
    # PS2's own real mip data, mainly relevant to the software renderer). Preserve the original
    # 3-way intent across both keys: Off -> both false, Basic -> hw generated only,
    # Full -> both (use real PS2 data, still enabling hw mip generation as a fallback).
    mipmapping = config.get('pcsx2x6_mipmapping', '0')
    pcsx2x6_ini_config.set('EmuCore/GS', 'hw_mipmap', 'false' if mipmapping == '0' else 'true')
    pcsx2x6_ini_config.set('EmuCore/GS', 'mipmap', 'true' if mipmapping == '2' else 'false')

    # Trilinear Filtering
    pcsx2x6_ini_config.set('EmuCore/GS', 'TriFilter', config.get('pcsx2x6_trilinear_filtering', '-1'))

    # Anisotropic Filtering
    pcsx2x6_ini_config.set('EmuCore/GS', 'MaxAnisotropy', config.get('pcsx2x6_anisotropic_filtering', '0'))

    # Dithering
    pcsx2x6_ini_config.set('EmuCore/GS', 'dithering_ps2', config.get('pcsx2x6_dithering', '2'))

    # Texture Preloading
    pcsx2x6_ini_config.set('EmuCore/GS', 'texture_preloading', config.get('pcsx2x6_texture_loading', '2'))

    # Deinterlacing
    pcsx2x6_ini_config.set('EmuCore/GS', 'deinterlace_mode', config.get('pcsx2x6_deinterlacing', '0'))

    # Anti-Blur
    pcsx2x6_ini_config.set('EmuCore/GS', 'pcrtc_antiblur', config.get('pcsx2x6_blur', 'true'))

    # Integer Scaling
    pcsx2x6_ini_config.set('EmuCore/GS', 'IntegerScaling', config.get('pcsx2x6_scaling', 'false'))

    # Blending Accuracy
    pcsx2x6_ini_config.set('EmuCore/GS', 'accurate_blending_unit', config.get('pcsx2x6_blending', '1'))

    # Texture Filtering
    pcsx2x6_ini_config.set('EmuCore/GS', 'filter', config.get('pcsx2x6_texture_filtering', '2'))

    # Bilinear Filtering
    pcsx2x6_ini_config.set('EmuCore/GS', 'linear_present_mode', config.get('pcsx2x6_bilinear_filtering', '1'))

    # Load Texture Replacements
    # pcsx2x6_ini_config.set('EmuCore/GS', 'LoadTextureReplacements', config.get('pcsx2x6_texture_replacements', 'false'))

    # OSD messages
    osd_enabled = config.get('pcsx2x6_osd_messages', 'true')

    # OSD Messages Position
    pcsx2x6_ini_config.set(
        'EmuCore/GS',
        'OsdMessagesPos',
        '0' if osd_enabled == 'false' else config.get('pcsx2x6_osd_messages_position', '2'),
    )

    # OSD Performance Position
    pcsx2x6_ini_config.set('EmuCore/GS', 'OsdPerformancePos', config.get('pcsx2x6_osd_performance_position', '0'))

    # Crop Overscan
    crop_overscan = '3' if config.get_bool('pcsx2x6_crop_overscan') else '0'

    pcsx2x6_ini_config.set('EmuCore/GS', 'CropLeft', crop_overscan)
    pcsx2x6_ini_config.set('EmuCore/GS', 'CropTop', crop_overscan)
    pcsx2x6_ini_config.set('EmuCore/GS', 'CropRight', crop_overscan)
    pcsx2x6_ini_config.set('EmuCore/GS', 'CropBottom', crop_overscan)

    # TV Shader
    pcsx2x6_ini_config.set('EmuCore', 'TVShader', config.get('pcsx2x6_shaderset', '0'))

    pcsx2x6_ini_config.set(
        'EmuCore', 'AutoIncrementSlot', config.get_bool('incrementalsavestates', True, return_values=('true', 'false'))
    )

    pcsx2x6_ini_config.set(
        'EmuCore', 'SaveStateOnShutdown', config.get_bool('autosave', return_values=('true', 'false'))
    )

    # VU thread speedhack
    pcsx2x6_ini_config.set(
        'EmuCore/Speedhacks', 'vuThread', config.get_bool('pcsx2x6_vuthread', return_values=('true', 'false'))
    )

    # EE Cycle Rate speedhack
    pcsx2x6_ini_config.set('EmuCore/Speedhacks', 'EECycleRate', config.get('pcsx2x6_eecyclerate', '0'))

    ## [InputSources]
    if not pcsx2x6_ini_config.has_section('InputSources'):
        pcsx2x6_ini_config.add_section('InputSources')

    pcsx2x6_ini_config.set('InputSources', 'Keyboard', 'true')
    pcsx2x6_ini_config.set('InputSources', 'Mouse', 'true')
    pcsx2x6_ini_config.set('InputSources', 'SDL', 'true')

    ## [Hotkeys]
    if not pcsx2x6_ini_config.has_section('Hotkeys'):
        pcsx2x6_ini_config.add_section('Hotkeys')

    pcsx2x6_ini_config.set('Hotkeys', 'ToggleFullscreen', 'Keyboard/Alt & Keyboard/Return')
    pcsx2x6_ini_config.set('Hotkeys', 'CycleAspectRatio', 'Keyboard/F6')
    pcsx2x6_ini_config.set('Hotkeys', 'CycleInterlaceMode', 'Keyboard/F5')
    pcsx2x6_ini_config.set('Hotkeys', 'CycleMipmapMode', 'Keyboard/Insert')
    pcsx2x6_ini_config.set('Hotkeys', 'GSDumpMultiFrame', 'Keyboard/Control & Keyboard/Shift & Keyboard/F8')
    pcsx2x6_ini_config.set('Hotkeys', 'Screenshot', 'Keyboard/F8')
    pcsx2x6_ini_config.set('Hotkeys', 'GSDumpSingleFrame', 'Keyboard/Shift & Keyboard/F8')
    pcsx2x6_ini_config.set('Hotkeys', 'ToggleSoftwareRendering', 'Keyboard/F9')
    pcsx2x6_ini_config.set('Hotkeys', 'ZoomIn', 'Keyboard/Control & Keyboard/Plus')
    pcsx2x6_ini_config.set('Hotkeys', 'ZoomOut', 'Keyboard/Control & Keyboard/Minus')
    pcsx2x6_ini_config.set('Hotkeys', 'InputRecToggleMode', 'Keyboard/Shift & Keyboard/R')
    pcsx2x6_ini_config.set('Hotkeys', 'LoadStateFromSlot', 'Keyboard/F3')
    pcsx2x6_ini_config.set('Hotkeys', 'SaveStateToSlot', 'Keyboard/F1')
    pcsx2x6_ini_config.set('Hotkeys', 'NextSaveStateSlot', 'Keyboard/F2')
    pcsx2x6_ini_config.set('Hotkeys', 'PreviousSaveStateSlot', 'Keyboard/Shift & Keyboard/F2')
    pcsx2x6_ini_config.set('Hotkeys', 'OpenPauseMenu', 'Keyboard/Escape')
    pcsx2x6_ini_config.set('Hotkeys', 'ToggleFrameLimit', 'Keyboard/F4')
    pcsx2x6_ini_config.set('Hotkeys', 'TogglePause', 'Keyboard/Space')
    pcsx2x6_ini_config.set('Hotkeys', 'ToggleSlowMotion', 'Keyboard/Shift & Keyboard/Backtab')
    pcsx2x6_ini_config.set('Hotkeys', 'ToggleTurbo', 'Keyboard/Tab')
    pcsx2x6_ini_config.set('Hotkeys', 'HoldTurbo', 'Keyboard/Period')

    # Clear old USB sections to prevent lingering device configuration values
    for usb_section in ('USB1', 'USB2'):
        if pcsx2x6_ini_config.has_section(usb_section):
            pcsx2x6_ini_config.remove_section(usb_section)

    ## [Pad]
    if not pcsx2x6_ini_config.has_section('Pad'):
        pcsx2x6_ini_config.add_section('Pad')

    pcsx2x6_ini_config.set('Pad', 'MultitapPort1', 'false')
    pcsx2x6_ini_config.set('Pad', 'MultitapPort2', 'false')

    # remove the previous [Padx] sections to avoid phantom controllers
    for section_name in ('Pad1', 'Pad2', 'Pad3', 'Pad4', 'Pad5', 'Pad6', 'Pad7', 'Pad8'):
        if pcsx2x6_ini_config.has_section(section_name):
            pcsx2x6_ini_config.remove_section(section_name)

    # Extract Player 1 and Player 2 controller objects safely
    pad1 = controllers[0] if len(controllers) > 0 else None
    pad2 = controllers[1] if len(controllers) > 1 else None

    p1_sdl = f'SDL-{pad1.index}' if pad1 is not None else 'SDL-0'
    p2_sdl = f'SDL-{pad2.index}' if pad2 is not None else 'SDL-1'

    pcsx2x6_ini_config.set('InputSources', 'SDLControllerEnhancedMode', 'false')

    ## [JVS]
    if not pcsx2x6_ini_config.has_section('JVS'):
        pcsx2x6_ini_config.add_section('JVS')

    jvs_mappings = {
        'TestMode': 'false',
        'VideoVoltage': 'true',
        'MonitorSyncFrequency': 'true',
        'VideoSyncSplit': 'true',
        'SindenBorderEnabled': 'false',
        'SindenBorderMode': '0',
        'SindenBorderThickness': '10',
        # Player 1 controls
        'P1_Up': f'{p1_sdl}/DPadUp',
        'P1_Down': f'{p1_sdl}/DPadDown',
        'P1_Left': f'{p1_sdl}/DPadLeft',
        'P1_Right': f'{p1_sdl}/DPadRight',
        'Tekken_LeftPunch_P1': f'{p1_sdl}/FaceWest',
        'Tekken_RightPunch_P1': f'{p1_sdl}/FaceNorth',
        'Tekken_LeftKick_P1': f'{p1_sdl}/FaceSouth',
        'Tekken_RightKick_P1': f'{p1_sdl}/FaceEast',
        'SoulCal_Horizontal_P1': f'{p1_sdl}/FaceWest',
        'SoulCal_Vertical_P1': f'{p1_sdl}/FaceNorth',
        'SoulCal_Kick_P1': f'{p1_sdl}/FaceEast',
        'SoulCal_Guard_P1': f'{p1_sdl}/FaceSouth',
        'Gundam_Shoot_P1': f'{p1_sdl}/FaceWest',
        'Gundam_Melee_P1': f'{p1_sdl}/FaceNorth',
        'Gundam_Jump_P1': f'{p1_sdl}/FaceSouth',
        'Gundam_Target_P1': f'{p1_sdl}/FaceEast',
        'BloodyRoar_Punch_P1': f'{p1_sdl}/FaceWest',
        'BloodyRoar_Kick_P1': f'{p1_sdl}/FaceSouth',
        'BloodyRoar_Beast_P1': f'{p1_sdl}/FaceEast',
        'BloodyRoar_Block_P1': f'{p1_sdl}/FaceNorth',
        'Fate_Weak_P1': f'{p1_sdl}/FaceWest',
        'Fate_Medium_P1': f'{p1_sdl}/FaceNorth',
        'Fate_Strong_P1': f'{p1_sdl}/FaceEast',
        'Fate_Guard_P1': f'{p1_sdl}/FaceSouth',
        'Kinnikuman_Attack_P1': f'{p1_sdl}/FaceWest',
        'Kinnikuman_ThrowGrab_P1': f'{p1_sdl}/FaceNorth',
        'Kinnikuman_Special_P1': f'{p1_sdl}/FaceEast',
        'Kinnikuman_Guard_P1': f'{p1_sdl}/FaceSouth',
        'PrideGP_LeftPunch_P1': f'{p1_sdl}/FaceWest',
        'PrideGP_RightPunch_P1': f'{p1_sdl}/FaceNorth',
        'PrideGP_LeftKick_P1': f'{p1_sdl}/FaceSouth',
        'PrideGP_RightKick_P1': f'{p1_sdl}/FaceEast',
        'Basara_Weak_P1': f'{p1_sdl}/FaceWest',
        'Basara_Medium_P1': f'{p1_sdl}/FaceNorth',
        'Basara_Strong_P1': f'{p1_sdl}/FaceEast',
        'Basara_Striker_P1': f'{p1_sdl}/FaceSouth',
        'DragonBallZ_Light_P1': f'{p1_sdl}/FaceWest',
        'DragonBallZ_Heavy_P1': f'{p1_sdl}/FaceNorth',
        'DragonBallZ_Guard_P1': f'{p1_sdl}/FaceSouth',
        'DragonBallZ_Jump_P1': f'{p1_sdl}/FaceEast',
        'YuYu_Punch_P1': f'{p1_sdl}/FaceWest',
        'YuYu_Kick_P1': f'{p1_sdl}/FaceNorth',
        'YuYu_Guard_P1': f'{p1_sdl}/FaceSouth',
        'SixButton_LightPunch_P1': f'{p1_sdl}/FaceWest',
        'SixButton_MediumPunch_P1': f'{p1_sdl}/FaceNorth',
        'SixButton_HeavyPunch_P1': f'{p1_sdl}/LeftShoulder',
        'SixButton_LightKick_P1': f'{p1_sdl}/FaceSouth',
        'SixButton_MediumKick_P1': f'{p1_sdl}/FaceEast',
        'SixButton_HeavyKick_P1': f'{p1_sdl}/RightShoulder',
        'SteerLeft': f'{p1_sdl}/-LeftX',
        'SteerRight': f'{p1_sdl}/+LeftX',
        'Gas': f'{p1_sdl}/+RightTrigger',
        'Brake': f'{p1_sdl}/+LeftTrigger',
        'Racing_ShiftUp_P1': f'{p1_sdl}/RightShoulder',
        'Racing_ShiftDown_P1': f'{p1_sdl}/LeftShoulder',
        'Racing_View_P1': f'{p1_sdl}/FaceNorth',
        'BG3_ShiftUp_P1': f'{p1_sdl}/RightShoulder',
        'BG3_ShiftDown_P1': f'{p1_sdl}/LeftShoulder',
        'BG3_View_P1': f'{p1_sdl}/FaceNorth',
        'BG3_Sidebrake_P1': f'{p1_sdl}/FaceWest',
        'BG3_Hazard_P1': f'{p1_sdl}/FaceEast',
        'P1_DonLeft': f'{p1_sdl}/FaceWest',
        'P1_DonRight': f'{p1_sdl}/FaceNorth',
        'P1_KaLeft': f'{p1_sdl}/FaceSouth',
        'P1_KaRight': f'{p1_sdl}/FaceEast',
        'P1_LLeverUp': f'{p1_sdl}/-LeftY',
        'P1_LLeverDown': f'{p1_sdl}/+LeftY',
        'P1_LLeverLeft': f'{p1_sdl}/-LeftX',
        'P1_LLeverRight': f'{p1_sdl}/+LeftX',
        'P1_RLeverUp': f'{p1_sdl}/-RightY',
        'P1_RLeverDown': f'{p1_sdl}/+RightY',
        'P1_RLeverLeft': f'{p1_sdl}/-RightX',
        'P1_RLeverRight': f'{p1_sdl}/+RightX',
        'P1_LTrigger': f'{p1_sdl}/+LeftTrigger',
        'P1_RTrigger': f'{p1_sdl}/+RightTrigger',
        'P1_LButton': f'{p1_sdl}/LeftShoulder',
        'P1_RButton': f'{p1_sdl}/RightShoulder',
        'Smash_TopSpin_P1': f'{p1_sdl}/FaceSouth',
        'Smash_Slice_P1': f'{p1_sdl}/FaceWest',
        'Technic_Activate_P1': f'{p1_sdl}/FaceWest',
        'Technic_Action_P1': f'{p1_sdl}/FaceSouth',
        'Technic_Super_P1': f'{p1_sdl}/FaceEast',
        'Baseball_A_P1': f'{p1_sdl}/FaceSouth',
        'Baseball_B_P1': f'{p1_sdl}/FaceWest',
        'Baseball_C_P1': f'{p1_sdl}/FaceNorth',
        'GundamQuiz_Target_P1': f'{p1_sdl}/FaceEast',
        'GundamQuiz_Shoot_P1': f'{p1_sdl}/FaceWest',
        'GundamQuiz_Melee_P1': f'{p1_sdl}/FaceNorth',
        'GundamQuiz_Jump_P1': f'{p1_sdl}/FaceSouth',
        'Inufuku_1_P1': f'{p1_sdl}/FaceNorth',
        'Inufuku_2_P1': f'{p1_sdl}/FaceSouth',
        'Inufuku_3_P1': f'{p1_sdl}/FaceWest',
        'Inufuku_4_P1': f'{p1_sdl}/FaceEast',
        # Player 2 controls
        'P2_Up': f'{p2_sdl}/DPadUp',
        'P2_Down': f'{p2_sdl}/DPadDown',
        'P2_Left': f'{p2_sdl}/DPadLeft',
        'P2_Right': f'{p2_sdl}/DPadRight',
        'Tekken_LeftPunch_P2': f'{p2_sdl}/FaceWest',
        'Tekken_RightPunch_P2': f'{p2_sdl}/FaceNorth',
        'Tekken_LeftKick_P2': f'{p2_sdl}/FaceSouth',
        'Tekken_RightKick_P2': f'{p2_sdl}/FaceEast',
        'SoulCal_Horizontal_P2': f'{p2_sdl}/FaceWest',
        'SoulCal_Vertical_P2': f'{p2_sdl}/FaceNorth',
        'SoulCal_Kick_P2': f'{p2_sdl}/FaceEast',
        'SoulCal_Guard_P2': f'{p2_sdl}/FaceSouth',
        'BloodyRoar_Punch_P2': f'{p2_sdl}/FaceWest',
        'BloodyRoar_Kick_P2': f'{p2_sdl}/FaceSouth',
        'BloodyRoar_Beast_P2': f'{p2_sdl}/FaceEast',
        'BloodyRoar_Block_P2': f'{p2_sdl}/FaceNorth',
        'Fate_Weak_P2': f'{p2_sdl}/FaceWest',
        'Fate_Medium_P2': f'{p2_sdl}/FaceNorth',
        'Fate_Strong_P2': f'{p2_sdl}/FaceEast',
        'Fate_Guard_P2': f'{p2_sdl}/FaceSouth',
        'Kinnikuman_Attack_P2': f'{p2_sdl}/FaceWest',
        'Kinnikuman_ThrowGrab_P2': f'{p2_sdl}/FaceNorth',
        'Kinnikuman_Special_P2': f'{p2_sdl}/FaceEast',
        'Kinnikuman_Guard_P2': f'{p2_sdl}/FaceSouth',
        'PrideGP_LeftPunch_P2': f'{p2_sdl}/FaceWest',
        'PrideGP_RightPunch_P2': f'{p2_sdl}/FaceNorth',
        'PrideGP_LeftKick_P2': f'{p2_sdl}/FaceSouth',
        'PrideGP_RightKick_P2': f'{p2_sdl}/FaceEast',
        'Basara_Weak_P2': f'{p2_sdl}/FaceWest',
        'Basara_Medium_P2': f'{p2_sdl}/FaceNorth',
        'Basara_Strong_P2': f'{p2_sdl}/FaceEast',
        'Basara_Striker_P2': f'{p2_sdl}/FaceSouth',
        'DragonBallZ_Light_P2': f'{p2_sdl}/FaceWest',
        'DragonBallZ_Heavy_P2': f'{p2_sdl}/FaceNorth',
        'DragonBallZ_Guard_P2': f'{p2_sdl}/FaceSouth',
        'DragonBallZ_Jump_P2': f'{p2_sdl}/FaceEast',
        'YuYu_Punch_P2': f'{p2_sdl}/FaceWest',
        'YuYu_Kick_P2': f'{p2_sdl}/FaceNorth',
        'YuYu_Guard_P2': f'{p2_sdl}/FaceSouth',
        'SixButton_LightPunch_P2': f'{p2_sdl}/FaceWest',
        'SixButton_MediumPunch_P2': f'{p2_sdl}/FaceNorth',
        'SixButton_HeavyPunch_P2': f'{p2_sdl}/LeftShoulder',
        'SixButton_LightKick_P2': f'{p2_sdl}/FaceSouth',
        'SixButton_MediumKick_P2': f'{p2_sdl}/FaceEast',
        'SixButton_HeavyKick_P2': f'{p2_sdl}/RightShoulder',
        'P2_DonLeft': f'{p2_sdl}/FaceWest',
        'P2_DonRight': f'{p2_sdl}/FaceNorth',
        'P2_KaLeft': f'{p2_sdl}/FaceSouth',
        'P2_KaRight': f'{p2_sdl}/FaceEast',
        'Smash_TopSpin_P2': f'{p2_sdl}/FaceSouth',
        'Smash_Slice_P2': f'{p2_sdl}/FaceWest',
        'Technic_Activate_P2': f'{p2_sdl}/FaceWest',
        'Technic_Action_P2': f'{p2_sdl}/FaceSouth',
        'Technic_Super_P2': f'{p2_sdl}/FaceEast',
        'Baseball_A_P2': f'{p2_sdl}/FaceSouth',
        'Baseball_B_P2': f'{p2_sdl}/FaceWest',
        'Baseball_C_P2': f'{p2_sdl}/FaceNorth',
        'GundamQuiz_Target_P2': f'{p2_sdl}/FaceEast',
        'GundamQuiz_Shoot_P2': f'{p2_sdl}/FaceWest',
        'GundamQuiz_Melee_P2': f'{p2_sdl}/FaceNorth',
        'GundamQuiz_Jump_P2': f'{p2_sdl}/FaceSouth',
        'Inufuku_1_P2': f'{p2_sdl}/FaceNorth',
        'Inufuku_2_P2': f'{p2_sdl}/FaceSouth',
        'Inufuku_3_P2': f'{p2_sdl}/FaceWest',
        'Inufuku_4_P2': f'{p2_sdl}/FaceEast',
        # Generic & Special buttons mapping
        'P1_Button1': f'{p1_sdl}/FaceSouth',
        'Coin1': f'{p1_sdl}/Back',
        'P1_Start': f'{p1_sdl}/Start',
    }

    for k, v in jvs_mappings.items():
        pcsx2x6_ini_config.set('JVS', k, v)

    ## [GameList]
    if not pcsx2x6_ini_config.has_section('GameList'):
        pcsx2x6_ini_config.add_section('GameList')

    pcsx2x6_ini_config.set('GameList', 'RecursivePaths', str(ROMS / 'namco2x6'))

    with config_file_name.open('w') as configfile:
        pcsx2x6_ini_config.write(configfile)
