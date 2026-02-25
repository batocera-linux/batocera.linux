from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self, overload

if TYPE_CHECKING:
    from collections.abc import Callable


class cached_property[TValue]:
    __slots__ = ('__doc__', 'func', 'slot_descriptor')

    func: Callable[[Any], TValue]
    slot_descriptor: Any | None

    def __init__(self, func: Callable[[Any], TValue]) -> None:
        self.func = func
        self.slot_descriptor = None
        self.__doc__ = func.__doc__

    @overload
    def __get__(self, instance: None, owner: type[object]) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type[object]) -> TValue: ...

    def __get__(self, instance: object | None, owner: type[object]) -> Self | TValue:
        if instance is None:
            return self

        if self.slot_descriptor is None:
            raise TypeError('cached_property must be used with batocera_launch.dataclasses.cached_dataclass')

        try:
            return self.slot_descriptor.__get__(instance, owner)
        except AttributeError:
            value = self.func(instance)
            self.slot_descriptor.__set__(instance, value)
            return value

    def __delete__(self, instance: object) -> None:
        if self.slot_descriptor is None:
            raise TypeError('cached_property must be used with batocera_launch.dataclasses.cached_dataclass')

        try:
            self.slot_descriptor.__delete__(instance)
        except AttributeError:
            pass
