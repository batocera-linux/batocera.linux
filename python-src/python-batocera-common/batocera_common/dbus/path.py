from __future__ import annotations

import inspect
from dataclasses import dataclass
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from dbus_fast import PropertyAccess
from dbus_fast.service import (
    ServiceInterface,
    dbus_method as _dbus_fast_dbus_method,
    dbus_property as _dbus_fast_dbus_property,
)

from .interface import (
    DBusInterface,
    get_dbus_method_info,
    get_dbus_property_info,
    get_interface_name,
    iterate_dbus_methods,
    iterate_dbus_properties,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from dbus_fast.aio import MessageBus


def _async_wrapper(func: Callable[..., Any], /) -> Callable[..., Any]:
    async def wrapper(interface: ServiceInterface, *args: object, **kwargs: object) -> Any:
        return await func(*args, **kwargs)

    return wrapper


def _sync_wrapper(func: Callable[..., Any], /) -> Callable[..., Any]:
    def wrapper(interface: ServiceInterface, *args: object, **kwargs: object) -> Any:
        return func(*args, **kwargs)

    return wrapper


def _create_dbus_method_wrapper(
    protocol_definition: Callable[..., object], method: Callable[..., object], /
) -> Callable[..., object]:
    dbus_method_info = get_dbus_method_info(protocol_definition)
    service_method = _dbus_fast_dbus_method(name=dbus_method_info['name'])(protocol_definition)

    if inspect.iscoroutinefunction(protocol_definition):
        wrapper = _async_wrapper(method)
    else:
        wrapper = _sync_wrapper(method)

    getattr(service_method, '__DBUS_METHOD').fn = wrapper

    return service_method


def _create_dbus_property_wrapper(protocol_definition: property, instance: object, /) -> property:
    protocol_getter = getattr(protocol_definition, 'fget', None)

    if protocol_getter is None:
        raise TypeError(f'{cast("Any", protocol_getter).__qualname__} is not a property getter')

    prop_name = protocol_definition.__name__

    if inspect.iscoroutinefunction(protocol_getter):
        raise TypeError(f'{protocol_definition.__name__}: async property getters are unsupported')

    info = get_dbus_property_info(protocol_definition)

    @wraps(protocol_getter)
    def getter(interface: ServiceInterface) -> Any:
        return getattr(instance, prop_name)

    getter.__name__ = prop_name

    descriptor = _dbus_fast_dbus_property(
        name=info['name'],
        access=(PropertyAccess.READ if protocol_definition.fset is None else PropertyAccess.READWRITE),
    )(getter)

    if protocol_definition.fset is not None:
        if inspect.iscoroutinefunction(protocol_definition.fset):
            raise TypeError(f'{prop_name}: async property setters are unsupported')

        @wraps(protocol_definition.fset)
        def setter(interface: ServiceInterface, value: Any) -> None:
            setattr(instance, prop_name, value)

        setter.__name__ = prop_name
        descriptor = descriptor.setter(setter)

    return descriptor


@dataclass(slots=True, frozen=True)
class DBusPath[I: DBusInterface]:
    _dbus_bus: MessageBus
    _dbus_path: str
    _dbus_interface: type[I]

    def export(self, obj: I, /) -> None:
        attrs: dict[str, object] = {}

        for member, interface_member in iterate_dbus_methods(self._dbus_interface):
            object_member = getattr(obj, member, None)

            if not callable(object_member):
                raise RuntimeError(
                    f'Object {obj!r} does not implement method {member!r} of interface {self._dbus_interface.__name__!r}'
                )

            attrs[member] = _create_dbus_method_wrapper(interface_member, object_member)

        for member, definition in iterate_dbus_properties(self._dbus_interface):
            inspect.getattr_static(obj, member)  # Check without invoking the getter.
            attrs[member] = _create_dbus_property_wrapper(definition, obj)

        service_cls = type(f'{obj.__class__.__name__}_{self._dbus_interface.__name__}', (ServiceInterface,), attrs)

        self._dbus_bus.export(self._dbus_path, service_cls(get_interface_name(self._dbus_interface)))
