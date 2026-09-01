from __future__ import annotations

import logging
import signal
import time
from pathlib import Path
from typing import TYPE_CHECKING, Final

import uvloop

from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BATOCERA_CONF, BATOCERA_SHARE_DIR

from .exceptions import BaseBatoceraException, BatoceraException

if TYPE_CHECKING:
    from .cli.arguments import Arguments
    from .profiler import Profiler

_logger: Final = logging.getLogger(__name__)


async def _run(args: Arguments, profiler: Profiler, /) -> int:
    from .emulator import Emulator

    async with Emulator.create(args, profiler) as emulator:
        return await emulator.run()


def _run_legacy(args: Arguments, profiler: Profiler, /) -> int:
    from configgen.emulatorlauncher import main  # pyright: ignore

    return main(args, profiler)


def launch(args: Arguments, profiler: Profiler, /) -> None:
    batocera_version = 'UNKNOWN'
    if (version_file := BATOCERA_SHARE_DIR / 'batocera.version').exists():
        batocera_version = version_file.read_text().strip()

    _logger.info('Batocera version: %s', batocera_version)
    _logger.debug('Arguments: %s', args)

    exit_code = 0
    try:
        config = KeyValueConfig()
        config.read(BATOCERA_CONF)

        if config.get('configgen') == '1':
            _logger.debug('Using legacy configgen')
            exit_code = _run_legacy(args, profiler)
        else:
            exit_code = uvloop.run(_run(args, profiler))
    except BaseBatoceraException as e:
        _logger.exception('batocera-launch exception')
        exit_code = e.exit_code

        if isinstance(e, BatoceraException):
            Path('/tmp/launch_error.log').write_text(e.args[0])
    except Exception:
        _logger.exception('batocera-launch exception')

    # this seems to be required so that the gpu memory is resituated and available for ES
    time.sleep(1)

    if exit_code < 0:
        signal_number = exit_code * -1

        if signal_number < signal.NSIG:
            signal_description = signal.strsignal(signal_number)

            if signal_description and ':' not in signal_description:
                signal_description = f'{signal_description}: {signal_number}'

            _logger.debug('Emulator terminated by signal (%s)', signal_description)
            exit_code = 0

    _logger.debug('Exiting batocera-launch with status %s', exit_code)

    exit(exit_code)
