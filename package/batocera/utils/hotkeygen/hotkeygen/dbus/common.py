from __future__ import annotations

from typing import Annotated, Final

from dbus_fast import Variant
from dbus_fast.annotations import DBusSignature

DBUS_SERVICE: Final = 'org.batocera.Hotkeygen'
DBUS_PATH: Final = '/org/batocera/Hotkeygen'

CONTEXT_INTERFACE: Final = 'org.batocera.Hotkeygen.Context'
MOUSE_INTERFACE: Final = 'org.batocera.Hotkeygen.Mouse'
HOTKEY_INTERFACE: Final = 'org.batocera.Hotkeygen.Hotkey'
CONFIG_INTERFACE: Final = 'org.batocera.Hotkeygen.Config'

type DBusContextType = tuple[str, dict[str, Variant]]
type DBusDeviceType = tuple[str, str, str, str]  # device_node, name, filename, full_path
type DBusDeviceMappingType = dict[int, str]
type DBusDeviceMappingsType = list[tuple[DBusDeviceType, tuple[DBusDeviceMappingType, DBusDeviceMappingType]]]

DBusDetails = Annotated[
    tuple[DBusContextType, DBusDeviceMappingsType], DBusSignature('((sa{sv})a((ssss)(a{ts}a{ts})))')
]

DBusDeviceMappingConfig = Annotated[dict[str, dict[str, str]], DBusSignature('a{sa{ss}}')]
DBusSystemDefaultMappingConfig = Annotated[tuple[dict[str, str], dict[str, str]], DBusSignature('(a{ss}a{ss})')]
