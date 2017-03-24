#!/bin/bash

V_ARCH=$(cat /recalbox/recalbox.arch)
V_OPENGLVERSION=$(DISPLAY=:0.0 glxinfo | grep -E '^OpenGL version string:' | sed -e s+'^OpenGL version string:[ ]*'++)
V_CPUNB=$(grep -E $'^processor\t:' /proc/cpuinfo | wc -l)
V_CPUMODEL1=$(grep -E $'^model name\t:' /proc/cpuinfo | head -1 | sed -e s+'^model name\t: '++)

echo "Architecture: ${V_ARCH}"
if test "${V_ARCH}" = "x86" -o "${V_ARCH}" = "x86_64"
then
    echo "OpenGL version: ${V_OPENGLVERSION}"
fi
echo "Cpu number: ${V_CPUNB}"
echo "Cpu model: ${V_CPUMODEL1}"

# battery
if test -e /sys/class/power_supply/BAT0/capacity
then
    BATT=$(cat /sys/class/power_supply/BAT0/capacity)
    echo "Battery: ${BATT}%"
fi

# temperature
# Unit: millidegree Celsius
TEMPE=$(cat /sys/devices/virtual/thermal/thermal_zone*/temp 2>/dev/null | sort -rn | head -1 | sed -e s+"[0-9][0-9][0-9]$"++)
if test -n "${TEMPE}"
then
    echo "Temperature: ${TEMPE}°"
fi
