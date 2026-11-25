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

from typing import TYPE_CHECKING

import pytest

from batocera_common.fan import (
    PROFILE_FILE,
    current_fan_profile,
    fan_curve,
    set_fan_profile,
    stop_fan_profile,
    wait_for_fan_check,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures('fake_fs')

CURVE = ['100.0=100', ' 70.0=50', ' 40.0=10', ' 20.0=0']


def test_balanced_keeps_the_curve() -> None:
    assert fan_curve(CURVE, 'balanced') == CURVE


def test_quiet_reaches_each_step_later() -> None:
    assert fan_curve(CURVE, 'quiet') == ['100.0=100', ' 80.0=50', ' 50.0=10', ' 30.0=0']


def test_performance_reaches_each_step_sooner() -> None:
    assert fan_curve(CURVE, 'performance') == [' 90.0=100', ' 60.0=50', ' 30.0=10', ' 10.0=0']


def test_max_always_runs_flat_out() -> None:
    assert fan_curve(CURVE, 'max') == ['0.0=100']


def test_nothing_without_a_fan_daemon() -> None:
    set_fan_profile('max')

    assert not PROFILE_FILE.exists()
    assert current_fan_profile() == 'balanced'


@pytest.mark.parametrize(
    ('profile', 'expected'),
    [
        ('quiet', 'quiet'),
        ('performance', 'performance'),
        ('max', 'max'),
        ('default', 'balanced'),
        ('loud', 'balanced'),
        (None, 'balanced'),
    ],
)
def test_switches_a_running_daemon(profile: str | None, expected: str) -> None:
    PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_FILE.write_text('')

    set_fan_profile(profile)

    assert current_fan_profile() == expected


def test_stopping_the_daemon_removes_the_profile() -> None:
    PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_FILE.write_text('max')

    stop_fan_profile()

    assert not PROFILE_FILE.exists()


class TestWaitForFanCheck:
    @pytest.fixture
    def clock(self, mocker: MockerFixture) -> list[float]:
        now = [0.0]

        def sleep(seconds: float) -> None:
            now[0] += seconds

        mocker.patch('batocera_common.fan.time.monotonic', side_effect=lambda: now[0])
        mocker.patch('batocera_common.fan.time.sleep', side_effect=sleep)
        return now

    def test_waits_the_whole_check(self, clock: list[float]) -> None:
        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROFILE_FILE.write_text('balanced')

        assert not wait_for_fan_check('balanced', 10)
        assert clock[0] == pytest.approx(10)

    def test_a_new_profile_cuts_it_short(self, mocker: MockerFixture, clock: list[float]) -> None:
        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROFILE_FILE.write_text('balanced')

        def sleep(seconds: float) -> None:
            clock[0] += seconds
            if clock[0] >= 2:
                PROFILE_FILE.write_text('max')

        mocker.patch('batocera_common.fan.time.sleep', side_effect=sleep)

        assert wait_for_fan_check('balanced', 10)
        assert clock[0] == pytest.approx(2)
