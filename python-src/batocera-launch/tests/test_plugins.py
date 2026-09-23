from __future__ import annotations

import asyncio
import threading
import time
from collections import ChainMap
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BATOCERA_CONF
from batocera_launch.config.config import SystemConfig
from batocera_launch.plugins import (
    HookContext,
    Plugin,
    PluginManager,
    load_plugins,
    power as power_module,
    tdp as tdp_module,
)
from batocera_launch.plugins.devfreq import STATE_DIR, DevfreqPlugin, detect_knobs, should_boost
from batocera_launch.plugins.power import PowerModePlugin, resolve_power_mode
from batocera_launch.plugins.tdp import TdpPlugin, tdp_watts

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyfakefs.fake_filesystem import FakeFilesystem

pytestmark = pytest.mark.usefixtures('fs')

_GPU = Path('/sys/class/devfreq/ff400000.gpu/governor')
_DMC = Path('/sys/class/devfreq/dmc/governor')
_MPGPU = Path('/sys/class/mpgpu/scale_mode')


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _config(
    *,
    system_settings: Mapping[str, str] | None = None,
    global_settings: Mapping[str, str] | None = None,
    user_config: KeyValueConfig | None = None,
    emulator: str = 'snes9x',
) -> SystemConfig:
    system_settings = ChainMap(dict(system_settings or {}))
    global_settings = dict(global_settings or {})
    none = cast('Any', None)

    return SystemConfig(
        ChainMap({}, ChainMap(system_settings, global_settings)),
        cli_args=none,
        es_settings=none,
        user_config=user_config or KeyValueConfig(),
        system_settings=system_settings,
        global_settings=global_settings,
        system='snes',
        rom=Path('/userdata/roms/snes/game.sfc'),
        emulator=emulator,
        emulator_forced=False,
        raw_core=None,
        core='',
        core_forced=False,
        ui_mode='Full',
        show_fps=False,
        netplay_mode=None,
        netplay_password=None,
        netplay_server_ip=None,
        netplay_server_port=None,
        netplay_server_session=None,
        state_slot=None,
        autosave=None,
        state_filename=None,
    )


def _context(**kwargs: Any) -> HookContext:
    return HookContext(_config(**kwargs))


@pytest.fixture
def on_mains(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(power_module, 'is_power_connected', lambda: True)


@pytest.fixture
def on_battery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(power_module, 'is_power_connected', lambda: False)


@pytest.fixture
def applied(monkeypatch: pytest.MonkeyPatch) -> list[str | None]:
    applied: list[str | None] = []

    def apply(mode: str | None, /, **kwargs: object) -> None:
        applied.append(mode)

    monkeypatch.setattr(power_module, 'apply_power_mode', apply)
    return applied


class TestResolvePowerMode:
    @pytest.mark.usefixtures('on_battery')
    def test_system_setting_wins_even_on_battery(self) -> None:
        config = _config(
            system_settings={'powermode': 'highperformance'}, global_settings={'batterymode': 'powersaver'}
        )

        assert resolve_power_mode(config) == 'highperformance'

    @pytest.mark.usefixtures('on_mains')
    def test_global_power_mode_on_mains(self) -> None:
        config = _config(global_settings={'powermode': 'balanced', 'batterymode': 'powersaver'})

        assert resolve_power_mode(config) == 'balanced'

    @pytest.mark.usefixtures('on_battery')
    def test_global_battery_mode_on_battery(self) -> None:
        config = _config(global_settings={'powermode': 'balanced', 'batterymode': 'powersaver'})

        assert resolve_power_mode(config) == 'powersaver'

    @pytest.mark.usefixtures('on_mains')
    def test_nothing_set(self) -> None:
        assert resolve_power_mode(_config()) is None


@pytest.mark.usefixtures('on_mains')
class TestPowerModePlugin:
    def test_start_applies_the_resolved_mode(self, applied: list[str | None]) -> None:
        PowerModePlugin().start(
            _context(system_settings={'powermode': 'powersaver'}, global_settings={'powermode': 'balanced'})
        )

        assert applied == ['powersaver']

    def test_stop_restores_the_global_mode(self, applied: list[str | None]) -> None:
        PowerModePlugin().stop(
            _context(system_settings={'powermode': 'powersaver'}, global_settings={'powermode': 'balanced'})
        )

        assert applied == ['balanced']

    def test_stop_without_a_global_mode_restores_the_default(self, applied: list[str | None]) -> None:
        PowerModePlugin().stop(_context(system_settings={'powermode': 'powersaver'}))

        assert applied == [None]


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


def _devfreq(path: Path, governor: str, available: str = 'simple_ondemand performance userspace') -> None:
    _write(path, f'{governor}\n')
    _write(path.with_name('available_governors'), f'{available}\n')


@pytest.mark.usefixtures('on_mains')
class TestDevfreqPlugin:
    def test_nothing_without_known_knobs(self) -> None:
        assert detect_knobs() == []

        DevfreqPlugin().start(_context(system_settings={'powermode': 'highperformance'}))
        DevfreqPlugin().stop(_context())

    def test_skips_a_device_without_the_performance_governor(self) -> None:
        _devfreq(_GPU, 'simple_ondemand', 'simple_ondemand')

        DevfreqPlugin().start(_context(system_settings={'powermode': 'highperformance'}))

        assert _GPU.read_text() == 'simple_ondemand\n'

    def test_boosts_and_restores_what_was_there(self) -> None:
        _devfreq(_GPU, 'simple_ondemand')
        _devfreq(_DMC, 'dmc_ondemand', 'dmc_ondemand performance')
        _write(_MPGPU, '1\n')
        plugin = DevfreqPlugin()

        plugin.start(_context(system_settings={'powermode': 'highperformance'}))

        assert _GPU.read_text() == 'performance'
        assert _DMC.read_text() == 'performance'
        assert _MPGPU.read_text() == '2'

        plugin.stop(_context())

        assert _GPU.read_text() == 'simple_ondemand'
        assert _DMC.read_text() == 'dmc_ondemand'
        assert _MPGPU.read_text() == '1'

    def test_a_governor_set_at_boot_is_left_alone(self) -> None:
        _devfreq(_GPU, 'performance')
        plugin = DevfreqPlugin()

        plugin.start(_context(global_settings={'powermode': 'balanced'}))
        plugin.stop(_context())

        assert _GPU.read_text() == 'performance\n'

    def test_already_boosted_is_left_alone_at_stop(self) -> None:
        _devfreq(_GPU, 'performance')
        plugin = DevfreqPlugin()

        plugin.start(_context(system_settings={'powermode': 'highperformance'}))
        plugin.stop(_context())

        assert _GPU.read_text() == 'performance\n'

    def test_not_boosting_leaves_a_custom_governor_alone(self) -> None:
        _devfreq(_GPU, 'userspace')

        DevfreqPlugin().start(_context(global_settings={'powermode': 'balanced'}))

        assert _GPU.read_text() == 'userspace\n'

    def test_a_launch_that_never_stopped_is_undone_by_the_next_one(self) -> None:
        _devfreq(_GPU, 'simple_ondemand')
        DevfreqPlugin().start(_context(system_settings={'powermode': 'highperformance'}))

        DevfreqPlugin().start(_context(global_settings={'powermode': 'powersaver'}))

        assert _GPU.read_text() == 'simple_ondemand'
        assert not any(STATE_DIR.iterdir())


class TestTdpPlugin:
    @pytest.fixture
    def applied(self, monkeypatch: pytest.MonkeyPatch) -> list[int]:
        applied: list[int] = []

        def apply(watts: int, /, **kwargs: object) -> None:
            applied.append(watts)

        monkeypatch.setattr(tdp_module, 'apply_tdp', apply)
        return applied

    @staticmethod
    def _user_config(max_tdp: str | None = '28') -> KeyValueConfig:
        config = KeyValueConfig()

        if max_tdp is not None:
            config['system.cpu.tdp'] = max_tdp

        return config

    @pytest.mark.parametrize(
        ('max_tdp', 'percentage', 'expected'), [('28', '50', 14), ('30', '75.0', 22), ('28', 'x', None)]
    )
    def test_watts(self, max_tdp: str, percentage: str, expected: int | None) -> None:
        assert tdp_watts(max_tdp, percentage) == expected

    def test_nothing_without_a_supported_cpu(self, applied: list[int]) -> None:
        plugin = TdpPlugin()

        plugin.start(_context(system_settings={'tdp': '50'}, user_config=self._user_config(None)))
        plugin.stop(_context(user_config=self._user_config(None)))

        assert applied == []

    def test_nothing_without_a_tdp_setting(self, applied: list[int]) -> None:
        plugin = TdpPlugin()

        plugin.start(_context(user_config=self._user_config()))
        plugin.stop(_context(user_config=self._user_config()))

        assert applied == []

    def test_scales_for_the_game_and_restores_the_maximum(self, applied: list[int]) -> None:
        plugin = TdpPlugin()
        context = _context(system_settings={'tdp': '50'}, user_config=self._user_config())

        plugin.start(context)
        plugin.stop(context)

        assert applied == [14, 28]

    def test_restores_the_global_percentage(self, applied: list[int]) -> None:
        plugin = TdpPlugin()
        context = _context(
            system_settings={'tdp': '50'}, global_settings={'tdp': '80'}, user_config=self._user_config()
        )

        plugin.start(context)
        plugin.stop(context)

        assert applied == [14, 22]


class _Recording(Plugin):
    def __init__(self, *, start_delay: float = 0) -> None:
        self.events: list[tuple[str, str]] = []
        self.start_delay = start_delay

    def start(self, context: HookContext, /) -> None:
        time.sleep(self.start_delay)
        self.events.append(('start', threading.current_thread().name))

    def stop(self, context: HookContext, /) -> None:
        self.events.append(('stop', threading.current_thread().name))


class _Failing(Plugin):
    def start(self, context: HookContext, /) -> None:
        raise RuntimeError('boom')


def _manager(*plugins: Plugin) -> PluginManager:
    return PluginManager(_context(), list(plugins))


class TestPluginManager:
    async def test_hooks_run_off_the_event_loop_thread(self) -> None:
        recording = _Recording()
        manager = _manager(recording)

        manager.start()
        await manager.ready()

        assert [event for event, _ in recording.events] == ['start']
        assert recording.events[0][1] != threading.current_thread().name

    async def test_ready_waits_for_a_slow_start(self) -> None:
        recording = _Recording(start_delay=0.2)
        manager = _manager(recording)

        manager.start()
        await manager.ready()

        assert [event for event, _ in recording.events] == ['start']

    async def test_a_failing_plugin_does_not_stop_the_others(self, caplog: pytest.LogCaptureFixture) -> None:
        recording = _Recording()
        manager = _manager(_Failing(), recording)

        manager.start()
        await manager.ready()

        assert [event for event, _ in recording.events] == ['start']
        assert '_Failing failed on start' in caplog.text

    async def test_stop_without_start(self) -> None:
        recording = _Recording()
        manager = _manager(recording)

        await manager.stop()

        assert [event for event, _ in recording.events] == ['stop']

    async def test_stop_runs_after_a_launch_cancelled_in_ready(self) -> None:
        recording = _Recording(start_delay=0.2)
        manager = _manager(recording)

        manager.start()
        waiting = asyncio.create_task(manager.ready())
        await asyncio.sleep(0)
        waiting.cancel()

        with pytest.raises(asyncio.CancelledError):
            await waiting

        await manager.stop()

        assert [event for event, _ in recording.events] == ['start', 'stop']

    async def test_stop_waits_for_a_slow_start(self) -> None:
        recording = _Recording(start_delay=0.2)
        manager = _manager(recording)

        manager.start()
        await manager.stop()

        assert [event for event, _ in recording.events] == ['start', 'stop']


def test_the_built_in_plugins_are_registered(fs: FakeFilesystem) -> None:
    fs.pause()
    names = {type(plugin).__name__ for plugin in load_plugins()}
    fs.resume()

    assert names >= {'DevfreqPlugin', 'PowerModePlugin', 'TdpPlugin'}
