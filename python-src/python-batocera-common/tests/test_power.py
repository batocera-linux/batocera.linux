from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from batocera_common import power
from batocera_common.paths import BATOCERA_CONF
from batocera_common.power import CPU_DIR, CPUFREQ_DIR, POWER_SUPPLY_DIR, apply_power_mode, is_power_connected, main

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

pytestmark = pytest.mark.usefixtures('fs')


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _cpufreq(governors: str, *, policies: Sequence[str] = ('policy0', 'policy4'), epp: str | None = None) -> None:
    for policy in policies:
        _write(CPUFREQ_DIR / policy / 'scaling_available_governors', f'{governors}\n')
        _write(CPUFREQ_DIR / policy / 'scaling_governor', 'schedutil\n')

    if epp is not None:
        for cpu in range(len(policies)):
            _write(CPU_DIR / f'cpu{cpu}' / 'cpufreq' / 'energy_performance_available_preferences', f'{epp}\n')
            _write(CPU_DIR / f'cpu{cpu}' / 'cpufreq' / 'energy_performance_preference', 'default\n')


def _governors() -> set[str]:
    return {path.read_text() for path in CPUFREQ_DIR.glob('policy*/scaling_governor')}


def _epps() -> set[str]:
    return {path.read_text() for path in CPU_DIR.glob('cpu*/cpufreq/energy_performance_preference')}


class TestApplyPowerMode:
    def test_nothing_without_cpufreq(self) -> None:
        apply_power_mode('highperformance')

        assert not CPUFREQ_DIR.exists()

    def test_highperformance(self) -> None:
        _cpufreq('performance schedutil', epp='default performance power')

        apply_power_mode('highperformance')

        assert _governors() == {'performance'}
        assert _epps() == {'performance'}

    def test_balanced_takes_the_first_available_governor(self) -> None:
        _cpufreq('performance ondemand powersave', epp='default performance power')

        apply_power_mode('balanced')

        assert _governors() == {'ondemand'}
        assert _epps() == {'default'}

    def test_powersaver(self) -> None:
        _cpufreq('performance powersave', epp='default performance power')

        apply_power_mode('powersaver')

        assert _governors() == {'powersave'}
        assert _epps() == {'power'}

    def test_default_restores_the_system_governor(self) -> None:
        _cpufreq('performance ondemand schedutil', epp='performance power')
        _write(BATOCERA_CONF, 'system.cpu.governor=ondemand\n')

        apply_power_mode(None)

        assert _governors() == {'ondemand'}
        assert _epps() == {'performance'}

    def test_default_ignores_an_unavailable_governor(self) -> None:
        _cpufreq('performance schedutil')
        _write(BATOCERA_CONF, 'system.cpu.governor=ondemand\n')

        apply_power_mode('default')

        assert _governors() == {'schedutil\n'}

    def test_unknown_mode_changes_nothing(self) -> None:
        _cpufreq('performance schedutil')

        apply_power_mode('turbo')

        assert _governors() == {'schedutil\n'}

    def test_only_writes_changed_policies(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _cpufreq('performance schedutil')
        (CPUFREQ_DIR / 'policy4' / 'scaling_governor').write_text('performance\n')
        written: list[Path] = []

        def write(path: Path, value: str, /) -> None:
            written.append(path)

        monkeypatch.setattr(power, 'write_sysfs', write)

        apply_power_mode('highperformance')

        assert written == [CPUFREQ_DIR / 'policy0' / 'scaling_governor']


class TestIsPowerConnected:
    def test_no_power_supplies_means_mains(self) -> None:
        assert is_power_connected()

    @pytest.mark.parametrize(('online', 'expected'), [('1', True), ('0', False)])
    def test_charger_online_flag(self, online: str, expected: bool) -> None:
        _write(POWER_SUPPLY_DIR / 'axp20x-usb' / 'type', 'USB\n')
        _write(POWER_SUPPLY_DIR / 'axp20x-usb' / 'online', f'{online}\n')
        _write(POWER_SUPPLY_DIR / 'axp20x-battery' / 'type', 'Battery\n')
        _write(POWER_SUPPLY_DIR / 'axp20x-battery' / 'status', 'Discharging\n')

        assert is_power_connected() is expected

    @pytest.mark.parametrize(('status', 'expected'), [('Discharging', False), ('Charging', True), ('Full', True)])
    def test_battery_status_without_a_charger_node(self, status: str, expected: bool) -> None:
        _write(POWER_SUPPLY_DIR / 'BAT0' / 'type', 'Battery\n')
        _write(POWER_SUPPLY_DIR / 'BAT0' / 'status', f'{status}\n')

        assert is_power_connected() is expected

    def test_a_peripheral_battery_is_not_a_charger(self) -> None:
        _write(POWER_SUPPLY_DIR / 'hidpp_battery_0' / 'type', 'Battery\n')
        _write(POWER_SUPPLY_DIR / 'hidpp_battery_0' / 'online', '1\n')
        _write(POWER_SUPPLY_DIR / 'hidpp_battery_0' / 'status', 'Discharging\n')
        _write(POWER_SUPPLY_DIR / 'BAT0' / 'type', 'Battery\n')
        _write(POWER_SUPPLY_DIR / 'BAT0' / 'status', 'Discharging\n')

        assert not is_power_connected()


class TestMain:
    @pytest.fixture
    def applied(self, monkeypatch: pytest.MonkeyPatch) -> list[str | None]:
        applied: list[str | None] = []

        def apply(mode: str | None, /, **kwargs: object) -> None:
            applied.append(mode)

        monkeypatch.setattr(power, 'apply_power_mode', apply)
        return applied

    def _run(self, monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
        monkeypatch.setattr('sys.argv', ['batocera-power-mode', *args])
        main()

    def test_ac_uses_the_global_power_mode(self, monkeypatch: pytest.MonkeyPatch, applied: list[str | None]) -> None:
        _write(BATOCERA_CONF, 'global.powermode=balanced\n')

        self._run(monkeypatch, 'ac')

        assert applied == ['balanced']

    def test_ac_without_a_mode_restores_the_default(
        self, monkeypatch: pytest.MonkeyPatch, applied: list[str | None]
    ) -> None:
        _write(BATOCERA_CONF, '')

        self._run(monkeypatch, 'ac')

        assert applied == [None]

    def test_battery_defaults_to_balanced(self, monkeypatch: pytest.MonkeyPatch, applied: list[str | None]) -> None:
        _write(BATOCERA_CONF, '')

        self._run(monkeypatch, 'battery')

        assert applied == ['balanced']

    def test_battery_uses_the_battery_mode(self, monkeypatch: pytest.MonkeyPatch, applied: list[str | None]) -> None:
        _write(BATOCERA_CONF, 'global.batterymode=powersaver\n')

        self._run(monkeypatch, 'battery')

        assert applied == ['powersaver']

    def test_mode_is_case_insensitive(self, monkeypatch: pytest.MonkeyPatch, applied: list[str | None]) -> None:
        self._run(monkeypatch, 'Powersaver')

        assert applied == ['powersaver']

    def test_unknown_mode_exits(self, monkeypatch: pytest.MonkeyPatch, applied: list[str | None]) -> None:
        with pytest.raises(SystemExit):
            self._run(monkeypatch, 'turbo')

        assert applied == []
