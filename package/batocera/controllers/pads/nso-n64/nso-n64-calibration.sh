#!/bin/bash
# This is needed because the default calibration data for the NSO N64 controller is incorrect

# VID AND PID for NSO N64 controller
TARGET_VENDOR="057E"
TARGET_PRODUCT="2019"

UDEV_INFO=$(udevadm info --query=all --name="$DEVNAME")
DEVPATH=$(echo "$UDEV_INFO" | grep 'DEVPATH' | cut -d'=' -f2)

if [[ "$DEVPATH" == *"$TARGET_VENDOR"* ]] && [[ "$DEVPATH" == *"$TARGET_PRODUCT"* ]]; then
    # Apply calibration for X-axis (axis 0)
    evdev-joystick --e "$DEVNAME" --minimum -27767 --maximum 32767 --a 0 --d 500 --f 25

    # Apply calibration for Y-axis (axis 1)
    evdev-joystick --e "$DEVNAME" --minimum -32767 --maximum 27767 --a 1 --d 500 --f 25
else
    echo "Device not found, exiting."
    exit 1
fi

exit 0
