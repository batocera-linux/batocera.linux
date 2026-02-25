from __future__ import annotations

import asyncio
import logging
import os
import signal
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.paths import BATOCERA_SHARE_DIR
from batocera_launch.asyncio import script_caller
from batocera_launch.config.config import SystemConfig
from batocera_launch.config.metadata import get_games_meta_data
from batocera_launch.devices.controller import Controller
from batocera_launch.devices.evmapy import EvmapyManager
from batocera_launch.devices.gun import Gun
from batocera_launch.devices.hotkeygen import HotkeygenManager
from batocera_launch.devices.mouse import prepare_mouse
from batocera_launch.devices.video import prepare_resolution
from batocera_launch.devices.wheels import configure_wheels
from batocera_launch.exceptions import BaseBatoceraException, BatoceraException
from batocera_launch.load import load_emulator
from batocera_launch.logging import setup_logging
from batocera_launch.paths import ES_GAMES_METADATA

if TYPE_CHECKING:
    from collections.abc import Callable

    from batocera_launch.profiler import Profiler

_logger: Final = logging.getLogger(__name__)
_MAX_PLAYERS: Final = 8


def _thread_task[**P, R](
    task_group: asyncio.TaskGroup, func: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
) -> asyncio.Task[R]:
    return task_group.create_task(asyncio.to_thread(func, *args, **kwargs))


async def _run(args: Namespace, profiler: Profiler, /) -> int:
    system_name: str = args.system
    system_config = SystemConfig.load(args)
    emulator_cls = load_emulator(system_config.emulator)

    async with asyncio.TaskGroup() as task_group:
        controllers_task = _thread_task(task_group, Controller.load_for_players, _MAX_PLAYERS, args)
        guns_task = _thread_task(task_group, Gun.get_and_precalibrate_all, system_config)
        metadata_task = _thread_task(task_group, get_games_meta_data, ES_GAMES_METADATA, system_name, system_config.rom)

    controllers = controllers_task.result()
    guns = guns_task.result()
    metadata = metadata_task.result()

    async with (
        configure_wheels(system_name, system_config, controllers, metadata) as (controllers, wheels),
        prepare_resolution(system_config) as resolution,
    ):
        emulator = emulator_cls.create(
            args,
            system_config,
            metadata,
            controllers,
            guns,
            wheels,
            resolution,
        )
        emulator.saves_path.mkdir(parents=True, exist_ok=True)

        async with prepare_mouse(emulator.needs_mouse):
            # SDL VSync is a big deal on OGA and RPi4
            os.environ.update({'SDL_RENDER_VSYNC': emulator.config.get_bool('vsync', False, return_values=('1', '0'))})

            async with (
                script_caller(('gameStart', 'gameStop'), system_name, emulator.name, emulator.core, emulator.rom),
                EvmapyManager(emulator) as evmapy_manager,
                HotkeygenManager(emulator) as hotkeygen_manager,
                emulator.get_command() as command,
            ):
                # TODO: bezels, gun help, gun borders

                with profiler.pause():
                    await hotkeygen_manager.reset_mouse()
                    async with evmapy_manager.monitor_controllers():
                        try:
                            return await command.run()
                        finally:
                            await asyncio.sleep(
                                1
                            )  # this seems to be required so that the gpu memory is resituated and available for ES


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

        exit_code = 0
        try:
            exit_code = asyncio.run(_run(args, profiler))
        except BaseBatoceraException as e:
            _logger.exception('configgen exception: ')
            exit_code = e.exit_code

            if isinstance(e, BatoceraException):
                Path('/tmp/launch_error.log').write_text(e.args[0])
        except Exception:
            _logger.exception('configgen exception: ')

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
