from __future__ import annotations

import asyncio
import logging
import os
import signal
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, cast

from batocera_launch.exceptions import BadCommandLineArguments

if TYPE_CHECKING:
    from collections.abc import MutableMapping, MutableSequence
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)


@dataclass(slots=True)
class Command:
    args: MutableSequence[str | Path]
    env: MutableMapping[str, str | Path] = field(default_factory=cast('type[MutableMapping[str, str | Path]]', dict))

    def __post_init__(self) -> None:
        self.args = list(self.args)
        self.env = dict(self.env)

    def update_env(self, **kwargs: str | Path) -> None:
        self.env.update(kwargs)

    def prepend_args(self, *args: str | Path) -> None:
        self.args = [*args, *self.args]

    async def run(self) -> int:
        env: dict[str, str | Path] = os.environ | self.env

        _logger.debug('args: %s', self.args)
        _logger.debug('env: %s', self.env)

        if not self.args:
            raise BadCommandLineArguments

        proc = await asyncio.create_subprocess_exec(
            *self.args,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        def signal_handler() -> None:
            _logger.debug('Killing process')
            proc.kill()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, signal_handler)

        # TODO: stream stdout and stderr to logging, etc.

        try:
            return await proc.wait()
        finally:
            loop.remove_signal_handler(signal.SIGINT)
