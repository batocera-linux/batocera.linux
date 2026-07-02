from __future__ import annotations

from dataclasses import dataclass
from shutil import copyfile
from typing import TYPE_CHECKING

from batocera_common.paths import CONFIGS
from batocera_launch import CaseSensitiveConfigParser, Command, Emulator, HotkeysContext
from batocera_launch.devices.controller import (
    generate_sdl_game_controller_config as generate_sdl_game_controller_config,
)
from batocera_launch_flycast.controllers import generate_controller_config, generate_keyboard_config
from batocera_launch_flycast.paths import (
    FLYCAST_BIOS,
    FLYCAST_CONFIG,
    FLYCAST_SAVES,
    FLYCAST_VMU_BLANK,
    FLYCAST_VMUA1,
    FLYCAST_VMUA2,
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(slots=True)
class Flycast(Emulator):
    needs_sdl_game_controller_config = True

    @property
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

    def configure(self, prepared_rom: Path, /) -> Command:
        config = CaseSensitiveConfigParser(interpolation=None)
        if FLYCAST_CONFIG.exists():
            try:
                config.read(FLYCAST_CONFIG)
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
                generate_controller_config(controller, 'dreamcast')
            else:
                # Write the Arcade variant (Atomiswave & Naomi/2)
                generate_controller_config(controller, 'arcade')

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
        generate_keyboard_config()

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
        FLYCAST_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with FLYCAST_CONFIG.open('w+') as cfg_file:
            config.write(cfg_file)

        # internal config
        FLYCAST_SAVES.mkdir(parents=True, exist_ok=True)

        # vmuA1
        if not FLYCAST_VMUA1.is_file():
            copyfile(FLYCAST_VMU_BLANK, FLYCAST_VMUA1)
        # vmuA2
        if not FLYCAST_VMUA2.is_file():
            copyfile(FLYCAST_VMU_BLANK, FLYCAST_VMUA2)

        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME.
        # VMU will be in $XDG_DATA_HOME / $FLYCAST_DATADIR because it needs rw access -> /userdata/saves/dreamcast
        # $FLYCAST_BIOS_PATH is where Flaycast should find the bios files
        # controller cfg files are set with an absolute path, so no worry
        return Command(
            ['/usr/bin/flycast', prepared_rom],
            {
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CONFIG_DIRS': CONFIGS,
                'XDG_DATA_HOME': FLYCAST_SAVES.parent,
                'FLYCAST_DATADIR': FLYCAST_SAVES.parent,
                'FLYCAST_BIOS_PATH': FLYCAST_BIOS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
