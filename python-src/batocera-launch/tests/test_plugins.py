from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_common.paths import BATOCERA_CONF
from batocera_launch.plugin_manager import HookContext
from batocera_launch.plugins.devfreq import STATE_DIR, DevfreqPlugin, detect_knobs, should_boost
from batocera_launch.plugins.power import PowerModePlugin, resolve_power_mode
from batocera_launch.plugins.tdp import TdpPlugin, tdp_watts

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

    from batocera_launch.config.config import SystemConfig


pytestmark = pytest.mark.usefixtures('fs')


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def on_mains(mocker: MockerFixture) -> None:
    mocker.patch('batocera_launch.plugins.power.is_power_connected', return_value=True)


@pytest.fixture
def on_battery(mocker: MockerFixture) -> None:
    mocker.patch('batocera_launch.plugins.power.is_power_connected', return_value=False)


@pytest.fixture
def hook_context(launch_config: SystemConfig) -> HookContext:
    return HookContext(launch_config)


class TestResolvePowerMode:
    @pytest.mark.usefixtures('on_battery')
    @pytest.mark.launch_config_system_settings({'powermode': 'highperformance'})
    @pytest.mark.launch_config_global_settings({'batterymode': 'powersaver'})
    def test_system_setting_wins_even_on_battery(self, launch_config: SystemConfig) -> None:
        assert resolve_power_mode(launch_config) == 'highperformance'

    @pytest.mark.usefixtures('on_mains')
    @pytest.mark.launch_config_global_settings({'powermode': 'balanced', 'batterymode': 'powersaver'})
    def test_global_power_mode_on_mains(self, launch_config: SystemConfig) -> None:
        assert resolve_power_mode(launch_config) == 'balanced'

    @pytest.mark.usefixtures('on_battery')
    @pytest.mark.launch_config_global_settings({'powermode': 'balanced', 'batterymode': 'powersaver'})
    def test_global_battery_mode_on_battery(self, launch_config: SystemConfig) -> None:
        assert resolve_power_mode(launch_config) == 'powersaver'

    @pytest.mark.usefixtures('on_mains')
    def test_nothing_set(self, launch_config: SystemConfig) -> None:
        assert resolve_power_mode(launch_config) is None


@pytest.mark.usefixtures('on_mains')
class TestPowerModePlugin:
    @pytest.fixture
    def apply_power_mode(self, mocker: MockerFixture) -> Mock:
        return mocker.patch('batocera_launch.plugins.power.apply_power_mode')

    @pytest.mark.launch_config_system_settings({'powermode': 'powersaver'})
    @pytest.mark.launch_config_global_settings({'powermode': 'balanced'})
    def test_start_applies_the_resolved_mode(self, apply_power_mode: Mock, hook_context: HookContext) -> None:
        PowerModePlugin().start(hook_context)

        apply_power_mode.assert_called_once_with('powersaver', user_config=hook_context.config.user_config)

    @pytest.mark.launch_config_system_settings({'powermode': 'powersaver'})
    @pytest.mark.launch_config_global_settings({'powermode': 'balanced'})
    def test_stop_restores_the_global_mode(self, apply_power_mode: Mock, hook_context: HookContext) -> None:
        PowerModePlugin().stop(hook_context)

        apply_power_mode.assert_called_once_with('balanced', user_config=hook_context.config.user_config)

    @pytest.mark.launch_config_system_settings({'powermode': 'powersaver'})
    def test_stop_without_a_global_mode_restores_the_default(
        self, apply_power_mode: Mock, hook_context: HookContext
    ) -> None:
        PowerModePlugin().stop(hook_context)

        apply_power_mode.assert_called_once_with(None, user_config=hook_context.config.user_config)


class TestShouldBoost:
    @pytest.mark.parametrize(
        ('mode', 'expected'), [('highperformance', True), ('balanced', False), ('powersaver', False), ('bogus', False)]
    )
    def test_from_the_power_mode(self, mode: str, expected: bool) -> None:
        assert should_boost(mode) is expected

    @pytest.mark.parametrize(('governor', 'expected'), [('performance', True), ('schedutil', False)])
    def test_from_the_system_governor_without_a_mode(self, governor: str, expected: bool) -> None:
        _write(BATOCERA_CONF, f'system.cpu.governor={governor}\n')

        assert should_boost(None) is expected


def _initialize_sysfs_governor(
    fs: FakeFilesystem,
    path: Path,
    params: str | tuple[str, str],
) -> None:
    if isinstance(params, str):
        governor = params
        available = 'simple_ondemand performance userspace'
    else:
        governor, available = params

    fs.makedirs(str(path.parent), exist_ok=True)
    fs.create_file(str(path), contents=f'{governor}\n')  # pyright: ignore
    fs.create_file(str(path.with_name('available_governors')), contents=f'{available}\n')  # pyright: ignore


@pytest.mark.usefixtures('on_mains')
class TestDevfreqPlugin:
    @pytest.fixture
    def mock_gpu(self, request: pytest.FixtureRequest, fs: FakeFilesystem) -> Path:
        gpu = Path('/sys/class/devfreq/ff400000.gpu/governor')

        _initialize_sysfs_governor(fs, gpu, request.param)

        return gpu

    @pytest.fixture
    def mock_dmc(self, request: pytest.FixtureRequest, fs: FakeFilesystem) -> Path:
        dmc = Path('/sys/class/devfreq/dmc/governor')

        _initialize_sysfs_governor(fs, dmc, request.param)

        return dmc

    @pytest.fixture
    def mock_mpgpu(self, fs: FakeFilesystem) -> Path:
        mpgpu = Path('/sys/class/mpgpu/scale_mode')

        fs.create_file(str(mpgpu), contents='1\n')  # pyright: ignore

        return mpgpu

    @pytest.mark.launch_config_system_settings({'powermode': 'highperformance'})
    def test_nothing_without_known_knobs(self, hook_context: HookContext) -> None:
        assert detect_knobs() == []

        DevfreqPlugin().start(hook_context)
        DevfreqPlugin().stop(hook_context)

    @pytest.mark.parametrize('mock_gpu', [('simple_ondemand', 'simple_ondemand')], indirect=True)
    @pytest.mark.launch_config_system_settings({'powermode': 'highperformance'})
    def test_skips_a_device_without_the_performance_governor(self, hook_context: HookContext, mock_gpu: Path) -> None:
        DevfreqPlugin().start(hook_context)

        assert mock_gpu.read_text() == 'simple_ondemand\n'

    @pytest.mark.parametrize('mock_gpu', ['simple_ondemand'], indirect=True)
    @pytest.mark.parametrize('mock_dmc', [('dmc_ondemand', 'dmc_ondemand performance')], indirect=True)
    @pytest.mark.launch_config_system_settings({'powermode': 'highperformance'})
    def test_boosts_and_restores_what_was_there(
        self, hook_context: HookContext, mock_gpu: Path, mock_dmc: Path, mock_mpgpu: Path
    ) -> None:
        plugin = DevfreqPlugin()

        plugin.start(hook_context)

        assert mock_gpu.read_text() == 'performance'
        assert mock_dmc.read_text() == 'performance'
        assert mock_mpgpu.read_text() == '2'

        plugin.stop(hook_context)

        assert mock_gpu.read_text() == 'simple_ondemand'
        assert mock_dmc.read_text() == 'dmc_ondemand'
        assert mock_mpgpu.read_text() == '1'

    @pytest.mark.parametrize('mock_gpu', ['performance'], indirect=True)
    @pytest.mark.launch_config_global_settings({'powermode': 'balanced'})
    def test_a_governor_set_at_boot_is_left_alone(self, hook_context: HookContext, mock_gpu: Path) -> None:
        plugin = DevfreqPlugin()

        plugin.start(hook_context)
        plugin.stop(hook_context)

        assert mock_gpu.read_text() == 'performance\n'

    @pytest.mark.parametrize('mock_gpu', ['performance'], indirect=True)
    @pytest.mark.launch_config_system_settings({'powermode': 'highperformance'})
    def test_already_boosted_is_left_alone_at_stop(self, hook_context: HookContext, mock_gpu: Path) -> None:
        plugin = DevfreqPlugin()

        plugin.start(hook_context)
        plugin.stop(hook_context)

        assert mock_gpu.read_text() == 'performance\n'

    @pytest.mark.parametrize('mock_gpu', ['userspace'], indirect=True)
    @pytest.mark.launch_config_global_settings({'powermode': 'balanced'})
    def test_not_boosting_leaves_a_custom_governor_alone(self, hook_context: HookContext, mock_gpu: Path) -> None:
        DevfreqPlugin().start(hook_context)

        assert mock_gpu.read_text() == 'userspace\n'

    @pytest.mark.parametrize('mock_gpu', ['simple_ondemand'], indirect=True)
    @pytest.mark.launch_config_system_settings({'powermode': 'highperformance'})
    def test_a_launch_that_never_stopped_is_undone_by_the_next_one(
        self, hook_context: HookContext, mock_gpu: Path
    ) -> None:
        DevfreqPlugin().start(hook_context)

        hook_context.config.system_settings.pop('powermode', None)  # pyright: ignore
        hook_context.config.global_settings['powermode'] = 'powersaver'  # pyright: ignore

        DevfreqPlugin().start(hook_context)

        assert mock_gpu.read_text() == 'simple_ondemand'
        assert not any(STATE_DIR.iterdir())


class TestTdpPlugin:
    @pytest.fixture
    def apply_tdp(self, mocker: MockerFixture) -> Mock:
        return mocker.patch('batocera_launch.plugins.tdp.apply_tdp')

    @pytest.mark.parametrize(
        ('max_tdp', 'percentage', 'expected'), [('28', '50', 14), ('30', '75.0', 22), ('28', 'x', None)]
    )
    def test_watts(self, max_tdp: str, percentage: str, expected: int | None) -> None:
        assert tdp_watts(max_tdp, percentage) == expected

    @pytest.mark.launch_config_system_settings({'tdp': '50'})
    def test_nothing_without_a_supported_cpu(self, apply_tdp: Mock, hook_context: HookContext) -> None:
        plugin = TdpPlugin()

        plugin.start(hook_context)
        plugin.stop(hook_context)

        apply_tdp.assert_not_called()

    @pytest.mark.launch_config_user_settings({'system.cpu.tdp': '28'})
    def test_nothing_without_a_tdp_setting(self, apply_tdp: Mock, hook_context: HookContext) -> None:
        plugin = TdpPlugin()

        plugin.start(hook_context)
        plugin.stop(hook_context)

        apply_tdp.assert_not_called()

    @pytest.mark.launch_config_user_settings({'system.cpu.tdp': '28'})
    @pytest.mark.launch_config_system_settings({'tdp': '50'})
    def test_scales_for_the_game_and_restores_the_maximum(self, apply_tdp: Mock, hook_context: HookContext) -> None:
        plugin = TdpPlugin()

        plugin.start(hook_context)
        plugin.stop(hook_context)

        assert apply_tdp.call_args_list == [
            ((14,), {}),
            ((28,), {'detach': True}),
        ]

    @pytest.mark.launch_config_user_settings({'system.cpu.tdp': '28'})
    @pytest.mark.launch_config_system_settings({'tdp': '50'})
    @pytest.mark.launch_config_global_settings({'tdp': '80'})
    def test_restores_the_global_percentage(self, apply_tdp: Mock, hook_context: HookContext) -> None:
        plugin = TdpPlugin()

        plugin.start(hook_context)
        plugin.stop(hook_context)

        assert apply_tdp.call_args_list == [((14,), {}), ((22,), {'detach': True})]
