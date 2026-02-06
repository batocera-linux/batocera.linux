#!/usr/bin/env python3
#
# Detect if this Batocera instance has a touchscreen (for Wayland).
# Discord: @lbrpdx
#
import re
import sys
import subprocess

def get_touch_device_names():
    # Run `libinput list-devices` and capture stdout
    try:
        result = subprocess.run(
            ["libinput", "list-devices"],
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running libinput: {e}", file=sys.stderr)
        return None

    output = result.stdout
    blocks = re.split(r"\n\s*\n", output.strip())

    names = []
    for block in blocks:
        if re.search(r"Capabilities:.*touch", block):
            m = re.search(r"Device:\s+([^\n]+)", block)
            if m:
                names.append(m.group(1))

    return names


def main():
    touch_devs = get_touch_device_names()

    if len(touch_devs)>0:
        print("Touchscreen-like device(s) found:")
        for d in touch_devs:
            print(
                f'  - {d}'
            )
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

