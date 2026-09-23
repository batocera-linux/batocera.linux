from __future__ import annotations

from typing import TYPE_CHECKING

from dbus_fast import Variant

from batocera_common.dataclasses import cached_dataclass, cached_property
from hotkeygen.dbus.client_interfaces import (
    ClientConfigInterace,
    ClientContextInterface,
    ClientHotkeyInterface,
    ClientMouseInterface,
)

from .base import Base

if TYPE_CHECKING:
    from .._types import HotkeysContext, HotkeysContextMapping


@cached_dataclass
class Client(Base):
    @cached_property
    def context_interface(self) -> ClientContextInterface:
        return ClientContextInterface(self.bus)

    @cached_property
    def mouse_interface(self) -> ClientMouseInterface:
        return ClientMouseInterface(self.bus)

    @cached_property
    def hotkey_interface(self) -> ClientHotkeyInterface:
        return ClientHotkeyInterface(self.bus)

    @cached_property
    def config_interface(self) -> ClientConfigInterace:
        return ClientConfigInterace(self.bus)

    async def set_context(self, context: HotkeysContextMapping, include_common: bool, /) -> None:
        await self.context_interface.set_context(
            context['name'],
            {action: Variant('s' if isinstance(keys, str) else 'as', keys) for action, keys in context['keys'].items()},
            include_common,
        )

    async def set_default_context(self) -> None:
        await self.context_interface.set_default_context()

    async def reload(self) -> None:
        await self.context_interface.reload()

    async def list_config(self) -> None:
        dbus_context, dbus_mappings = await self.context_interface.get_details()

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
        await self.mouse_interface.reset()

    async def send_hotkey(self, key: str, delay: int, /) -> None:
        await self.hotkey_interface.send(key, delay)

    async def get_system_default_mapping_config(self) -> tuple[dict[str, str], dict[str, str]]:
        return await self.config_interface.get_system_default_mapping_config()

    async def get_device_mapping_config(self) -> dict[str, dict[str, str]]:
        return await self.config_interface.get_device_mapping_config()

    async def set_device_mapping_config(self, filename: str, key: str, action: str, /) -> None:
        await self.config_interface.set_device_mapping_config(filename, key, action)

    async def remove_device_mapping_config(self, filename: str, key: str, /) -> None:
        await self.config_interface.remove_device_mapping_config(filename, key)
