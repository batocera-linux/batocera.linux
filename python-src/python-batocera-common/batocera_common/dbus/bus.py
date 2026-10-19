# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Self

from dbus_fast import BusType, NameFlag, RequestNameReply
from dbus_fast.aio import MessageBus

from .interface import DBusInterface
from .path import DBusPath
from .proxy import DBusObjectProxy

if TYPE_CHECKING:
    from types import TracebackType

_logger = logging.getLogger(__name__)


class _BusState(Enum):
    NEW = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTING = auto()
    CLOSED = auto()


@dataclass(slots=True)
class Bus:
    """A single-use connection whose lifecycle is controlled by one owner."""

    bus_type: BusType = field(default=BusType.SYSTEM, kw_only=True)

    __message_bus: MessageBus = field(init=False)
    __state: _BusState = field(init=False, default=_BusState.NEW)

    @property
    def connected(self) -> bool:
        return self.__state is _BusState.CONNECTED and self.__message_bus.connected

    @property
    def connecting(self) -> bool:
        return self.__state is _BusState.CONNECTING

    @property
    def disconnecting(self) -> bool:
        return self.__state is _BusState.DISCONNECTING

    def __post_init__(self) -> None:
        self.__message_bus = MessageBus(bus_type=self.bus_type)

    async def request_name(self, name: str) -> None:
        if not self.connected:
            raise RuntimeError('Bus is not connected')

        reply = await self.__message_bus.request_name(name, flags=NameFlag.DO_NOT_QUEUE)

        if reply not in {RequestNameReply.PRIMARY_OWNER, RequestNameReply.ALREADY_OWNER}:
            raise RuntimeError(f'Failed to acquire D-Bus name {name!r}: {reply.name}')

    async def connect(self) -> None:
        if self.connected:
            return

        if self.__state is _BusState.CONNECTED:
            raise RuntimeError('Bus connection was lost; create a new Bus')

        if self.__state is _BusState.CLOSED:
            raise RuntimeError('Bus is closed; create a new Bus')

        if self.__state is not _BusState.NEW:
            raise RuntimeError('Cannot connect while a Bus lifecycle operation is in progress')

        self.__state = _BusState.CONNECTING
        try:
            await self.__message_bus.connect()
        except BaseException:
            self.__state = _BusState.CLOSED
            self.__message_bus.disconnect()
            raise

        self.__state = _BusState.CONNECTED

    async def disconnect(self) -> None:
        if self.connecting or self.disconnecting:
            raise RuntimeError('Cannot disconnect while a Bus lifecycle operation is in progress')

        if self.__state is _BusState.CLOSED:
            return

        was_new = self.__state is _BusState.NEW
        self.__state = _BusState.DISCONNECTING
        try:
            self.__message_bus.disconnect()
            if was_new:
                return

            # Finish cleanup before returning cancellation to the owner.
            shutdown = asyncio.create_task(self.__message_bus.wait_for_disconnect())
            cancellation: asyncio.CancelledError | None = None
            while not shutdown.done():
                try:
                    await asyncio.shield(shutdown)
                except asyncio.CancelledError as error:
                    cancellation = error

            shutdown.result()
            if cancellation is not None:
                raise cancellation
        finally:
            self.__state = _BusState.CLOSED

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
            _logger.exception('Failed to clean up D-Bus during context exit')

    def get_path[I: DBusInterface](self, path: str, interface: type[I], /) -> DBusPath[I]:
        return DBusPath(self.__message_bus, path, interface)

    def get_object(self, bus_name: str, path: str, /) -> DBusObjectProxy:
        return DBusObjectProxy(self.__message_bus, bus_name, path)
