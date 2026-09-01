from __future__ import annotations

import asyncio
import logging
import os
import signal
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, cast

from batocera_common.asyncio import env_to_fspath

from .exceptions import BadCommandLineArguments, UnexpectedEmulatorExit

if TYPE_CHECKING:
    from collections.abc import Awaitable, MutableMapping, MutableSequence
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)
_emulator_logger: Final = logging.getLogger('emulator')


async def _log_emulator_output(stream: asyncio.StreamReader, level: int, prefix: str) -> None:
    while line := await stream.readline():
        _emulator_logger.log(level, '%s %s', prefix, line.decode(errors='backslashreplace').rstrip())


@dataclass(slots=True)
class Command:
    args: MutableSequence[str | Path]
    env: MutableMapping[str, str | Path] = field(default_factory=cast('type[MutableMapping[str, str | Path]]', dict))

    # Can be used to wait for something to complete (like background task for downloading a file) before running
    # the command
    wait_for: Awaitable[object] | None = None

    def __post_init__(self) -> None:
        self.args = list(self.args)
        self.env = dict(self.env)

    def update_env(self, **kwargs: str | Path) -> None:
        self.env.update(kwargs)

    def prepend_args(self, *args: str | Path) -> None:
        self.args = [*args, *self.args]

    async def run(self) -> int:
        env: dict[str, str | Path] = os.environ | self.env

        _logger.debug('Running command: %s', ' '.join(map(str, self.args)))
        _logger.debug('Environment variables: %s', self.env)

        if not self.args:
            raise BadCommandLineArguments

        if self.wait_for is not None:
            await self.wait_for

        proc = await asyncio.create_subprocess_exec(
            'nice',
            '-n',
            '-4',
            *self.args,
            env=env_to_fspath(env),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        def _signal_handler() -> None:
            if proc.returncode is None:
                _logger.debug('Killing process')
                proc.kill()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, _signal_handler)

        assert proc.stdout is not None
        assert proc.stderr is not None

        # Set up async tasks to read from stdout and stderr and log the output while the
        # process is running. The tasks continuously read from the streams and log the output
        # until the process terminates or an exception occurs. Since this is done in tasks,
        # this allows the main coroutine to wait for the process to finish while still logging
        # output in real-time.
        stdout_task = asyncio.create_task(_log_emulator_output(proc.stdout, logging.DEBUG, '[stdout]'))
        stderr_task = asyncio.create_task(_log_emulator_output(proc.stderr, logging.ERROR, '[stderr]'))

        reader_tasks = (stdout_task, stderr_task)
        exit_code = 0

        async def _cleanup_process() -> None:
            for task in reader_tasks:
                task.cancel()

            await asyncio.gather(*reader_tasks, return_exceptions=True)

            if proc.returncode is None:
                proc.kill()

            # Reap the process and drain any remaining buffered pipe data.
            await proc.communicate()

        try:
            await asyncio.gather(*reader_tasks)
            exit_code = await proc.wait()
        except BrokenPipeError:
            # Seeing BrokenPipeError? This is probably caused by head truncating output in the front-end
            # Examine es-core/src/platform.cpp::runSystemCommand for additional context
            await _cleanup_process()
        except BaseException as e:
            _logger.error('emulator exited')

            await _cleanup_process()

            raise UnexpectedEmulatorExit from e
        finally:
            loop.remove_signal_handler(signal.SIGINT)

        return exit_code
