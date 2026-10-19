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

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
)

from dbus_fast import Message, Variant
from dbus_fast._private.util import replace_idx_with_fds
from dbus_fast.proxy_object import BaseProxyInterface

if TYPE_CHECKING:
    from dbus_fast.aio import MessageBus


@dataclass(slots=True, frozen=True)
class DBusObjectProxy:
    _dbus_bus: MessageBus
    _dbus_bus_name: str
    _dbus_path: str

    def get_proxy[P: DBusProxy](self, proxy_cls: type[P], /) -> P:
        return proxy_cls(self._dbus_bus, self._dbus_bus_name, self._dbus_path)


@dataclass(slots=True, frozen=True)
class DBusProxy:
    __dbus_interface_name__: ClassVar[str]

    _dbus_bus: MessageBus
    _dbus_bus_name: str
    _dbus_path: str

    async def _call_method(
        self,
        method: str,
        signature: str,
        body: list[Any],
        return_signature: str | None,
        /,
        *,
        interface: str | None = None,
    ) -> Any:
        if interface is None:
            interface = self.__dbus_interface_name__

        reply = await self._dbus_bus.call(
            Message(
                destination=self._dbus_bus_name,
                path=self._dbus_path,
                interface=interface,
                member=method,
                signature=signature,
                body=body,
            )
        )

        BaseProxyInterface._check_method_return(reply, return_signature or '')

        body = replace_idx_with_fds(reply.signature_tree, reply.body, reply.unix_fds)

        if not body:
            return None

        if len(body) == 1:
            return body[0]

        return body

    async def _get_property(self, name: str, signature: str, /) -> Any:
        result: Variant = await self._call_method(
            'Get',
            'ss',
            [self.__dbus_interface_name__, name],
            'v',
            interface='org.freedesktop.DBus.Properties',
        )

        if result.signature != signature:
            raise RuntimeError(f'Property {name!r}: expected signature {signature!r}, received {result.signature!r}')

        return result.value

    async def _set_property(
        self,
        name: str,
        signature: str,
        value: Any,
        /,
    ) -> None:
        await self._call_method(
            'Set',
            'ssv',
            [self.__dbus_interface_name__, name, Variant(signature, value)],
            '',
            interface='org.freedesktop.DBus.Properties',
        )
