from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CACHE, CHEATS, CONFIGS, ROMS, SAVES, SCREENSHOTS
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_LEGACY_CORE: Final = 'duckstation-legacy'

_LANGUAGES: Final = {
    'en_US': 'en',
    'de_DE': 'de',
    'fr_FR': 'fr',
    'es_ES': 'es',
    'he_IL': 'he',
    'it_IT': 'it',
    'ja_JP': 'ja',
    'nl_NL': 'nl',
    'pl_PL': 'pl',
    'pt_BR': 'pt-br',
    'pt_PT': 'pt-pt',
    'ru_RU': 'ru',
    'zh_CN': 'zh-cn',
}

_BIOS_LISTS: Final[Mapping[str, Sequence[str]]] = {
    'NTSCU': ['scph101.bin', 'scph1001.bin', 'scph5501.bin', 'scph7001.bin', 'scph7501.bin'],
    'PAL': [
        'scph1002.bin',
        'scph5502.bin',
        'scph5552.bin',
        'scph7002.bin',
        'scph7502.bin',
        'scph9002.bin',
        'scph102a.bin',
        'scph102b.bin',
    ],
    'NTSCJ': ['scph100.bin', 'scph1000.bin', 'scph3000.bin', 'scph3500.bin', 'scph5500.bin', 'scph7000.bin', 'scph7003.bin'],
    'Uni': ['psxonpsp660.bin', 'ps1_rom.bin'],
}

_BIOS_REGION_KEYS: Final = {'NTSCU': 'PathNTSCU', 'PAL': 'PathPAL', 'NTSCJ': 'PathNTSCJ'}

_PEDAL_KEYS: Final = {1: 'c', 2: 'v', 3: 'b', 4: 'n'}

# SDL2 pad bindings are identical for every controller
_PAD_BINDINGS: Final = {
    'Up': 'DPadUp',
    'Right': 'DPadRight',
    'Down': 'DPadDown',
    'Left': 'DPadLeft',
    'Triangle': 'Y',
    'Circle': 'B',
    'Cross': 'A',
    'Square': 'X',
    'Select': 'Back',
    'Start': 'Start',
    'L1': 'LeftShoulder',
    'R1': 'RightShoulder',
    'L2': '+LeftTrigger',
    'R2': '+RightTrigger',
    'L3': 'LeftStick',
    'R3': 'RightStick',
    'LLeft': '-LeftX',
    'LRight': '+LeftX',
    'LDown': '+LeftY',
    'LUp': '-LeftY',
    'RLeft': '-RightX',
    'RRight': '+RightX',
    'RDown': '+RightY',
    'RUp': '-RightY',
    'SmallMotor': 'SmallMotor',
    'LargeMotor': 'LargeMotor',
}

_NEGCON_BINDINGS: Final = {
    'A': 'B',
    'B': 'Y',
    'I': '+RightTrigger',
    'II': '+LeftTrigger',
    'L': 'LeftShoulder',
    'R': 'RightShoulder',
    'SteeringLeft': '-LeftX',
    'SteeringRight': '+LeftX',
}

_HOTKEYS: Final = {
    'FastForward': 'Keyboard/Tab',
    'Reset': 'Keyboard/F6',
    'LoadSelectedSaveState': 'Keyboard/F1',
    'SaveSelectedSaveState': 'Keyboard/F2',
    'SelectPreviousSaveStateSlot': 'Keyboard/F3',
    'SelectNextSaveStateSlot': 'Keyboard/F4',
    'Screenshot': 'Keyboard/F10',
    'Rewind': 'Keyboard/F5',
    'OpenPauseMenu': 'Keyboard/F7',
    'ChangeDisc': 'Keyboard/F8',
}


def _language() -> str:
    return _LANGUAGES.get(environ['LANG'][:5], _LANGUAGES['en_US'])


def _rewrite_m3u_full_path(m3u: Path, /) -> Path:
    """Rewrite an m3u with absolute paths, working around DuckStation's handling of relative ones."""
    first_line = m3u.read_text().splitlines()[0].rstrip()
    rewritten = Path('/tmp') / Path(first_line).with_suffix('.m3u').name

    with m3u.open() as source, rewritten.open('w') as target:
        for line in source:
            # handle both "/MGScd1.chd" and "MGScd1.chd"
            target.write(str(m3u.parent / line.removeprefix('/')))

    return rewritten


def _find_bios() -> dict[str, str]:
    try:
        files_lower = {file.name.lower(): file.name for file in BIOS.iterdir()}
    except OSError as e:
        raise BatoceraException(f'Unable to read BIOS directory: {BIOS}') from e

    found: dict[str, str] = {}

    for region, bios_list in _BIOS_LISTS.items():
        for bios in bios_list:
            if bios.lower() in files_lower:
                found[region] = files_lower[bios.lower()]
                break

    return found


@cached_dataclass
class Duckstation(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'duckstation',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_F7',
                'reset': 'KEY_F6',
                'restore_state': 'KEY_F1',
                'save_state': 'KEY_F2',
                'previous_slot': 'KEY_F3',
                'next_slot': 'KEY_F4',
                'rewind': 'KEY_F5',
                'fastforward': 'KEY_TAB',
                'next_disk': 'KEY_F8',
            },
        }

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return Path('/usr/share/duckstation/resources/gamecontrollerdb.txt')

    @property
    def _legacy(self) -> bool:
        return self.core == _LEGACY_CORE

    def _write_settings(self) -> None:
        settings = CaseSensitiveConfigParser(interpolation=None)
        settings_path = self.config_dir / 'settings.ini'
        if settings_path.exists():
            settings.read(settings_path)

        for section in (
            'Main',
            'ControllerPorts',
            'Console',
            'BIOS',
            'CPU',
            'GPU',
            'Display',
            'Audio',
            'GameList',
            'Cheevos',
            'TextureReplacements',
            'InputSources',
            'MemoryCards',
            'Folders',
            'Hotkeys',
            'CDROM',
        ):
            if not settings.has_section(section):
                settings.add_section(section)

        ## [Main]
        settings.set('Main', 'SettingsVersion', '3')  # Probably to be updated in the future
        settings.set('Main', 'InhibitScreensaver', 'true')
        settings.set('Main', 'StartPaused', 'false')
        settings.set('Main', 'StartFullscreen', 'true')
        settings.set('Main', 'PauseOnFocusLoss', 'false')
        settings.set('Main', 'PauseOnMenu', 'true')
        settings.set('Main', 'ConfirmPowerOff', 'false')
        settings.set('Main', 'ApplyGameSettings', 'true')
        if not self._legacy:
            settings.set('Main', 'SetupWizardIncomplete', 'false')
        settings.set('Main', 'EmulationSpeed', self.config.get('duckstation_clocking', '1'))
        settings.set('Main', 'SyncToHostRefreshRate', self.config.get('duckstation_hrr', 'false'))

        # Rewind
        settings.set('Main', 'RewindEnable', 'true')
        settings.set('Main', 'RewindFrequency', '1')  # Frame skipped each seconds
        match self.config.get('duckstation_rewind'):
            case '120' | '90' | '60' | '30' | '15' as rewind:
                settings.set('Main', 'RewindSaveSlots', rewind)  # Total duration available in sec
            case '10':
                settings.set('Main', 'RewindSaveSlots', '100')
                settings.set('Main', 'RewindFrequency', '0.100000')
            case '5':
                settings.set('Main', 'RewindSaveSlots', '50')
                settings.set('Main', 'RewindFrequency', '0.050000')
            case _:
                settings.set('Main', 'RewindEnable', 'false')

        settings.set('Main', 'EnableDiscordPresence', 'false')
        settings.set('Main', 'Language', _language())

        ## [ControllerPorts]
        settings.set('ControllerPorts', 'ControllerSettingsMigrated', 'true')
        settings.set('ControllerPorts', 'MultitapMode', 'Disabled')
        settings.set('ControllerPorts', 'PointerXScale', '8')
        settings.set('ControllerPorts', 'PointerYScale', '8')
        settings.set('ControllerPorts', 'PointerXInvert', 'false')
        settings.set('ControllerPorts', 'PointerYInvert', 'false')

        ## [Console]
        settings.set('Console', 'Region', self.config.get('duckstation_region', 'Auto'))
        if not self._legacy:
            settings.set('Console', 'EnableCheats', self.config.get('duckstation_cheats', 'False'))

        ## [BIOS]
        settings.set('BIOS', 'SearchDirectory', str(BIOS))
        settings.set('BIOS', 'PatchFastBoot', self.config.get('duckstation_PatchFastBoot', 'false'))

        found_bios = _find_bios()
        if self._legacy:
            # the legacy core knows nothing about a universal BIOS
            found_bios.pop('Uni', None)

        if not found_bios:
            raise BatoceraException('No PSX1 BIOS found')

        if uni_bios := found_bios.get('Uni'):
            for key in _BIOS_REGION_KEYS.values():
                settings.set('BIOS', key, uni_bios)
        else:
            for region, bios in found_bios.items():
                settings.set('BIOS', _BIOS_REGION_KEYS[region], bios)

        ## [CPU]
        settings.set('CPU', 'ExecutionMode', self.config.get('duckstation_executionmode', 'Recompiler'))

        ## [GPU]
        settings.set('GPU', 'Renderer', self.config.get('duckstation_gfxbackend', 'OpenGL'))
        # Multisampling force (MSAA or SSAA) - no GUI option anymore...
        settings.set('GPU', 'PerSampleShading', 'false')
        settings.set('GPU', 'Multisamples', '1')
        settings.set('GPU', 'ThreadedPresentation', self.config.get('duckstation_threadedpresentation', 'false'))
        settings.set('GPU', 'ResolutionScale', self.config.get('duckstation_resolution_scale', '1'))
        settings.set('GPU', 'WidescreenHack', self.config.get('duckstation_widescreen_hack', 'false'))
        settings.set('GPU', 'ForceNTSCTimings', self.config.get('duckstation_60hz', 'false'))
        settings.set('GPU', 'TextureFilter', self.config.get('duckstation_texture_filtering', 'Nearest'))
        pgxp = self.config.get('duckstation_pgxp', 'true')
        settings.set('GPU', 'PGXPEnable', pgxp)
        settings.set('GPU', 'PGXPCulling', pgxp)
        settings.set('GPU', 'PGXPTextureCorrection', pgxp)
        settings.set('GPU', 'PGXPPreserveProjFP', pgxp)
        settings.set('GPU', 'TrueColor', self.config.get('duckstation_truecolour', 'false'))
        settings.set('GPU', 'ScaledDithering', self.config.get('duckstation_dithering', 'true'))
        settings.set('GPU', 'DisableInterlacing', self.config.get('duckstation_interlacing', 'false'))

        if antialiasing := self.config.get_str('duckstation_antialiasing'):
            if 'ssaa' in antialiasing:
                settings.set('GPU', 'PerSampleShading', 'true')
                settings.set('GPU', 'Multisamples', antialiasing.split('-')[0])
            else:
                settings.set('GPU', 'Multisamples', antialiasing)
                settings.set('GPU', 'PerSampleShading', 'false')

        ## [Display]
        aspect_ratio = self.config.get_str('duckstation_ratio')
        settings.set('Display', 'AspectRatio', aspect_ratio or 'Auto (Game Native)')

        if aspect_ratio is not None and aspect_ratio != '4:3':
            self.config['bezel'] = 'none'

        settings.set('Display', 'VSync', self.config.get('duckstation_vsync', 'false'))
        settings.set('Display', 'CropMode', self.config.get('duckstation_CropMode', 'Overscan'))
        # Enable Frameskipping = option missing
        settings.set('Display', 'DisplayAllFrames', 'false')
        settings.set('Display', 'ShowOSDMessages', self.config.get('duckstation_osd', 'false'))
        # Optimal frame pacing
        settings.set('Display', 'DisplayAllFrames', self.config.get('duckstation_ofp', 'false'))
        settings.set('Display', 'IntegerScaling', self.config.get('duckstation_integer', 'false'))
        settings.set('Display', 'LinearFiltering', self.config.get('duckstation_linear', 'false'))
        stretch = self.config.get('duckstation_stretch', 'false')
        settings.set('Display', 'Stretch', stretch)

        if stretch == 'true' and self.config.get('duckstation_integer', 'false') == 'false':
            self.config['bezel'] = 'none'

        ## [Audio]
        settings.set('Audio', 'StretchMode', self.config.get('duckstation_audio_mode', 'TimeStretch'))

        ## [GameList]
        settings.set('GameList', 'RecursivePaths', str(ROMS / 'psx'))

        ## [Cheevos]
        if self.config.get_bool('retroachievements'):
            settings.set('Cheevos', 'Enabled', 'true')
            settings.set('Cheevos', 'Username', self.config.get('retroachievements.username', ''))
            settings.set('Cheevos', 'Token', self.config.get('retroachievements.token', ''))
            # For "hardcore" retroachievement points (no save, no rewind...)
            settings.set(
                'Cheevos',
                'ChallengeMode',
                self.config.get_bool('retroachievements.hardcore', return_values=('true', 'false')),
            )
            # Rich presence information will be collected and sent to the server where supported
            settings.set(
                'Cheevos',
                'RichPresence',
                self.config.get_bool('retroachievements.richpresence', return_values=('true', 'false')),
            )
            settings.set(
                'Cheevos',
                'PrimedIndicators',
                self.config.get_bool('retroachievements.challenge_indicators', return_values=('true', 'false')),
            )
            settings.set(
                'Cheevos',
                'Leaderboards',
                self.config.get_bool('retroachievements.leaderboards', return_values=('true', 'false')),
            )
            if not self._legacy:
                settings.set(
                    'Cheevos',
                    'UnofficialTestMode',
                    self.config.get_bool('retroachievements.unofficial', return_values=('true', 'false')),
                )
        else:
            settings.set('Cheevos', 'Enabled', 'false')

        ## [TextureReplacements]
        # Texture replacements live in saves/textures/<psx game id>, Normal by default
        enable_vram_write_replacements = 'true'
        preload_textures = 'false'

        match self.config.get('duckstation_custom_textures'):
            case 'false' | '0':
                enable_vram_write_replacements = 'false'
            case 'preload':
                preload_textures = 'true'

        settings.set('TextureReplacements', 'EnableVRAMWriteReplacements', enable_vram_write_replacements)
        settings.set('TextureReplacements', 'PreloadTextures', preload_textures)

        ## [InputSources]
        settings.set('InputSources', 'SDL', 'true')
        settings.set('InputSources', 'SDLControllerEnhancedMode', 'false')
        settings.set('InputSources', 'Evdev', 'false')
        settings.set('InputSources', 'XInput', 'false')
        settings.set('InputSources', 'RawInput', 'false')

        ## [MemoryCards]
        settings.set('MemoryCards', 'Directory', '../../../saves/duckstation/memcards')

        ## [Folders]
        # Paths are relative to the config directory
        if not self._legacy:
            for directory in (CACHE / 'duckstation', SCREENSHOTS, SAVES / 'duckstation', CHEATS / 'duckstation'):
                directory.mkdir(parents=True, exist_ok=True)

        settings.set('Folders', 'Cache', '../../cache/duckstation')
        settings.set('Folders', 'Screenshots', '../../../screenshots')
        settings.set('Folders', 'SaveStates', '../../../saves/duckstation')
        settings.set('Folders', 'Cheats', '../../../cheats/duckstation')

        self._write_pads(settings)
        self._write_guns(settings)

        ## [Hotkeys]
        # Force defaults to be aligned with evmapy
        for hotkey, key in _HOTKEYS.items():
            settings.set('Hotkeys', hotkey, key)
        if settings.has_option('Hotkeys', 'OpenQuickMenu'):
            settings.remove_option('Hotkeys', 'OpenQuickMenu')

        ## [CDROM]
        settings.set('CDROM', 'AllowBootingWithoutSBIFile', self.config.get('duckstation_boot_without_sbi', 'false'))

        ## [UI]
        if not self._legacy:
            if not settings.has_section('UI'):
                settings.add_section('UI')
            settings.set('UI', 'UnofficialBuildWarningConfirmed', 'true')

        settings_path.parent.mkdir(parents=True, exist_ok=True)
        with settings_path.open('w') as config_file:
            settings.write(config_file)

    def _write_pads(self, settings: CaseSensitiveConfigParser, /) -> None:
        for player in range(1, 9):
            section = f'Pad{player}'
            if settings.has_section(section):
                settings.remove_section(section)
            settings.add_section(section)
            settings.set(section, 'Type', 'None')

        settings.set('ControllerPorts', 'MultitapMode', 'Disabled')

        for player, pad in enumerate(self.controllers[:8], start=1):
            # automatically add the multi-tap
            if player > 2:
                settings.set('ControllerPorts', 'MultitapMode', 'BothPorts' if player > 4 else 'Port1Only')

            section = f'Pad{player}'
            sdl = f'SDL-{pad.index}'
            controller_type = self.config.get_str(f'duckstation_Controller{player}')

            settings.set(section, 'Type', controller_type or 'DigitalController')

            for option, binding in _PAD_BINDINGS.items():
                settings.set(section, option, f'{sdl}/{binding}')

            settings.set(section, 'VibrationBias', '8')

            # D-Pad to Joystick
            digitalmode = self.config.get_str('duckstation_digitalmode')
            settings.set(section, 'AnalogDPadInDigitalMode', digitalmode or 'false')
            if digitalmode and controller_type == 'AnalogController':
                # the legacy core needs a chord, the current one toggles on Guide alone
                settings.set(section, 'Analog', f'{sdl}/Guide & {sdl}/+LeftTrigger' if self._legacy else f'{sdl}/Guide')

            if controller_type == 'NeGcon':
                for option, binding in _NEGCON_BINDINGS.items():
                    settings.set(section, option, f'{sdl}/{binding}')

            # The legacy core drives a GunCon through the controller type rather than a detected gun
            if self._legacy and controller_type == 'GunCon':
                settings.set(section, 'Trigger', f'{sdl}/+RightTrigger')
                settings.set(section, 'ShootOffscreen', f'{sdl}/+LeftTrigger')
                settings.set(section, 'A', f'{sdl}/A')
                settings.set(section, 'B', f'{sdl}/B')

            if controller_type == 'PlayStationMouse':
                settings.set(section, 'Right', f'{sdl}/B')
                settings.set(section, 'Left', f'{sdl}/A')
                settings.set(section, 'RelativeMouseMode', f'{sdl}true')

    def _write_guns(self, settings: CaseSensitiveConfigParser, /) -> None:
        # Guns - configure based on detected guns, not controllers. The legacy core has no
        # equivalent; it maps a GunCon from the controller type in _write_pads instead.
        if self._legacy or not (self.config.use_guns and self.guns):
            return

        for player, _ in enumerate(self.guns[:8], start=1):
            section = f'Pad{player}'
            pointer = f'Pointer-{player - 1}'
            # Gun mapping is hardcoded into patch.
            # Justifier ROM mapping: BTN_LEFT = Trigger | BTN_RIGHT = Back | BTN_MIDDLE = Start
            if self.metadata.get('gun_type') == 'justifier':
                settings.set(section, 'Type', 'Justifier')
            else:
                # GunCon ROM mapping: BTN_LEFT = Trigger | BTN_RIGHT = A | BTN_MIDDLE = B
                settings.set(section, 'Type', 'GunCon')
                # Pedal key for button A
                pedal_key = self.config.get_str(f'controllers.pedals{player}', _PEDAL_KEYS.get(player))
                if pedal_key:
                    settings.set(section, 'A', f'{pointer}/RightButton & Keyboard/{pedal_key.upper()}')
                else:
                    settings.set(section, 'A', f'{pointer}/RightButton')

            # Crosshairs - BGR color code. Player 1 red; player 2 blue.
            settings.set(section, 'CrosshairScale', self.config.get('duckstation_crosshair', '0'))
            settings.set(section, 'CrosshairColor', '0000FF' if player == 1 else 'FF0000')

    async def configure(self) -> Command:
        rom = _rewrite_m3u_full_path(self.rom) if self.rom.suffix == '.m3u' else self.rom

        self._write_settings()

        if Path('/usr/bin/duckstation-qt').exists():
            args: list[str | Path] = ['duckstation-qt', '-batch', '-nogui', '--', rom]
        else:
            args = ['duckstation-nogui', '-batch', '-fullscreen', '--', rom]

        env: dict[str, str | Path] = {
            'XDG_CONFIG_HOME': CONFIGS,
            'QT_QPA_PLATFORM': 'xcb' if self._legacy or not environ.get('WAYLAND_DISPLAY') else 'wayland',
            'SDL_JOYSTICK_HIDAPI': '0',
        }

        if not self._legacy:
            # use their modified shaderc library
            env['LD_LIBRARY_PATH'] = '/usr/stenzek-shaderc/lib:/usr/lib'

        return Command(args, env=env)
