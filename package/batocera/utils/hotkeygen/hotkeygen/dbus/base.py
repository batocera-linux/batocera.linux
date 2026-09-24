from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, Self

from dbus_fast import BusType
from dbus_fast.aio import MessageBus

from batocera_common.dataclasses import cached_dataclass

if TYPE_CHECKING:
    from types import TracebackType


@cached_dataclass
class Base:
    bus: MessageBus = field(init=False)
    __connected: bool = field(init=False, default=False)

    @property
    def connected(self) -> bool:
        return self.__connected

    def __post_init__(self) -> None:
        self.bus = MessageBus(bus_type=BusType.SYSTEM)

    async def connect(self) -> None:
        if not self.connected:
            await self.bus.connect()
            self.__connected = True

    async def disconnect(self) -> None:
        if self.connected:
            self.bus.disconnect()
            await self.bus.wait_for_disconnect()
            self.__connected = False

    async def __aenter__(self) -> Self:
        await self.connect()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        try:
            await self.disconnect()
        except Exception:
            pass
