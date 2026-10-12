# ruff: ignore[missing-required-import]

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
