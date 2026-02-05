#!/usr/bin/env python3
#
# Detect if this Batocera instance has a touchscreen (for Wayland).
# Discord: @lbrpdx
#
import re
import sys
from dataclasses import dataclass
from typing import List, Optional

# Generic names of touchscreen devices to look for (lowercase)
TC_NAME_IDS = [ "touch", "digitizer", "fts3528", "ft5x06", "td4328" ]

# Other proprietary touchscreens: pairs of [ vendor, product ]
PROPRIETARY_TC = [ [ "2808" , "1015" ], # SteamDeck LCD
                 ]
PROC_INPUT_DEVICES = "/proc/bus/input/devices"

@dataclass
class InputDeviceInfo:
    name: str
    handlers: List[str]
    bus: Optional[str]
    vendor: Optional[str]
    product: Optional[str]
    abs_bits: Optional[str]
    key_bits: Optional[str]

def parse_proc_bus_input_devices(path: str = PROC_INPUT_DEVICES) -> List[InputDeviceInfo]:
    devices: List[InputDeviceInfo] = []
    current: dict = {}

    def flush():
        nonlocal current
        if current:
            devices.append(
                InputDeviceInfo(
                    name=current.get("name", ""),
                    handlers=current.get("handlers", []),
                    bus=current.get("bus"),
                    vendor=current.get("vendor"),
                    product=current.get("product"),
                    abs_bits=current.get("abs"),
                    key_bits=current.get("key"),
                )
            )
            current = {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    flush()
                    continue

                prefix = line[:2]
                rest = line[3:]

                if prefix == "I:":
                    # I: Bus=0018 Vendor=2808 Product=1015 Version=0100
                    parts = rest.split()
                    for p in parts:
                        if p.startswith("Bus="):
                            current["bus"] = p.split("=", 1)[1]
                        elif p.startswith("Vendor="):
                            current["vendor"] = p.split("=", 1)[1]
                        elif p.startswith("Product="):
                            current["product"] = p.split("=", 1)[1]
                elif prefix == "N:":
                    # N: Name="FTS3528:00 2808:1015"
                    m = re.search(r'Name="([^"]+)"', rest)
                    if m:
                        current["name"] = m.group(1)
                elif prefix == "H:":
                    # H: Handlers=ledtrig_input_events event14
                    m = re.search(r"Handlers=(.+)", rest)
                    if m:
                        current["handlers"] = m.group(1).split()
                elif prefix == "B:":
                    # B: ABS=3273800000000003
                    if rest.startswith("ABS="):
                        current["abs"] = rest.split("=", 1)[1]
                    elif rest.startswith("KEY="):
                        current["key"] = rest.split("=", 1)[1]
            # flush last
            flush()
    except FileNotFoundError:
        return []

    return devices


def looks_like_touchscreen(dev: InputDeviceInfo) -> bool:
    name_lower = dev.name.lower()

    # Generic name-based heuristics
    for n in TC_NAME_IDS:
        if n in name_lower:
            return True

    # Known vendors list
    for p in PROPRIETARY_TC:
        if dev.vendor == p[0] and dev.product == p[1]:
            return True

    return False


def has_touchscreen() -> bool:
    devices = parse_proc_bus_input_devices()
    for dev in devices:
        if looks_like_touchscreen(dev):
            return True
    return False


def main():
    devices = parse_proc_bus_input_devices()
    touch_devs = [d for d in devices if looks_like_touchscreen(d)]

    if touch_devs:
        print("Touchscreen-like device(s) found:")
        for d in touch_devs:
            handlers = " ".join(d.handlers)
            print(
                f'  - name="{d.name}", bus={d.bus}, vendor={d.vendor}, '
                f"product={d.product}, handlers=[{handlers}]"
            )
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

