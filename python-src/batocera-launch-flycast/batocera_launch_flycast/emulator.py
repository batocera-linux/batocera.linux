from __future__ import annotations

from importlib import resources
from shutil import copyfile
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CONFIGS, SAVES
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
)

from .controllers import generate_controller_config, generate_keyboard_config

if TYPE_CHECKING:
    from pathlib import Path

VMU_BLANK: Final = resources.files() / 'data' / 'vmu_save_blank.bin'


@cached_dataclass
class Flycast(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'flycast',
            'keys': {
                'exit': 'KEY_F7',
                'menu': 'KEY_TAB',
                'save_state': 'KEY_F8',
                'restore_state': 'KEY_F9',
                'fastforward': 'KEY_SPACE',
            },
        }

    @cached_property
    def bios_dir(self) -> Path:
        return BIOS / 'dc'

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'dreamcast' / 'flycast'

    @cached_property
    def vmua1_path(self) -> Path:
        return self.saves_dir / 'vmu_save_A1.bin'

    @cached_property
    def vmua2_path(self) -> Path:
        return self.saves_dir / 'vmu_save_A2.bin'

    @cached_property
    def mapping_dir(self) -> Path:
        return self.config_dir / 'mappings'

    async def configure(self) -> Command:
        config = CaseSensitiveConfigParser(interpolation=None)
        config_path = self.config_dir / 'emu.cfg'

        if config_path.exists():
            try:
                config.read(config_path)
            except Exception:
                pass  # give up the file

        if not config.has_section('input'):
            config.add_section('input')

        # Lightguns - configure before controllers (guns take priority on ports)
        gun_ports: set[int] = set()
        if self.config.use_guns and self.guns:
            for player_number, _ in enumerate(self.guns[:4], start=1):
                config.set('input', f'device{player_number}', '7')  # MDT_LightGun
                config.set('input', f'device{player_number}.1', '1')  # VMU
                config.set('input', f'device{player_number}.2', '10')  # None
                gun_ports.add(player_number)

        # For each pad detected
        for controller in self.controllers:
            # Skip ports already assigned to guns
            if controller.player_number in gun_ports:
                continue

            # Write the mapping files for Dreamcast
            if self.system == 'dreamcast':
                generate_controller_config(self.mapping_dir, controller, 'dreamcast')
            else:
                # Write the Arcade variant (Atomiswave & Naomi/2)
                generate_controller_config(self.mapping_dir, controller, 'arcade')

            # Set the controller type per Port
            config.set('input', f'device{controller.player_number}', '0')  # Sega Controller
            config.set('input', f'device{controller.player_number}.1', '1')  # Sega VMU
            # Set controller pack, gui option
            config.set(
                'input',
                f'device{controller.player_number}.2',
                self.config.get_str(f'flycast_ctrl{controller.player_number}_pack', '1'),
            )  # Sega VMU
            # Ensure controller(s) are on seperate Ports
            port = controller.player_number - 1
            config.set('input', f'maple_sdl_joystick_{controller.index}', str(port))

        # add the keyboard mappings for hotkeys
        generate_keyboard_config(self.mapping_dir)

        if not config.has_section('config'):
            config.add_section('config')
        if not config.has_section('window'):
            config.add_section('window')
        # ensure we are always fullscreen
        config.set('window', 'fullscreen', 'yes')
        # set video resolution
        config.set('window', 'width', str(self.resolution.width))
        config.set('window', 'height', str(self.resolution.height))
        # set render resolution - default 480 (Native)
        config.set('config', 'rend.Resolution', self.config.get_str('flycast_render_resolution', '480'))
        # wide screen mode - default off
        config.set('config', 'rend.WideScreen', self.config.get_str('flycast_ratio', 'no'))
        # rotate option - default off
        config.set('config', 'rend.Rotate90', self.config.get_str('flycast_rotate', 'no'))
        # renderer - default: OpenGL
        renderer = self.config.get('flycast_renderer')
        sorting = self.config.get('flycast_sorting')

        if renderer == '0':
            if sorting == '3':
                # per pixel
                config.set('config', 'pvr.rend', '3')
            else:
                # per triangle
                config.set('config', 'pvr.rend', '0')
        elif renderer == '4':
            if sorting == '3':
                # per pixel
                config.set('config', 'pvr.rend', '5')
            else:
                # per triangle
                config.set('config', 'pvr.rend', '4')
        else:
            config.set('config', 'pvr.rend', '0')
            if sorting == '3':
                # per pixel
                config.set('config', 'pvr.rend', '3')

        # anisotropic filtering
        config.set('config', 'rend.AnisotropicFiltering', self.config.get_str('flycast_anisotropic', '1'))
        # transparent sorting
        # per strip
        config.set('config', 'rend.PerStripSorting', 'yes' if self.config.get('flycast_sorting') == '2' else 'no')

        # [Dreamcast specifics]
        # language
        config.set('config', 'Dreamcast.Language', self.config.get_str('flycast_language', '1'))
        # region
        config.set('config', 'Dreamcast.Region', self.config.get_str('flycast_region', '1'))
        # save / load states
        config.set('config', 'Dreamcast.AutoLoadState', self.config.get_str('flycast_loadstate', 'no'))
        config.set('config', 'Dreamcast.AutoSaveState', self.config.get_str('flycast_savestate', 'no'))
        # windows CE
        config.set('config', 'Dreamcast.ForceWindowsCE', self.config.get_str('flycast_winCE', 'no'))
        # Per-game VMU
        config.set('config', 'PerGameVmu', self.config.get_bool('flycast_per_game_vmu', return_values=('yes', 'no')))
        # DSP
        config.set('config', 'aica.DSPEnabled', self.config.get_str('flycast_DSP', 'no'))
        # Guns crosshairs
        config.set('config', 'rend.CrossHairColor1', self.config.get_str('flycast_lightgun1_crosshair', '0'))
        config.set('config', 'rend.CrossHairColor2', self.config.get_str('flycast_lightgun2_crosshair', '0'))
        config.set('config', 'rend.CrossHairColor3', self.config.get_str('flycast_lightgun3_crosshair', '0'))
        config.set('config', 'rend.CrossHairColor4', self.config.get_str('flycast_lightgun4_crosshair', '0'))

        # Retroachievements
        if not config.has_section('achievements'):
            config.add_section('achievements')

        if self.config.get_bool('retroachievements'):
            username = self.config.get('retroachievements.username', '')
            hardcore = self.config.get_bool('retroachievements.hardcore', return_values=('yes', 'no'))
            token = self.config.get('retroachievements.token', '')

            # apply config
            config.set('achievements', 'Enabled', 'yes')
            config.set('achievements', 'HardcoreMode', hardcore)
            config.set('achievements', 'Token', token)
            config.set('achievements', 'UserName', username)
        else:
            config.set('achievements', 'Enabled', 'no')

        # custom : allow the user to configure directly emu.cfg via batocera.conf via lines like : dreamcast.flycast.section.option=value
        for section_option, user_config_value in self.config.items(starts_with='flycast.'):
            custom_section, _, custom_option = section_option.partition('.')
            if not config.has_section(custom_section):
                config.add_section(custom_section)
            config.set(custom_section, custom_option, user_config_value)

        ### update the configuration file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open('w+') as cfg_file:
            config.write(cfg_file)

        # internal config
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        if not self.vmua1_path.is_file() or not self.vmua2_path.is_file():
            with resources.as_file(VMU_BLANK) as vmu_blank:
                # vmuA1
                if not self.vmua1_path.is_file():
                    copyfile(vmu_blank, self.vmua1_path)

                # vmuA2
                if not self.vmua2_path.is_file():
                    copyfile(vmu_blank, self.vmua2_path)

        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME.
        # VMU will be in $XDG_DATA_HOME / $FLYCAST_DATADIR because it needs rw access -> /userdata/saves/dreamcast
        # $FLYCAST_BIOS_PATH is where Flaycast should find the bios files
        # controller cfg files are set with an absolute path, so no worry
        return Command(
            ['/usr/bin/flycast', self.rom],
            {
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CONFIG_DIRS': CONFIGS,
                'XDG_DATA_HOME': self.saves_dir.parent,
                'FLYCAST_DATADIR': self.saves_dir.parent,
                'FLYCAST_BIOS_PATH': self.bios_dir,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
