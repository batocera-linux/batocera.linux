from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Emulator, HotkeysContext, SpecialDecorationsMixin
from batocera_launch_mame_common import (
    MameControlScheme,
    MessSystemInfo,
    load_all_mame_control_mappings,
    load_mame_control_scheme,
)
from batocera_launch_mame_common.paths import MAME_BIN_DIR, MAMEPathsMixin

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class MAMEBase(MAMEPathsMixin, SpecialDecorationsMixin, Emulator):  # pyright: ignore[reportIncompatibleVariableOverride]
    @property
    def handles_bezels(self) -> bool:
        return True

    @property
    def execution_path(self) -> Path | None:
        # Change directory to MAME folder (allows data plugin to load properly)
        return MAME_BIN_DIR

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'mame',
            'keys': {
                'exit': 'KEY_ESC',
                'menu': 'KEY_TAB',
                'pause': 'KEY_F5',
                'reset': 'KEY_F3',
                'coin': 'KEY_5',
                'fastforward': 'KEY_PAGEDOWN',
                'save_state': ['KEY_LEFTSHIFT', 'KEY_F6'],
                'restore_state': ['KEY_LEFTSHIFT', 'KEY_F7'],
            },
        }

    @cached_property
    def mess_system_info(self) -> MessSystemInfo | None:
        return MessSystemInfo.load(self.system)

    @cached_property
    def bezel_set(self) -> str | None:
        bezel_set = self.config.get_str('bezel') or None

        if self.config.get_bool('forceNoBezel'):
            bezel_set = None

        return bezel_set

    @cached_property
    def use_mouse(self) -> bool:
        mess_system = self.mess_system_info
        return self.config.get_bool('use_mouse') or not (mess_system is None or not mess_system.name)

    @cached_property
    def mame_control_scheme(self) -> MameControlScheme:
        return load_mame_control_scheme(self.config.get_str('altlayout', 'auto'), self.rom.stem)

    @cached_property
    def all_mame_control_mappings(self) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        return load_all_mame_control_mappings(self.mame_control_scheme, self.config.use_guns, self.use_mouse)
