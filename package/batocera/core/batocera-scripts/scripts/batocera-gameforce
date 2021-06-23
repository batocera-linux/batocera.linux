#!/bin/bash

if [ "${1}" == "buttonColorLed" ]; then

echo "${2}" > /userdata/system/buttoncolorled.save

case "${2}" in
    "red")
    echo 1 > /sys/class/leds/red/brightness
    echo 0 > /sys/class/leds/green/brightness
    echo 0 > /sys/class/leds/blue/brightness
    ;;
    "green")
    echo 0 > /sys/class/leds/red/brightness
    echo 1 > /sys/class/leds/green/brightness
    echo 0 > /sys/class/leds/blue/brightness
    ;;
    "blue")
    echo 0 > /sys/class/leds/red/brightness
    echo 0 > /sys/class/leds/green/brightness
    echo 1 > /sys/class/leds/blue/brightness
    ;;
    "white")
    echo 1 > /sys/class/leds/red/brightness
    echo 1 > /sys/class/leds/green/brightness
    echo 1 > /sys/class/leds/blue/brightness
    ;;
    "purple")
    echo 1 > /sys/class/leds/red/brightness
    echo 0 > /sys/class/leds/green/brightness
    echo 1 > /sys/class/leds/blue/brightness
    ;;
    "yellow")
    echo 1 > /sys/class/leds/red/brightness
    echo 1 > /sys/class/leds/green/brightness
    echo 0 > /sys/class/leds/blue/brightness
    ;;
    "cyan")
    echo 0 > /sys/class/leds/red/brightness
    echo 1 > /sys/class/leds/green/brightness
    echo 1 > /sys/class/leds/blue/brightness
    ;;
    "off")
    echo 0 > /sys/class/leds/red/brightness
    echo 0 > /sys/class/leds/green/brightness
    echo 0 > /sys/class/leds/blue/brightness
    ;;
    esac
fi

if [ "${1}" == "powerLed" ]; then

echo "${2}" > /userdata/system/powerled.save

case "${2}" in
    "off")
    echo 0 > /sys/class/leds/heartbeat/brightness
    ;;
    "heartbeat")
    echo "heartbeat" > /sys/class/leds/heartbeat/trigger
    ;;
    "on")
    echo 0 > /sys/class/leds/heartbeat/brightness
    echo 1 > /sys/class/leds/heartbeat/brightness
    ;;
    esac
fi
exit 0
