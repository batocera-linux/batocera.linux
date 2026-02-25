from __future__ import annotations

from typing import TYPE_CHECKING

from .core import Core

if TYPE_CHECKING:
    from .emulator import Libretro


def load_core(emulator: Libretro) -> Core:
    from importlib.metadata import entry_points

    cores = entry_points(group='batocera_launch_libretro.cores')
    core_cls: type[Core] = Core

    if emulator.core in cores.names:
        core_cls = cores[emulator.core].load()

    return core_cls(emulator)
