#!/bin/bash

# This is needed because the default calibration data for the NSO N64 controller is incorrect

# VID AND PID for NSO N64 controller
TARGET_VENDOR="057E"
TARGET_PRODUCT="2019"

find_event_device() {
    for device in /dev/input/event*; do
        udev_info=$(udevadm info --query=all --name="$device")        
        devpath=$(echo "$udev_info" | grep 'DEVPATH' | cut -d'=' -f2)
        
        if [[ "$devpath" == *"$TARGET_VENDOR"* ]] && [[ "$devpath" == *"$TARGET_PRODUCT"* ]]; then
            EVENT_PATH=$device
            return 0
        fi
    done

    return 1
}

find_event_device

if [ -z "$EVENT_PATH" ]; then
    echo "Device not found, exiting."
    exit 1
fi

# Apply calibration for X-axis (axis 0)
evdev-joystick --e "$EVENT_PATH" --minimum -27767 --maximum 32767 --a 0 --d 500 --f 25

# Apply calibration for Y-axis (axis 1)
evdev-joystick --e "$EVENT_PATH" --minimum -32767 --maximum 27767 --a 1 --d 500 --f 25

exit 0
