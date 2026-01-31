from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from ..Command import Command
    from ..config import SystemConfig
    from ..controller import Controllers
    from ..Emulator import Emulator
    from ..gun import Guns
    from ..types import DeviceInfoMapping, HotkeysContext, Resolution


class Generator(metaclass=ABCMeta):
    @abstractmethod
    def generate(
        self,
        system: Emulator,
        rom: Path,
        playersControllers: Controllers,
        metadata: Mapping[str, str],
        guns: Guns,
        wheels: DeviceInfoMapping,
        gameResolution: Resolution,
    ) -> Command:
        ...

    def getResolutionMode(self, config: SystemConfig) -> str:
        return config['videomode']

    def getMouseMode(self, config: SystemConfig, rom: Path) -> bool:
        return False

    def executionDirectory(self, config: SystemConfig, rom: Path) -> Path | None:
        return None

    # Some systems expect to write into the ROM area, for example: DOS and Amiga.
    def writesToRom(self) -> bool:
        return False

    # mame or libretro have internal bezels, don't display the one of mangohud
    def supportsInternalBezels(self) -> bool:
        return False

    # mangohud must be called by the generator itself (wine based emulator for example)
    def hasInternalMangoHUDCall(self) -> bool:
        return False

    def getInGameRatio(self, config: SystemConfig, gameResolution: Resolution, rom: Path) -> float:
        # put a default value, but it should be overriden by generators
        return 4/3

    @abstractmethod
    def getHotkeysContext(self) -> HotkeysContext:
        ...
