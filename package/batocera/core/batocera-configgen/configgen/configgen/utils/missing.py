from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal, overload

# Because `dict.get(key)` returns `None` if there is no key set and the value
# stored in a key can be None, there's no quick way to differentiate between
# a missing key and a key with a value of `None`. `MISSING` is a sentinel
# value that can be used like `None` and will only ever match itself. For
# type checkers, we have to treat `MISSING` as an `Enum` value because Python
# has no native sentinel object and we need a unique value that type checkers
# understand.

if TYPE_CHECKING:
    import enum

    class _MISSING_TYPE(enum.Enum):
        MISSING = enum.auto()

        @overload
        def __eq__(self, other: MissingType) -> Literal[True]:  # pyright: ignore[reportOverlappingOverload]
            ...

        @overload
        def __eq__(self, other: object) -> Literal[False]: ...

        def __eq__(self, other: object) -> bool: ...

        def __lt__(self, other: object) -> Literal[False]: ...

        def __gt__(self, other: object) -> Literal[False]: ...

        def __bool__(self) -> Literal[False]: ...

        def __hash__(self) -> int: ...

        def __repr__(self) -> str: ...

    MISSING: Final = _MISSING_TYPE.MISSING
    type MissingType = Literal[_MISSING_TYPE.MISSING]
else:

    class _MissingSentinel:
        __slots__ = ()

        def __eq__(self, other: object) -> bool:
            return other is self

        def __lt__(self, other: object) -> Literal[False]:
            return False

        def __gt__(self, other: object) -> Literal[False]:
            return False

        def __bool__(self) -> Literal[False]:
            return False

        def __hash__(self) -> int:
            return 0

        def __repr__(self) -> str:
            return '...'

    type MissingType = _MissingSentinel
    MISSING: Final[MissingType] = _MissingSentinel()
