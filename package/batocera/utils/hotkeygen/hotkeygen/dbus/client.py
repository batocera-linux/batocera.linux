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

from typing import TYPE_CHECKING

from dbus_fast import Variant

from batocera_common.dataclasses import cached_dataclass, cached_property
from hotkeygen.dbus.common import DBUS_BUS_NAME, DBUS_PATH
from hotkeygen.dbus.proxies import HotkeygenInterfaceProxy

if TYPE_CHECKING:
    from batocera_common.dbus import Bus
    from hotkeygen._types import HotkeysContext, HotkeysContextMapping


@cached_dataclass
class HotkeygenClient:
    bus: Bus

    @cached_property
    def hotkeygen_proxy(self) -> HotkeygenInterfaceProxy:
        hotkeygen_object = self.bus.get_object(DBUS_BUS_NAME, DBUS_PATH)
        return hotkeygen_object.get_proxy(HotkeygenInterfaceProxy)

    async def set_context(self, context: HotkeysContextMapping, include_common: bool, /) -> None:
        await self.hotkeygen_proxy.set_context(
            context['name'],
            {action: Variant('s' if isinstance(keys, str) else 'as', keys) for action, keys in context['keys'].items()},
            include_common,
        )

    async def set_default_context(self) -> None:
        await self.hotkeygen_proxy.set_default_context()

    async def reload(self) -> None:
        await self.hotkeygen_proxy.reload()

    async def list_config(self) -> None:
        dbus_context, dbus_mappings = await self.hotkeygen_proxy.get_details()

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

    async def reset_mouse_position(self) -> None:
        await self.hotkeygen_proxy.reset_mouse_position()

    async def send_hotkey(self, key: str, delay: int, /) -> None:
        await self.hotkeygen_proxy.send_hotkey(key, delay)

    async def get_system_default_mapping_config(self) -> tuple[dict[str, str], dict[str, str]]:
        return await self.hotkeygen_proxy.get_system_default_mapping_config()

    async def get_device_mapping_config(self) -> dict[str, dict[str, str]]:
        return await self.hotkeygen_proxy.get_device_mapping_config()

    async def set_device_mapping_config(self, filename: str, key: str, action: str, /) -> None:
        await self.hotkeygen_proxy.set_device_mapping_config(filename, key, action)

    async def remove_device_mapping_config(self, filename: str, key: str, /) -> None:
        await self.hotkeygen_proxy.remove_device_mapping_config(filename, key)
