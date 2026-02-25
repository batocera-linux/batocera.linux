from __future__ import annotations

import asyncio
import logging
import os
import signal
import time
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.paths import BATOCERA_SHARE_DIR

from .asyncio import script_caller
from .config.config import SystemConfig
from .devices.evmapy import EvmapyManager
from .devices.hotkeygen import HotkeygenManager, reset_mouse as _hotkeygen_reset_mouse
from .devices.mouse import prepare_mouse
from .devices.video import list_outputs
from .exceptions import BaseBatoceraException, BatoceraException
from .load import load_emulator
from .logging import setup_logging

if TYPE_CHECKING:
    from .profiler import Profiler

_logger: Final = logging.getLogger(__name__)
_MAX_PLAYERS: Final = 8


async def _run(args: Namespace, profiler: Profiler, /) -> int:
    system_config = SystemConfig.load(args)
    emulator_cls = load_emulator(system_config.emulator)

    async with emulator_cls.prepare_emulator(args, _MAX_PLAYERS) as emulator:
        outputs = await list_outputs(timeout=3)

        if len(outputs) > 1:
            _logger.debug('Multiple displays detected (%s). Resetting mouse to primary display.', ', '.join(outputs))
            await _hotkeygen_reset_mouse()
        else:
            _logger.debug(
                'Single display detected (%s). Skipping mouse reset to keep cursor hidden',
                ', '.join(outputs) if outputs else 'default',
            )

        async with prepare_mouse(emulator.needs_mouse):
            # SDL VSync is a big deal on OGA and RPi4
            os.environ.update(
                {'SDL_RENDER_VSYNC': emulator.config.get_bool('sdlvsync', True, return_values=('1', '0'))}
            )

            async with (
                script_caller(('gameStart', 'gameStop'), emulator.system, emulator.name, emulator.core, emulator.rom),
                EvmapyManager(emulator) as evmapy_manager,
                HotkeygenManager(emulator),
                emulator.get_command() as command,
            ):
                with profiler.pause():
                    async with evmapy_manager.monitor_controllers():
                        return await command.run()


def launch(profiler: Profiler, /) -> None:
    with setup_logging():
        batocera_version = 'UNKNOWN'
        if (version_file := BATOCERA_SHARE_DIR / 'batocera.version').exists():
            batocera_version = version_file.read_text().strip()

        _logger.info('Batocera version: %s', batocera_version)

        parser = ArgumentParser()

        for p in range(1, _MAX_PLAYERS + 1):
            parser.add_argument(f'-p{p}index', help=f'player{p} controller index', type=int, required=False)
            parser.add_argument(f'-p{p}guid', help=f'player{p} controller SDL2 guid', type=str, required=False)
            parser.add_argument(f'-p{p}name', help=f'player{p} controller name', type=str, required=False)
            parser.add_argument(f'-p{p}devicepath', help=f'player{p} controller device', type=str, required=False)
            parser.add_argument(
                f'-p{p}nbbuttons', help=f'player{p} controller number of buttons', type=int, required=False
            )
            parser.add_argument(f'-p{p}nbhats', help=f'player{p} controller number of hats', type=int, required=False)
            parser.add_argument(f'-p{p}nbaxes', help=f'player{p} controller number of axes', type=int, required=False)

        parser.add_argument('-system', help='select the system to launch', type=str, required=True)
        parser.add_argument('-rom', help='rom absolute path', type=Path, required=True)
        parser.add_argument('-emulator', help='force emulator', type=str, required=False)
        parser.add_argument('-core', help='force emulator core', type=str, required=False)
        parser.add_argument('-netplaymode', help='host/client', type=str, required=False)
        parser.add_argument('-netplaypass', help='enable spectator mode', type=str, required=False)
        parser.add_argument('-netplayip', help='remote ip', type=str, required=False)
        parser.add_argument('-netplayport', help='remote port', type=str, required=False)
        parser.add_argument('-netplaysession', help='netplay session', type=str, required=False)
        parser.add_argument('-state_slot', help='state slot', type=str, required=False)
        parser.add_argument('-state_filename', help='state filename', type=str, required=False)
        parser.add_argument('-autosave', help='autosave', type=str, required=False)
        parser.add_argument('-systemname', help='system fancy name', type=str, required=False)
        parser.add_argument(
            '-gameinfoxml', help='game info xml', type=Path, nargs='?', default=Path('/dev/null'), required=False
        )
        parser.add_argument('-lightgun', help='configure lightguns', action='store_true')
        parser.add_argument('-wheel', help='configure wheel', action='store_true')
        parser.add_argument('-trackball', help='configure trackball', action='store_true')
        parser.add_argument('-spinner', help='configure spinner', action='store_true')

        args = parser.parse_args()

        _logger.debug('arguments: %s', args)

        exit_code = 0
        try:
            exit_code = asyncio.run(_run(args, profiler))
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

        _logger.debug('Exiting configgen with status %s', exit_code)

        exit(exit_code)
