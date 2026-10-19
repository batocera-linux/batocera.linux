# ruff: ignore[missing-required-import]

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

# NOTE: in order for dbus_fast to properly introspect the annotations
# this file CANNOT use `from __future__ import annotations`

from typing import Annotated, Protocol

from dbus_fast import Variant
from dbus_fast.annotations import DBusBool, DBusSignature, DBusStr, DBusUInt64

from batocera_common.dbus import DBusInterface, dbus_interface, dbus_method, dbus_property

from .common import (
    HOTKEYGEN_INTERFACE,
    DBusContext,
    DBusDetails,
    DBusDeviceMappingConfig,
    DBusSystemDefaultMappingConfig,
)

DBusKeysDict = Annotated[dict[str, Variant], DBusSignature('a{sv}')]


@dbus_interface(HOTKEYGEN_INTERFACE)
class HotkeygenInterface(DBusInterface, Protocol):
    @property
    @dbus_property(name='Context')
    def dbus_context(self) -> DBusContext: ...

    @dbus_method(name='SetContext')
    def set_context(self, name: DBusStr, keys: DBusKeysDict, include_common: DBusBool, /) -> None: ...
    @dbus_method(name='SetDefaultContext')
    def set_default_context(self) -> None: ...
    @dbus_method(name='GetDetails')
    def get_details(self) -> DBusDetails: ...
    @dbus_method(name='Reload')
    def reload(self) -> None: ...

    @dbus_method(name='ResetMousePosition')
    async def reset_mouse_position(self) -> None: ...

    @dbus_method(name='SendHotkey')
    async def send_hotkey(self, key: DBusStr, delay: DBusUInt64, /) -> None: ...

    @dbus_method(name='GetSystemDefaultMappingConfig')
    def get_system_default_mapping_config(self) -> DBusSystemDefaultMappingConfig: ...
    @dbus_method(name='GetDeviceMappingConfig')
    def get_device_mapping_config(self) -> DBusDeviceMappingConfig: ...
    @dbus_method(name='SetDeviceMappingConfig')
    def set_device_mapping_config(self, filename: DBusStr, key: DBusStr, action: DBusStr, /) -> None: ...
    @dbus_method(name='RemoveDeviceMappingConfig')
    def remove_device_mapping_config(self, filename: DBusStr, key: DBusStr, /) -> None: ...
