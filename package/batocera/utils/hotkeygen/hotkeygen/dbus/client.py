from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, cast

from dbus_fast import Variant

from batocera_common.dataclasses import cached_dataclass, cached_property

from .base import Base
from .common import (
    CONFIG_INTERFACE,
    CONTEXT_INTERFACE,
    DBUS_PATH,
    DBUS_SERVICE,
    HOTKEY_INTERFACE,
    MOUSE_INTERFACE,
    DBusDetails,
)

if TYPE_CHECKING:
    from dbus_fast.aio import ProxyInterface, ProxyObject
    from dbus_fast.introspection import Node

    from .._types import HotkeysContext, HotkeysContextMapping


@cached_dataclass
class Client(Base):
    introspection: Node = field(init=False)

    async def connect(self) -> None:
        await super().connect()

        self.introspection = await self.bus.introspect(DBUS_SERVICE, DBUS_PATH)

    @cached_property
    def proxy(self) -> ProxyObject:
        return self.bus.get_proxy_object(DBUS_SERVICE, DBUS_PATH, self.introspection)

    @cached_property
    def context_interface(self) -> ProxyInterface:
        return self.proxy.get_interface(CONTEXT_INTERFACE)

    @cached_property
    def mouse_interface(self) -> ProxyInterface:
        return self.proxy.get_interface(MOUSE_INTERFACE)

    @cached_property
    def hotkey_interface(self) -> ProxyInterface:
        return self.proxy.get_interface(HOTKEY_INTERFACE)

    @cached_property
    def config_interface(self) -> ProxyInterface:
        return self.proxy.get_interface(CONFIG_INTERFACE)

    async def set_context(self, context: HotkeysContextMapping, include_common: bool, /) -> None:
        await self.context_interface.call_set_context(  # pyright: ignore
            context['name'],
            {action: Variant('s' if isinstance(keys, str) else 'as', keys) for action, keys in context['keys'].items()},
            include_common,
        )

    async def set_default_context(self) -> None:
        await self.context_interface.call_set_default_context()  # pyright: ignore

    async def reload(self) -> None:
        await self.context_interface.call_reload()  # pyright: ignore

    async def list_config(self) -> None:
        dbus_context, dbus_mappings = cast('DBusDetails', await self.context_interface.call_get_details())  # pyright: ignore

        context: HotkeysContext = {
            'name': dbus_context[0],
            'keys': {action: key.value for action, key in dbus_context[1].items()},
        }
        mappings = dict(dbus_mappings)

        from ..utils import print_context, print_mapping

        if context['name']:
            print_context(context)

        for (device_node, name, filename, full_path), (mapping, associations) in mappings.items():
            if full_path:
                print(f'# device {device_node} [{name}] ({full_path})')
            else:
                print(f'# device {device_node} [{name}] (no {filename} file found)')

            if associations:
                print_mapping(mapping, associations, context)

    async def reset_mouse(self) -> None:
        await self.mouse_interface.call_reset()  # pyright: ignore

    async def send_hotkey(self, key: str, delay: int, /) -> None:
        await self.hotkey_interface.call_send(key, delay)  # pyright: ignore

    async def get_system_default_mapping_config(self) -> tuple[dict[str, str], dict[str, str]]:
        return await self.config_interface.call_get_system_default_mapping_config()  # pyright: ignore

    async def get_device_mapping_config(self) -> dict[str, dict[str, str]]:
        return await self.config_interface.call_get_device_mapping_config()  # pyright: ignore

    async def set_device_mapping_config(self, filename: str, key: str, action: str, /) -> None:
        await self.config_interface.call_set_device_mapping_config(filename, key, action)  # pyright: ignore

    async def remove_device_mapping_config(self, filename: str, key: str, /) -> None:
        await self.config_interface.call_remove_device_mapping_config(filename, key)  # pyright: ignore
