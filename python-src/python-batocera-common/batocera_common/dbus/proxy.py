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
