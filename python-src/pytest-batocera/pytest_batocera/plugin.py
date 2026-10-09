from __future__ import annotations

import os
from collections import ChainMap
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import uvloop
from aiointercept import aiointercept
from pyfakefs import helpers
from pyfakefs.fake_filesystem import FakeFilesystem, OSType
from pyfakefs.fake_filesystem_unittest import Patcher

from batocera_launch.rom import Rom

from .mock_key_value_config import MockKeyValueConfig
from .mock_system_config import MockSystemConfig

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator, Mapping
    from types import ModuleType

    from _pytest.fixtures import SubRequest
    from pytest_asyncio.plugin import LoopFactory
    from pytest_mock import MockerFixture


def pytest_asyncio_loop_factories(config: pytest.Config, item: pytest.Item) -> Mapping[str, LoopFactory]:
    return {
        'uvloop': uvloop.new_event_loop,
    }


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        'markers', 'launch_config_emulator(name): the emulator name for the mock SystemConfig object'
    )
    config.addinivalue_line('markers', 'launch_config_core(name): the core name for the mock SystemConfig object')
    config.addinivalue_line('markers', 'launch_config_system(name): the system name for the mock SystemConfig object')
    config.addinivalue_line(
        'markers', 'launch_config_user_settings(settings): the user settings for the mock SystemConfig object'
    )
    config.addinivalue_line(
        'markers', 'launch_config_system_settings(settings): the system settings for the mock SystemConfig object'
    )
    config.addinivalue_line(
        'markers', 'launch_config_global_settings(settings): the global settings for the mock SystemConfig object'
    )
    config.addinivalue_line(
        'markers', 'launch_config_render_config(renderconfig): the render config for the mock SystemConfig object'
    )
    config.addinivalue_line('markers', 'launch_rom_filename(path): the rom filename for the mock SystemConfig object')
    config.addinivalue_line('markers', 'launch_rom_source(path): the rom source path for the mock SystemConfig object')
    config.addinivalue_line(
        'markers', 'launch_rom_prepared(path): the prepared rom path for the mock SystemConfig object'
    )


@pytest.fixture
def fs_modules_to_reload() -> list[ModuleType] | None:
    return


@pytest.fixture
def fs(fs_modules_to_reload: list[ModuleType] | None, mocker: MockerFixture) -> Iterator[FakeFilesystem]:
    environ = os.environ.copy()

    # delete these so our fake filesystem does not inherit the temporary directory
    # of the machine running the tests
    environ.pop('TMP', None)
    environ.pop('TMPDIR', None)
    environ.pop('TEMP', None)

    with mocker.patch.dict('os.environ', environ, clear=True):
        # batocera runs as root
        helpers.set_uid(0)

        with Patcher(
            additional_skip_names=[
                'syrupy.utils',
                'syrupy.extensions.amber.serializer',
                'syrupy.extensions.image',
                'syrupy.extensions.single_file',
            ],
            modules_to_reload=fs_modules_to_reload,
            allow_root_user=True,
        ) as patcher:
            patcher.fs.os = OSType.LINUX  # pyright: ignore
            yield patcher.fs  # pyright: ignore

        helpers.reset_ids()


@pytest.fixture
async def mock_server() -> AsyncIterator[aiointercept]:
    async with aiointercept(mock_external_urls=True) as m:
        yield m


@pytest.fixture
def launch_config_emulator(request: SubRequest) -> str:
    if (marker := request.node.get_closest_marker('launch_config_emulator')) is not None:
        return marker.args[0]

    return 'unset-emulator'


@pytest.fixture
def launch_config_core(request: SubRequest) -> str | None:
    if (marker := request.node.get_closest_marker('launch_config_core')) is not None:
        return marker.args[0]

    return None


@pytest.fixture
def launch_config_system(request: SubRequest) -> str:
    if (marker := request.node.get_closest_marker('launch_config_system')) is not None:
        return marker.args[0]

    return 'unset-system'


@pytest.fixture
def launch_config_user_settings(request: SubRequest) -> dict[str, str]:
    if (marker := request.node.get_closest_marker('launch_config_user_settings')) is not None:
        return marker.args[0]
    return {}


@pytest.fixture
def launch_config_system_settings(request: SubRequest) -> dict[str, str]:
    if (marker := request.node.get_closest_marker('launch_config_system_settings')) is not None:
        return marker.args[0]

    return {}


@pytest.fixture
def launch_config_global_settings(request: SubRequest) -> dict[str, str]:
    if (marker := request.node.get_closest_marker('launch_config_global_settings')) is not None:
        return marker.args[0]
    return {}


@pytest.fixture
def launch_config_render_config(request: SubRequest) -> dict[str, str]:
    if (marker := request.node.get_closest_marker('launch_config_render_config')) is not None:
        return marker.args[0]

    return {}


@pytest.fixture
def launch_rom_filename(request: SubRequest) -> str:
    marker = request.node.get_closest_marker('launch_rom_source')
    return 'test.rom' if marker is None else marker.args[0]


@pytest.fixture
def launch_rom_source(request: SubRequest, launch_config_system: str, launch_rom_filename: str) -> str:
    marker = request.node.get_closest_marker('launch_rom_source')

    return f'/userdata/roms/{launch_config_system}/{launch_rom_filename}' if marker is None else marker.args[0]


@pytest.fixture
def launch_rom_prepared(request: SubRequest, launch_rom_source: str) -> str | None:
    marker = request.node.get_closest_marker('launch_rom_prepared')

    return None if marker is None else marker.args[0]


@pytest.fixture
def launch_rom(launch_rom_source: str, launch_rom_prepared: str | None) -> Rom:
    return Rom(Path(launch_rom_source), None if launch_rom_prepared is None else Path(launch_rom_prepared))


@pytest.fixture
def launch_config(
    mocker: MockerFixture,
    request: SubRequest,
    launch_config_emulator: str,
    launch_config_core: str | None,
    launch_config_system: str,
    launch_config_user_settings: dict[str, str],
    launch_config_system_settings: dict[str, str],
    launch_config_global_settings: dict[str, str],
    launch_config_render_config: dict[str, str],
    launch_rom: Rom,
) -> MockSystemConfig:
    """Fixture that returns a dictionary of settings for the mock SystemConfig object."""
    return MockSystemConfig(
        data=ChainMap(
            launch_config_user_settings, ChainMap(launch_config_system_settings, launch_config_global_settings)
        ),
        cli_args=mocker.Mock(),
        es_settings=mocker.Mock(),
        user_config=MockKeyValueConfig(data=launch_config_user_settings),
        system_settings=launch_config_system_settings,
        global_settings=launch_config_global_settings,
        system=launch_config_system,
        rom=launch_rom,
        emulator=launch_config_emulator,
        emulator_forced=False,
        raw_core=launch_config_core,
        core=launch_config_core or launch_config_emulator,
        core_forced=False,
        ui_mode='Full',
        show_fps=False,
        render_config_data=launch_config_render_config,
    )
