from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import UnknownEmulator

if TYPE_CHECKING:
    from .emulator import Emulator


def load_emulator(emulator_name: str) -> type[Emulator]:
    from importlib.metadata import entry_points

    emulators = entry_points(group='batocera_launch.emulators')

    if emulator_name in emulators.names:
        try:
            return emulators[emulator_name].load()
        except Exception as e:
            raise UnknownEmulator from e

    if 'configgen' in emulators.names:
        return emulators['configgen'].load()

    raise UnknownEmulator
