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

from batocera_common.platform_profile import (
    PLATFORM_PROFILE_DIR,
    PROFILE_SETTLE_SECONDS,
    current_platform_profile,
    main,
    set_highest_power_profile,
    set_platform_profile,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures('fs')


def _handler(name: str, choices: str, profile: str) -> None:
    handler = PLATFORM_PROFILE_DIR / name
    handler.mkdir(parents=True, exist_ok=True)
    (handler / 'choices').write_text(f'{choices}\n')
    (handler / 'profile').write_text(f'{profile}\n')


def _profile(name: str = 'platform-profile-0') -> str:
    return (PLATFORM_PROFILE_DIR / name / 'profile').read_text().strip()


class TestPlatformProfile:
    def test_nothing_without_a_handler(self) -> None:
        assert current_platform_profile() is None
        assert not set_platform_profile('balanced')

    def test_sets_an_offered_profile(self) -> None:
        _handler('platform-profile-0', 'low-power balanced performance custom', 'custom')

        assert set_platform_profile('balanced')
        assert current_platform_profile() == 'balanced'

    def test_ignores_a_profile_not_offered(self) -> None:
        _handler('platform-profile-0', 'low-power balanced performance', 'balanced')

        assert not set_platform_profile('quiet')
        assert _profile() == 'balanced'

    def test_unchanged_when_already_set(self) -> None:
        _handler('platform-profile-0', 'low-power balanced performance', 'balanced')

        assert not set_platform_profile('balanced')

    def test_sets_every_handler_offering_it(self) -> None:
        _handler('platform-profile-0', 'low-power balanced performance', 'balanced')
        _handler('platform-profile-1', 'quiet balanced performance', 'quiet')

        assert set_platform_profile('performance')
        assert {_profile('platform-profile-0'), _profile('platform-profile-1')} == {'performance'}

    @pytest.mark.parametrize(
        ('choices', 'expected'),
        [
            ('low-power balanced performance custom', 'custom'),
            ('quiet balanced max-power performance', 'max-power'),
            ('low-power balanced performance', 'performance'),
            ('low-power balanced', 'balanced'),
        ],
    )
    def test_highest_power_profile(self, choices: str, expected: str) -> None:
        _handler('platform-profile-0', choices, 'balanced')

        set_highest_power_profile()

        assert _profile() == expected


class TestMain:
    @pytest.fixture
    def run_main(self, mocker: MockerFixture) -> Callable[..., None]:
        def _run(*argv: str) -> None:
            mocker.patch('sys.argv', ['batocera-platform-profile', *argv])
            main()

        return _run

    def test_max_prints_the_previous_profile_and_waits(
        self, run_main: Callable[..., None], capsys: pytest.CaptureFixture[str], mocker: MockerFixture
    ) -> None:
        sleep = mocker.patch('batocera_common.platform_profile.time.sleep')
        _handler('platform-profile-0', 'low-power balanced performance custom', 'balanced')

        run_main('max')

        assert capsys.readouterr().out == 'balanced\n'
        assert _profile() == 'custom'
        sleep.assert_called_once_with(PROFILE_SETTLE_SECONDS)

    def test_max_does_not_wait_when_unchanged(self, run_main: Callable[..., None], mocker: MockerFixture) -> None:
        sleep = mocker.patch('batocera_common.platform_profile.time.sleep')
        _handler('platform-profile-0', 'low-power balanced performance custom', 'custom')

        run_main('max')

        sleep.assert_not_called()

    def test_set_waits_for_the_firmware(self, run_main: Callable[..., None], mocker: MockerFixture) -> None:
        sleep = mocker.patch('batocera_common.platform_profile.time.sleep')
        _handler('platform-profile-0', 'low-power balanced performance custom', 'custom')

        run_main('set', 'low-power')

        assert _profile() == 'low-power'
        sleep.assert_called_once_with(PROFILE_SETTLE_SECONDS)

    def test_set_empty_is_a_no_op(self, run_main: Callable[..., None], mocker: MockerFixture) -> None:
        sleep = mocker.patch('batocera_common.platform_profile.time.sleep')
        _handler('platform-profile-0', 'low-power balanced performance custom', 'custom')

        run_main('set', '')

        assert _profile() == 'custom'
        sleep.assert_not_called()

    def test_list_merges_every_handler(self, run_main: Callable[..., None], capsys: pytest.CaptureFixture[str]) -> None:
        _handler('platform-profile-0', 'low-power balanced performance custom', 'custom')
        _handler('platform-profile-1', 'quiet balanced', 'balanced')

        run_main('list')

        assert capsys.readouterr().out == 'balanced custom low-power performance quiet\n'

    def test_list_without_a_handler(self, run_main: Callable[..., None], capsys: pytest.CaptureFixture[str]) -> None:
        run_main('list')

        assert capsys.readouterr().out == '\n'

    def test_usage(self, run_main: Callable[..., None]) -> None:
        with pytest.raises(SystemExit):
            run_main('bogus')
