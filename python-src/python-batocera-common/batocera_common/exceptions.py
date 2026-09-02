from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def flatten_exception_group_iter[E: Exception](group: BaseExceptionGroup[E], /) -> Iterator[E]:
    """Yield leaf exceptions from ``group`` in depth-first order.

    Nested :class:`BaseExceptionGroup` instances are expanded recursively so
    only non-group exceptions are yielded.
    """
    for exception in group.exceptions:
        if isinstance(exception, BaseExceptionGroup):
            yield from flatten_exception_group_iter(exception)
        else:
            yield exception


def flatten_exception_group[E: Exception](group: BaseExceptionGroup[E], /) -> list[E]:
    """Return leaf exceptions from ``group`` as a list in depth-first order.

    Convenience wrapper around :func:`flatten_exception_group_iter`.
    """
    return list(flatten_exception_group_iter(group))
