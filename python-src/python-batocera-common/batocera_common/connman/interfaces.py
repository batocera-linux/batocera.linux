# ruff: ignore[missing-required-import]

# NOTE: in order for dbus_fast to properly introspect the annotations
# this file CANNOT use `from __future__ import annotations`

from typing import Annotated, Protocol

from dbus_fast import Variant
from dbus_fast.annotations import DBusSignature

from batocera_common.dbus import DBusInterface, dbus_interface, dbus_method

ConnmanProperties = Annotated[dict[str, Variant], DBusSignature('a{sv}')]


@dbus_interface('net.connman.Manager')
class ConnmanManagerInterface(DBusInterface, Protocol):
    @dbus_method(name='GetProperties')
    def get_properties(self) -> ConnmanProperties: ...
