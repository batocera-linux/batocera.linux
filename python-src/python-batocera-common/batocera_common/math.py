from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison


def clamp[T: SupportsRichComparison](value: T, lower: T, upper: T, /) -> T:
    """Clamp a value between a lower and upper bound."""

    return min(max(lower, value), upper)
