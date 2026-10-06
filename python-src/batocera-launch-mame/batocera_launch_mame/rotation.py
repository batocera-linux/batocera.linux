from __future__ import annotations

import subprocess

from batocera_launch import HookContext, Plugin


def _resolution(command: str, /) -> str:
    return subprocess.run(['batocera-resolution', command], capture_output=True, text=True, check=False).stdout.strip()


class MameRotationPlugin(Plugin):
    def stop(self, context: HookContext, /) -> None:
        if context.config.emulator != 'mame' or _resolution('getDisplayMode') != 'xorg':
            return

        if rotation := _resolution('getRotation'):
            subprocess.run(['batocera-resolution', 'setRotation', rotation], check=False)
