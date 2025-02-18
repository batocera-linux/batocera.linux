from __future__ import annotations

import json
import logging
import subprocess
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ..generators.Generator import Generator

eslog = logging.getLogger(__name__)

@contextmanager
def set_hotkeygen_context(generator: Generator, system: Emulator, /) -> Iterator[None]:
    # hotkeygen context
    hkc = generator.getHotkeysContext()

    # limit hotkeys
    # there is an option to disable all hotkeys but exit in case the player 1 is a pad with not hotkey specific button
    if system.isOptSet("exithotkeyonly") and system.getOptBoolean("exithotkeyonly"):
        if "exit" in hkc["keys"]:
            hkc["keys"] = { "exit": hkc["keys"]["exit"] }
        else:
            # should not happen while exit should always be there
            hkc["keys"] = {}
    # if uimod is not full (aka kiosk or children mode), remove the menu action
    if system.isOptSet("uimode") and system.config["uimode"] != "Full":
        if "menu" in hkc["keys"]:
            del hkc["keys"]["menu"]

    eslog.debug("hotkeygen: updating context to {}".format(hkc["name"]))
    subprocess.call(["hotkeygen", "--new-context", hkc["name"], json.dumps(hkc["keys"])])

    try:
        yield
    finally:
        # reset hotkeygen context
        eslog.debug("hotkeygen: resetting to default context")
        subprocess.call(["hotkeygen", "--default-context"])

def get_hotkeygen_event() -> str | None:
    import evdev

    for dev in evdev.list_devices():
        input_device = evdev.InputDevice(dev)
        if input_device.name == "batocera hotkeys":
            return dev
    return None
