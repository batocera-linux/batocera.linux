from __future__ import annotations

from typing import TYPE_CHECKING

from .core import Core

if TYPE_CHECKING:
    from .emulator import Libretro


def load_core(emulator: Libretro, /) -> Core:
    from importlib.metadata import entry_points

    cores = entry_points(group='batocera_launch_libretro.cores')
    core_cls: type[Core] = Core

    if emulator.core in cores.names:
        core_cls = cores[emulator.core].load()

    core = core_cls(emulator)

    # Load the `.info` file right away to ensure that the core is installed
    # NOTE: keep this assert here, as it will raise a `MissingCore` exception if
    # the `.info` file is not installed, but we want to load this file early
    assert core.info

    return core
