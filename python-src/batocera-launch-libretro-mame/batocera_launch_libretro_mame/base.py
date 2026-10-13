from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import BatoceraException
from batocera_launch_libretro import Core
from batocera_launch_mame_common import MameControlScheme, MessSystemInfo, load_mame_control_scheme
from batocera_launch_mame_common.paths import MAMEPathsMixin

_logger = logging.getLogger(__name__)

_CORE_CONFIG: Final = CONFIGS / 'lr-mame'
_ARCADE_SYSTEMS: Final = {
    'mame',
    'neogeo',
    'lcdgames',
    'tvgames',
    'vis',
    'namco22',
    'model1',
    'model2',
    'model3',
    'cave3rd',
    'gaelco',
    'hikaru',
}


@cached_dataclass
class MAMEBase(MAMEPathsMixin, Core):
    gun_mapping: ClassVar = {'default': {'p1': 0, 'p2': 1, 'p3': 2}}

    @cached_property
    def map_lightguns(self) -> bool:
        return self.config.get_bool('lightgun_map', self.config.core == 'mame')

    @cached_property
    def cmd_filename(self) -> Path:
        return Path('/var/run/cmdfiles') / f'{self.rom.stem}.cmd'

    @cached_property
    def is_arcade(self) -> bool:
        return self.system in _ARCADE_SYSTEMS

    @cached_property
    def mess_system_info(self) -> MessSystemInfo | None:
        info = MessSystemInfo.load(self.system)

        if not self.is_arcade and info is None:
            raise BatoceraException(f'Unknown MAME system: {self.system}')

        return info

    @cached_property
    def mame_control_scheme(self) -> MameControlScheme:
        return load_mame_control_scheme(
            self.config.get('altlayout', 'auto'),
            self.rom.stem,
            overrides={
                'capcom': {'fightstick': 'sfsnes'},
                'mortal_kombat': {'fightstick': 'mksnes'},
                'killer_instinct': {'fightstick': 'kisnes'},
                'default': {
                    'fightstick': 'sfsnes',
                    'megadrive': 'default',
                },
            },
        )

    @cached_property
    def rom_argument(self) -> str | Path | None:
        return self.cmd_filename

    @cached_property
    def mess_model(self) -> str:
        if not self.is_arcade:
            if altmodel := self.config.get('altmodel'):
                return altmodel

            if (mess_system_info := self.mess_system_info) is not None:
                return mess_system_info.name

        return ''

    @cached_property
    def cfg_path(self) -> Path:
        custom_cfg = self.config.get_bool('customcfg')
        core_segment = f'lr-{self.config.core}' if self.config.core == 'mame' else self.config.core

        if self.is_arcade or not self.mess_system_info or not self.mess_system_info.name:
            return CONFIGS.joinpath(core_segment, 'custom') if custom_cfg else self.saves_dir.joinpath('mame', 'cfg')

        if self.config.get_bool('pergamecfg'):
            return CONFIGS / core_segment / self.mess_system_info.name / self.rom.name

        if custom_cfg:
            return CONFIGS / core_segment / self.mess_system_info.name / 'custom'

        return self.saves_dir / 'cfg' / self.mess_system_info.name

    @cached_property
    def control_type(self) -> str:
        if self.system == 'bbcmicro' and (stick_type := self.config.get('sticktype', 'none')) != 'none':
            return stick_type

        if self.system == 'apple2' and (game_io := self.config.get('gameio', 'none')) != 'none':
            if game_io == 'joyport' and self.mess_model != 'apple2p':
                _logger.debug('Joyport joystick is only compatible with Apple II Plus')
            else:
                return game_io

        return 'none'
