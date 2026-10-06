from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.cpu import fast_cores, read_cpu_capacities, resolve_cpu_cluster

if TYPE_CHECKING:
    from collections.abc import Mapping

pytestmark = pytest.mark.usefixtures('fs')

_SYS_CPU = Path('/sys/devices/system/cpu')

# 6x Cortex-A55 + 2x Cortex-A78 (Snapdragon 4 Gen 2), as the kernel reports it
_SM4450 = {0: 451, 1: 451, 2: 451, 3: 451, 4: 451, 5: 451, 6: 1024, 7: 1024}

# 4x Cortex-A55 + 3x Cortex-A77 + 1x prime Cortex-A77 (Snapdragon 865)
_SM8250 = {0: 402, 1: 402, 2: 402, 3: 402, 4: 873, 5: 873, 6: 873, 7: 1024}


def _write_capacities(capacities: Mapping[int, int | str], /) -> None:
    for cpu, capacity in capacities.items():
        cpu_dir = _SYS_CPU / f'cpu{cpu}'
        cpu_dir.mkdir(parents=True, exist_ok=True)
        (cpu_dir / 'cpu_capacity').write_text(f'{capacity}\n')


class TestReadCpuCapacities:
    def test_reads_every_core(self) -> None:
        _write_capacities(_SM4450)

        assert read_cpu_capacities(_SYS_CPU) == _SM4450

    def test_missing_sysfs_is_empty(self) -> None:
        assert read_cpu_capacities(_SYS_CPU) == {}

    def test_homogeneous_kernel_without_capacity_files_is_empty(self) -> None:
        (_SYS_CPU / 'cpu0').mkdir(parents=True)
        (_SYS_CPU / 'cpu1').mkdir(parents=True)

        assert read_cpu_capacities(_SYS_CPU) == {}

    def test_unparsable_core_is_skipped(self) -> None:
        _write_capacities({0: 1024, 1: 'garbage', 2: 1024})

        assert read_cpu_capacities(_SYS_CPU) == {0: 1024, 2: 1024}

    def test_ignores_non_cpu_entries(self) -> None:
        _write_capacities({0: 1024, 1: 1024})
        (_SYS_CPU / 'cpufreq').mkdir()
        (_SYS_CPU / 'cpufreq' / 'cpu_capacity').write_text('1\n')

        assert read_cpu_capacities(_SYS_CPU) == {0: 1024, 1: 1024}


class TestFastCores:
    def test_big_little_drops_little_cores(self) -> None:
        assert fast_cores(_SM4450) == {6, 7}

    def test_three_tier_keeps_prime_and_gold_cores(self) -> None:
        assert fast_cores(_SM8250) == {4, 5, 6, 7}

    def test_homogeneous_is_none(self) -> None:
        assert fast_cores({0: 1024, 1: 1024, 2: 1024, 3: 1024}) is None

    def test_empty_is_none(self) -> None:
        assert fast_cores({}) is None

    def test_single_fast_core_is_not_worth_it(self) -> None:
        assert fast_cores({0: 1024, 1: 400, 2: 400, 3: 400}) is None

    def test_mild_spread_counts_as_homogeneous(self) -> None:
        # Two-tier parts with no efficiency cores, like a prime + performance layout
        assert fast_cores({0: 1024, 1: 1024, 2: 850, 3: 850, 4: 850, 5: 850}) is None


class TestResolveCpuCluster:
    def test_fast_picks_fast_cores(self) -> None:
        _write_capacities(_SM4450)

        assert resolve_cpu_cluster('fast', _SYS_CPU) == {6, 7}

    def test_all_never_restricts(self) -> None:
        _write_capacities(_SM4450)

        assert resolve_cpu_cluster('all', _SYS_CPU) is None

    def test_fast_on_homogeneous_cpu_is_none(self) -> None:
        _write_capacities({0: 1024, 1: 1024, 2: 1024, 3: 1024})

        assert resolve_cpu_cluster('fast', _SYS_CPU) is None

    def test_fast_without_sysfs_is_none(self) -> None:
        assert resolve_cpu_cluster('fast', _SYS_CPU) is None

    def test_unknown_value_is_none(self) -> None:
        _write_capacities(_SM4450)

        assert resolve_cpu_cluster('bogus', _SYS_CPU) is None
