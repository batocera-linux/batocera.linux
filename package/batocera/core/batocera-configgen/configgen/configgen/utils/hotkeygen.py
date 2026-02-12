from __future__ import annotations

import json
import logging
import subprocess
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from types import TracebackType

    from ..Emulator import Emulator
    from ..generators.Generator import Generator

_logger = logging.getLogger(__name__)

@dataclass(slots=True)
class HotkeygenManager(AbstractContextManager['HotkeygenManager', None]):
    generator: Generator
    system: Emulator

    def __enter__(self) -> Self:
        # hotkeygen context
        hkc = self.generator.getHotkeysContext()

        exit_hotkey_only = self.system.config.get_bool("exithotkeyonly")

        # limit hotkeys
        # there is an option to disable all hotkeys but exit in case the player 1 is a pad with not hotkey specific button
        if exit_hotkey_only:
            if "exit" in hkc["keys"]:
                hkc["keys"] = { "exit": hkc["keys"]["exit"] }
            else:
                # should not happen while exit should always be there
                hkc["keys"] = {}

        # if uimod is not full (aka kiosk or children mode), remove the menu action
        if self.system.config.ui_mode != "Full" and "menu" in hkc["keys"]:
            del hkc["keys"]["menu"]

        _logger.debug("hotkeygen: updating context to %s", hkc["name"])

        cmd = ["hotkeygen", "--new-context", hkc["name"], json.dumps(hkc["keys"])]

        if exit_hotkey_only:
            cmd.append("--disable-common")

        subprocess.call(cmd)

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        # reset hotkeygen context
        _logger.debug("hotkeygen: resetting to default context")
        subprocess.call(["hotkeygen", "--default-context"])

    def reset_mouse(self) -> None:
        try:
            _logger.debug("Triggering mouse reset to primary display")
            subprocess.call(["/usr/bin/hotkeygen", "--reset-mouse"])
        except Exception as e:
            _logger.warning("Failed to reset mouse: %s", e)

def get_hotkeygen_event() -> str | None:
    import evdev

    for dev in evdev.list_devices():
        input_device = evdev.InputDevice(dev)
        if input_device.name == "batocera hotkeys":
            return dev
    return None
