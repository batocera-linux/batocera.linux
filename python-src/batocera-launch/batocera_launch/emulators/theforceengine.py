from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

_PATCH_FILE: Final = 'df_patch4.zip'


@cached_dataclass
class TheForceEngine(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'theforceengine',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': ['KEY_LEFTALT', 'KEY_F5'],
                'restore_state': ['KEY_LEFTALT', 'KEY_F9'],
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.config.get_bool('force_widescreen') else 4 / 3

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        mods_dir = self.config_dir / 'Mods'
        mods_dir.mkdir(parents=True, exist_ok=True)

        mod_name: str | None = None
        if (mods_dir / _PATCH_FILE).exists():
            mod_name = _PATCH_FILE

        first_line = self.rom.read_text().splitlines()
        if first_line and first_line[0].strip():
            mod_name = first_line[0].strip()

        force_config = CaseSensitiveConfigParser(interpolation=None)
        settings_file = self.config_dir / 'settings.ini'
        if settings_file.exists():
            force_config.read(settings_file)

        if not force_config.has_section('Window'):
            force_config.add_section('Window')
        force_config.set('Window', 'width', str(self.resolution.width))
        force_config.set('Window', 'height', str(self.resolution.height))
        force_config.set('Window', 'fullscreen', 'true')

        if not force_config.has_section('Graphics'):
            force_config.add_section('Graphics')

        res_height = self.config.get_int('force_render_res', self.resolution.height)
        res_width = int(res_height) * 4 / 3
        res_width_int = int(res_width)
        force_config.set(
            'Graphics',
            'gameWidth',
            str(res_width_int if res_width == res_width_int else res_width),
        )
        force_config.set('Graphics', 'gameHeight', str(res_height))
        force_config.set(
            'Graphics',
            'widescreen',
            self.config.get_bool('force_widescreen', return_values=('true', 'false')),
        )
        force_config.set(
            'Graphics',
            'vsync',
            self.config.get_bool('force_vsync', True, return_values=('true', 'false')),
        )
        force_config.set('Graphics', 'frameRateLimit', self.config.get_str('force_rate', '60'))
        force_config.set('Graphics', 'renderer', self.config.get_str('force_api', '1'))
        force_config.set('Graphics', 'colorMode', self.config.get_str('force_colour', '0'))
        force_config.set(
            'Graphics',
            'useBilinear',
            self.config.get_bool('force_bilinear', return_values=('true', 'false')),
        )
        force_config.set(
            'Graphics',
            'useMipmapping',
            self.config.get_bool('force_mipmapping', return_values=('true', 'false')),
        )
        force_config.set(
            'Graphics',
            'reticleEnable',
            self.config.get_bool('force_crosshair', return_values=('true', 'false')),
        )
        force_config.set(
            'Graphics',
            'bloomEnabled',
            self.config.get_bool('force_postfx', return_values=('true', 'false')),
        )

        if not force_config.has_section('Hud'):
            force_config.add_section('Hud')
        force_config.set('Hud', 'hudScale', '"Proportional"')
        force_config.set('Hud', 'hudPos', '"Edge"')
        force_config.set('Hud', 'scale', '1.000')

        if not force_config.has_section('Enhancements'):
            force_config.add_section('Enhancements')

        force_hd = self.config.get_bool('force_hd', return_values=('1', '0'))
        force_config.set('Enhancements', 'hdTextures', force_hd)
        force_config.set('Enhancements', 'hdSprites', force_hd)
        force_config.set('Enhancements', 'hdHud', force_hd)

        if force_hd == '1':
            force_config.set('Graphics', 'colorMode', '2')

        if not force_config.has_section('Sound'):
            force_config.add_section('Sound')
        force_config.set(
            'Sound',
            'disableSoundInMenus',
            self.config.get_bool('force_menu_sound', return_values=('true', 'false')),
        )
        force_config.set(
            'Sound',
            'use16Channels',
            self.config.get_bool('force_digital_audio', return_values=('true', 'false')),
        )

        if not force_config.has_section('System'):
            force_config.add_section('System')
        if not force_config.has_section('A11y'):
            force_config.add_section('A11y')

        if not force_config.has_section('Game'):
            force_config.add_section('Game')
        force_config.set('Game', 'game', 'Dark Forces')

        if not force_config.has_section('Dark_Forces'):
            force_config.add_section('Dark_Forces')

        dark_forces_path = self.roms_dir / 'Star Wars - Dark Forces'
        force_config.set('Dark_Forces', 'sourcePath', f'"{dark_forces_path}/"')
        force_config.set(
            'Dark_Forces',
            'disableFightMusic',
            self.config.get_bool('force_fight_music', return_values=('true', 'false')),
        )
        force_config.set(
            'Dark_Forces',
            'enableAutoaim',
            self.config.get_bool('force_auto_aim', True, return_values=('true', 'false')),
        )
        force_config.set(
            'Dark_Forces',
            'showSecretFoundMsg',
            self.config.get_bool('force_secret_msg', True, return_values=('true', 'false')),
        )
        force_config.set(
            'Dark_Forces',
            'autorun',
            self.config.get_bool('force_auto_run', return_values=('true', 'false')),
        )
        force_config.set(
            'Dark_Forces',
            'bobaFettFacePlayer',
            self.config.get_bool('force_boba', return_values=('true', 'false')),
        )
        force_config.set(
            'Dark_Forces',
            'smoothVUEs',
            self.config.get_bool('force_smooth_vues', return_values=('true', 'false')),
        )

        if not force_config.has_section('Outlaws'):
            force_config.add_section('Outlaws')
        force_config.set('Outlaws', 'sourcePath', '""')

        if not force_config.has_section('CVar'):
            force_config.add_section('CVar')

        with settings_file.open('w') as configfile:
            force_config.write(configfile)

        args: list[str | Path] = ['theforceengine']

        skip_cutscenes = self.config.get_str('force_skip_cutscenes')
        if skip_cutscenes == 'initial':
            args.append('-c0')
        elif skip_cutscenes == 'skip':
            args.append('-c')

        if mod_name is not None:
            args.append(f'-u{mod_name}')

        args.append('-gDARK')

        return Command(args, env={'TFE_DATA_HOME': self.config_dir})
