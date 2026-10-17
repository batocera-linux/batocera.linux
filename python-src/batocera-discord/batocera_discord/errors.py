"""Exception groups, kept as tuples so the code also runs on the Python 3.12 of older images.

(the formatter turns ``except (A, B):`` into the 3.14-only ``except A, B:``)
"""

from __future__ import annotations

import subprocess
from typing import Final

PROCESS_ERRORS: Final = (OSError, subprocess.TimeoutExpired)
IO_ERRORS: Final = (OSError, ValueError)
LOOKUP_ERRORS: Final = (KeyError, ValueError)
