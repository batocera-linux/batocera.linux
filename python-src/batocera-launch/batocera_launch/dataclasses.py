from __future__ import annotations

from dataclasses import Field, dataclass as _stdlib_dataclass, field
from typing import TYPE_CHECKING, Any, dataclass_transform, overload

from .functools import cached_property

if TYPE_CHECKING:
    from collections.abc import Callable


@overload
def cached_dataclass[T](
    cls: type[T],
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    weakref_slot: bool = False,
) -> type[T]: ...


@overload
def cached_dataclass[T](
    cls: None = None,
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    weakref_slot: bool = False,
) -> Callable[[type[T]], type[T]]: ...


@dataclass_transform(field_specifiers=(field, Field))
def cached_dataclass[T](
    cls: type[T] | None = None,
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    weakref_slot: bool = False,
) -> type[T] | Callable[[type[T]], type[T]]:
    def wrap(cls: type[T]) -> type[T]:
        cached_props: dict[str, cached_property[Any]] = {}

        for key, value in list(vars(cls).items()):
            if isinstance(value, cached_property):
                cached_props[key] = value
                setattr(cls, key, field(init=False, repr=False, compare=False))

        if cached_props:
            for key in cached_props:
                cls.__annotations__[key] = object

        new_cls = _stdlib_dataclass(
            cls,
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,
            match_args=match_args,
            kw_only=kw_only,
            slots=True,
            weakref_slot=weakref_slot,
        )

        for key, cached_prop in cached_props.items():
            descriptor = new_cls.__dict__.get(key)

            if descriptor is None:
                # If we're overriding a parent property, no slot is created for it
                # in the subclass, so we need to get the descriptor from the parent class
                descriptor = getattr(new_cls, key)

            if isinstance(descriptor, cached_property):
                # If the descriptor is a cached property from the parent class, we have
                # to get the slot descriptor from the parent class, since the subclass
                # doesn't have one
                descriptor = descriptor.slot_descriptor

            cached_prop.slot_descriptor = descriptor
            setattr(new_cls, key, cached_prop)

        return new_cls

    if cls is None:
        return wrap

    return wrap(cls)
