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
