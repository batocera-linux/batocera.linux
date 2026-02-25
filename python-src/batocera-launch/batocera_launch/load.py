from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch.exceptions import UnknownEmulator

if TYPE_CHECKING:
    from batocera_launch.emulator import Emulator


def load_emulator(emulator_name: str) -> type[Emulator]:
    from importlib.metadata import entry_points

    emulators = entry_points(group='batocera_launch.emulators')

    if emulator_name in emulators.names:
        return emulators[emulator_name].load()

    if 'configgen' in emulators.names:
        return emulators['configgen'].load()

    raise UnknownEmulator
