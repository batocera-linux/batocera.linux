from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest
from batocera_launch_mame.rotation import MameRotationPlugin

from batocera_launch import HookContext, SystemConfig
from batocera_launch.plugin_manager import PluginManager

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_run(mocker: MockerFixture, request: pytest.FixtureRequest) -> Mock:
    outputs: dict[str, str] = getattr(request, 'param', {})

    def side_effect(command: list[str], /, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(stdout=outputs.get(command[1], ''))

    return mocker.patch('subprocess.run', side_effect=side_effect)


@pytest.fixture
def hook_context(launch_config: SystemConfig) -> HookContext:
    return HookContext(launch_config)


@pytest.mark.launch_config_emulator('snes9x')
def test_other_emulators_are_ignored(mock_run: Mock, hook_context: HookContext) -> None:
    MameRotationPlugin().stop(hook_context)

    mock_run.assert_not_called()


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.parametrize('mock_run', [{'getDisplayMode': 'xorg\n', 'getRotation': '1\n'}], indirect=True)
def test_reapplies_the_xorg_rotation(mock_run: Mock, hook_context: HookContext) -> None:
    MameRotationPlugin().stop(hook_context)

    assert mock_run.call_args_list == [
        ((['batocera-resolution', 'getDisplayMode'],), {'capture_output': True, 'text': True, 'check': False}),
        ((['batocera-resolution', 'getRotation'],), {'capture_output': True, 'text': True, 'check': False}),
        ((['batocera-resolution', 'setRotation', '1'],), {'check': False}),
    ]


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.parametrize('mock_run', [{'getDisplayMode': 'wayland\n'}], indirect=True)
def test_leaves_wayland_alone(mock_run: Mock, hook_context: HookContext) -> None:
    MameRotationPlugin().stop(hook_context)

    assert mock_run.call_args_list == [
        ((['batocera-resolution', 'getDisplayMode'],), {'capture_output': True, 'text': True, 'check': False}),
    ]


def test_is_registered(mocker: MockerFixture) -> None:
    manager = PluginManager(mocker.Mock(spec=HookContext))
    assert 'MameRotationPlugin' in {type(plugin).__name__ for plugin in manager.plugins}
