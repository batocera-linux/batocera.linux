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

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Protocol,
    TypedDict,
    cast,
    get_protocol_members,
    is_protocol,
    overload,
)
from typing_extensions import TypeForm
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class DBusMethodInfo(TypedDict):
    name: str


class DBusPropertyInfo(TypedDict):
    name: str


class DBusInterface(Protocol): ...


_INTERFACE_NAME_REGISTRY: Final = WeakKeyDictionary[TypeForm[DBusInterface], str]()


def dbus_interface[I: DBusInterface](name: str, /) -> Callable[[type[I]], type[I]]:
    def decorator(interface: type[I], /) -> type[I]:
        if not is_protocol(interface):
            raise TypeError('D-Bus interfaces must be protocols')

        if interface in _INTERFACE_NAME_REGISTRY:
            raise TypeError(f'{interface.__qualname__} is already decorated with @dbus_interface()')

        _INTERFACE_NAME_REGISTRY[interface] = name

        return interface

    return decorator


def get_interface_name(interface: type[object], /) -> str:
    try:
        return _INTERFACE_NAME_REGISTRY[interface]
    except KeyError:
        raise TypeError(f'{interface.__qualname__} is not decorated with @dbus_interface()') from None


@overload
def dbus_method[**P, R](
    method: None = None,
    /,
    *,
    name: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
@overload
def dbus_method[**P, R](
    method: Callable[P, R],
    /,
    *,
    name: str | None = None,
) -> Callable[P, R]: ...


def dbus_method[**P, R](
    method: Callable[P, R] | None = None,
    /,
    *,
    name: str | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R], /) -> Callable[P, R]:
        info: DBusMethodInfo = {
            'name': name or func.__name__,
        }
        setattr(func, '__DBUS_METHOD_INFO', info)

        return func

    if method is None:
        return decorator

    return decorator(method)


def get_dbus_method_info(method: Callable[..., Any], /) -> DBusMethodInfo:
    info = getattr(method, '__DBUS_METHOD_INFO', None)

    if info is None:
        raise TypeError(f'{method.__qualname__} is not decorated with @dbus_method()')

    return info


def iterate_dbus_methods(interface: TypeForm[DBusInterface], /) -> Iterator[tuple[str, Callable[..., Any]]]:
    for name in sorted(get_protocol_members(cast('type[object]', interface))):
        member = getattr(interface, name, None)

        if callable(member):
            try:
                get_dbus_method_info(member)  # Raises TypeError if not a D-Bus method
                yield name, member
            except TypeError:
                pass


@overload
def dbus_property[C: Callable[..., Any]](
    method: None = None,
    /,
    *,
    name: str | None = None,
) -> Callable[[C], C]: ...
@overload
def dbus_property[C: Callable[..., Any]](
    method: C,
    /,
    *,
    name: str | None = None,
) -> C: ...


def dbus_property[C: Callable[..., Any]](
    method: C | None = None,
    /,
    *,
    name: str | None = None,
) -> C | Callable[[C], C]:
    def decorator(getter: C, /) -> C:
        info: DBusPropertyInfo = {
            'name': name or getter.__name__,
        }
        setattr(getter, '__DBUS_PROPERTY_INFO', info)
        return getter

    if method is None:
        return decorator

    return decorator(method)


def get_dbus_property_info(prop: property, /) -> DBusPropertyInfo:
    getter = getattr(prop, 'fget', None)

    if getter is None:
        raise TypeError(f'{cast("Any", prop).__qualname__} is not a property getter')

    info = getattr(getter, '__DBUS_PROPERTY_INFO', None)

    if info is None:
        raise TypeError(f'{getter.__qualname__} is not decorated with @dbus_property()')

    return info


def iterate_dbus_properties(interface: TypeForm[DBusInterface], /) -> Iterator[tuple[str, property]]:
    for name in sorted(get_protocol_members(cast('type[object]', interface))):
        member = inspect.getattr_static(interface, name)

        if isinstance(member, property):
            try:
                get_dbus_property_info(member)  # Raises TypeError if not a D-Bus property
                yield member.__name__, member
            except TypeError:
                pass
