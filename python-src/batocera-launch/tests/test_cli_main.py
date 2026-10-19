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

import io
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

from batocera_launch.cli.main import main

if TYPE_CHECKING:
    from collections.abc import Generator

    from pytest_mock import MockerFixture


def test_exits_with_the_launch_code_after_logging_closes_stdout(mocker: MockerFixture) -> None:
    stdout = io.TextIOWrapper(io.BytesIO())

    @contextmanager
    def setup_logging() -> Generator[None]:
        try:
            yield
        finally:
            stdout.close()

    mocker.patch.object(sys, 'stdout', stdout)
    mocker.patch('batocera_launch.cli.main.setup_logging', setup_logging)
    mocker.patch('batocera_launch.cli.main.Arguments.parse')
    mocker.patch('batocera_launch.launch.launch', side_effect=SystemExit(204))
    os_exit = mocker.patch('os._exit')

    main()

    os_exit.assert_called_once_with(204)
