from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from . import Hook

if TYPE_CHECKING:
    from ..config.config import SystemConfig


def _resolution(command: str, /) -> str:
    return subprocess.run(['batocera-resolution', command], capture_output=True, text=True, check=False).stdout.strip()


class MameRotationHook(Hook):
    """A rotated xorg screen can come back unrotated after MAME exits; apply the rotation again."""

    def stop(self, config: SystemConfig, /) -> None:
        if config.emulator != 'mame' or _resolution('getDisplayMode') != 'xorg':
            return

        if rotation := _resolution('getRotation'):
            subprocess.run(['batocera-resolution', 'setRotation', rotation], check=False)
