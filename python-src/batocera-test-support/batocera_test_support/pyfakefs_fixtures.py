from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType


@pytest.fixture
def fakefs_modules_to_reload() -> list[ModuleType] | None:
    return
