from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..Command import Command
    from ..config import SystemConfig
    from ..controller import ControllerMapping
    from ..Emulator import Emulator
    from ..gun import Guns
    from ..types import DeviceInfoMapping, HotkeysContext, Resolution


class Generator(metaclass=ABCMeta):
    @abstractmethod
    def generate(
        self,
        system: Emulator,
        rom: str,
        playersControllers: ControllerMapping,
        metadata: Mapping[str, str],
        guns: Guns,
        wheels: DeviceInfoMapping,
        gameResolution: Resolution,
    ) -> Command:
        ...

    def getResolutionMode(self, config: SystemConfig) -> str:
        return config['videomode']

    def getMouseMode(self, config: SystemConfig, rom: str) -> bool:
        return False

    def executionDirectory(self, config: SystemConfig, rom: str) -> str | None:
        return None

    # mame or libretro have internal bezels, don't display the one of mangohud
    def supportsInternalBezels(self) -> bool:
        return False

    # mangohud must be called by the generator itself (wine based emulator for example)
    def hasInternalMangoHUDCall(self) -> bool:
        return False

    def getInGameRatio(self, config: SystemConfig, gameResolution: Resolution, rom: str) -> float:
        # put a default value, but it should be overriden by generators
        return 4/3

    @abstractmethod
    def getHotkeysContext(self) -> HotkeysContext:
        ...
