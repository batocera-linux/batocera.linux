from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

_logger: Final = logging.getLogger(__name__)

SYS_CPU_DIR: Final = Path('/sys/devices/system/cpu')

# Below this fraction of the fastest core's capacity, a core is "little".
_LITTLE_CORE_THRESHOLD: Final = 0.6

_MIN_FAST_CORES: Final = 2


def read_cpu_capacities(sys_cpu_dir: Path = SYS_CPU_DIR, /) -> dict[int, int]:
    """Read each core's cpu_capacity; empty where the kernel does not expose it."""
    capacities: dict[int, int] = {}

    for capacity_file in sys_cpu_dir.glob('cpu[0-9]*/cpu_capacity'):
        try:
            capacities[int(capacity_file.parent.name[3:])] = int(capacity_file.read_text().strip())
        except OSError, ValueError:
            continue

    return capacities


def fast_cores(capacities: Mapping[int, int], /) -> frozenset[int] | None:
    """The cores that are not little, or None when there is nothing to exclude."""
    if not capacities:
        return None

    fastest = max(capacities.values())
    fast = frozenset(cpu for cpu, capacity in capacities.items() if capacity >= fastest * _LITTLE_CORE_THRESHOLD)

    if len(fast) == len(capacities) or len(fast) < _MIN_FAST_CORES:
        return None

    return fast


def resolve_cpu_cluster(mode: str, /, sys_cpu_dir: Path = SYS_CPU_DIR) -> frozenset[int] | None:
    """Translate the ``cpucluster`` setting (``all`` or ``fast``) into a CPU set, or None."""
    if mode == 'all':
        return None

    if mode != 'fast':
        _logger.warning('Unknown cpucluster value %r, using all cores', mode)
        return None

    capacities = read_cpu_capacities(sys_cpu_dir)
    cores = fast_cores(capacities)

    if cores is None:
        _logger.debug('CPU is homogeneous (capacities: %s), not restricting cores', capacities or 'unknown')
    else:
        _logger.debug('Fast cores: %s (capacities: %s)', sorted(cores), capacities)

    return cores
