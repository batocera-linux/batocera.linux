from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


def get_cpu_speed() -> int:
    try:
        if not Path("/usr/bin/lscpu").exists():
            return 0

        cpuSpdCmd = 'lscpu -e=maxmhz | grep -m 1 "[0-9]" | cut -d, -f1'
        cpuSpdOutput = subprocess.check_output(cpuSpdCmd, shell=True).decode(sys.stdout.encoding)[:-1]
        return int(cpuSpdOutput)
    except Exception:
        return 0

def is_pc() -> bool:
    try:
        return platform.uname().machine.lower().find("x86") == 0
    except Exception:
        return False
