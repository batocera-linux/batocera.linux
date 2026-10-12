from __future__ import annotations

from typing import Annotated, Final

from dbus_fast import Variant
from dbus_fast.annotations import DBusSignature

DBUS_BUS_NAME: Final = 'org.batocera.Hotkeygen'
DBUS_PATH: Final = '/'

HOTKEYGEN_INTERFACE: Final = 'org.batocera.Hotkeygen'

type DBusContextType = tuple[str, dict[str, Variant]]
type DBusDeviceType = tuple[str, str, str, str]  # device_node, name, filename, full_path
type DBusDeviceMappingType = dict[int, str]
type DBusDeviceMappingsType = list[tuple[DBusDeviceType, tuple[DBusDeviceMappingType, DBusDeviceMappingType]]]

DBusContext = Annotated[DBusContextType, DBusSignature('(sa{sv})')]
DBusDetails = Annotated[
    tuple[DBusContextType, DBusDeviceMappingsType], DBusSignature('((sa{sv})a((ssss)(a{ts}a{ts})))')
]

DBusDeviceMappingConfig = Annotated[dict[str, dict[str, str]], DBusSignature('a{sa{ss}}')]
DBusSystemDefaultMappingConfig = Annotated[tuple[dict[str, str], dict[str, str]], DBusSignature('(a{ss}a{ss})')]
