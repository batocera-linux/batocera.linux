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

import pytest

from batocera_common.math import clamp


class TestClamp:
    @pytest.mark.parametrize(
        ('value', 'lower', 'upper', 'expected'),
        [
            (5, 0, 10, 5),
            (0, 0, 10, 0),
            (10, 0, 10, 10),
            (-1, 0, 10, 0),
            (11, 0, 10, 10),
            (5, 5, 5, 5),
            (-5, -10, -1, -5),
            (-11, -10, -1, -10),
            (0, -10, -1, -1),
        ],
    )
    def test_integers(self, value: int, lower: int, upper: int, expected: int) -> None:
        assert clamp(value, lower, upper) == expected

    @pytest.mark.parametrize(
        ('value', 'lower', 'upper', 'expected'),
        [
            (0.5, 0.0, 1.0, 0.5),
            (-0.1, 0.0, 1.0, 0.0),
            (1.1, 0.0, 1.0, 1.0),
            (0.0, 0.0, 1.0, 0.0),
            (1.0, 0.0, 1.0, 1.0),
        ],
    )
    def test_floats(self, value: float, lower: float, upper: float, expected: float) -> None:
        assert clamp(value, lower, upper) == expected

    @pytest.mark.parametrize(
        ('value', 'lower', 'upper', 'expected'),
        [
            ('m', 'a', 'z', 'm'),
            ('A', 'a', 'z', 'a'),
            ('{', 'a', 'z', 'z'),
            ('a', 'a', 'z', 'a'),
            ('z', 'a', 'z', 'z'),
        ],
    )
    def test_strings(self, value: str, lower: str, upper: str, expected: str) -> None:
        assert clamp(value, lower, upper) == expected

    def test_equal_bounds(self) -> None:
        assert clamp(42, 42, 42) == 42
        assert clamp(0, 42, 42) == 42
        assert clamp(100, 42, 42) == 42
