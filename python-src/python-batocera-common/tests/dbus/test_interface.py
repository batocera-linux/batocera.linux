from __future__ import annotations

from typing import Protocol

import pytest

from batocera_common.dbus.interface import (
    DBusInterface,
    dbus_interface,
    dbus_method,
    dbus_property,
    get_dbus_method_info,
    get_dbus_property_info,
    get_interface_name,
    iterate_dbus_methods,
    iterate_dbus_properties,
)


@dbus_interface('com.example.Thing')
class ThingInterface(DBusInterface, Protocol):
    @property
    @dbus_property(name='SomeProperty')
    def some_property(self) -> str: ...

    @property
    @dbus_property
    def another_property(self) -> str: ...

    @dbus_method(name='GetValue')
    async def get_value(self) -> int: ...

    @dbus_method
    def do_something(self) -> None: ...

    @property
    def not_a_dbus_property(self) -> str: ...

    def not_a_dbus_method(self) -> None: ...


class TestInterface:
    def test_interface_name(self) -> None:
        assert get_interface_name(ThingInterface) == 'com.example.Thing'

    def test_interface_name_not_decorated(self) -> None:
        class NotDecorated(DBusInterface, Protocol): ...

        with pytest.raises(TypeError, match=r'\.NotDecorated is not decorated with @dbus_interface\(\)$'):
            get_interface_name(NotDecorated)

    def test_interface_not_protocol(self) -> None:
        with pytest.raises(TypeError, match='D-Bus interfaces must be protocols'):

            @dbus_interface('com.example.NotAProtocol')
            class NotAProtocol(DBusInterface): ...

    def test_interface_already_registered(self) -> None:
        with pytest.raises(TypeError, match=r'\.MyThing is already decorated with @dbus_interface\(\)$'):

            @dbus_interface('com.example.MyThing')
            @dbus_interface('com.example.MyOtherThing')
            class MyThing(DBusInterface, Protocol): ...

    def test_interface_methods(self) -> None:
        assert list(iterate_dbus_methods(ThingInterface)) == [
            ('do_something', ThingInterface.do_something),
            ('get_value', ThingInterface.get_value),
        ]
        assert [get_dbus_method_info(method) for _, method in iterate_dbus_methods(ThingInterface)] == [
            {'name': 'do_something'},
            {'name': 'GetValue'},
        ]

    def test_get_method_info_not_decorated(self) -> None:
        with pytest.raises(TypeError, match=r'\.not_a_dbus_method is not decorated with @dbus_method\(\)$'):
            get_dbus_method_info(ThingInterface.not_a_dbus_method)

    def test_interface_properties(self) -> None:
        assert list(iterate_dbus_properties(ThingInterface)) == [
            ('another_property', ThingInterface.another_property),  # pyright: ignore
            ('some_property', ThingInterface.some_property),  # pyright: ignore
        ]
        assert [get_dbus_property_info(method) for _, method in iterate_dbus_properties(ThingInterface)] == [
            {'name': 'another_property'},
            {'name': 'SomeProperty'},
        ]

    def test_get_property_info_not_a_property(self) -> None:
        with pytest.raises(TypeError, match=r'\.not_a_dbus_method is not a property getter$'):
            get_dbus_property_info(ThingInterface.not_a_dbus_method)  # pyright: ignore

    def test_get_property_info_not_decorated(self) -> None:
        with pytest.raises(TypeError, match=r'\.not_a_dbus_property is not decorated with @dbus_property\(\)$'):
            get_dbus_property_info(ThingInterface.not_a_dbus_property)  # pyright: ignore
