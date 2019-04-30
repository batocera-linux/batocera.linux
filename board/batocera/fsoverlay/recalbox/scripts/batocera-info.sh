#!/bin/bash

### short version (for osd)
if test "$1" = "--short"
then
    BATT=$(grep -E "^POWER_SUPPLY_CAPACITY=" /sys/class/power_supply/BAT*/uevent | sed -e s+'^POWER_SUPPLY_CAPACITY='++ | sort -rn | head -1)
    DT=$(date +%H:%M)
    if test -n "${BATT}"
    then
	echo "Battery: ${BATT}% - ${DT}"
    else
	echo "${DT}"
    fi
    exit 0
fi
###

V_ARCH=$(cat /usr/share/batocera/batocera.arch)
V_CPUNB=$(grep -E $'^processor\t:' /proc/cpuinfo | wc -l)
V_CPUMODEL1=$(grep -E $'^model name\t:' /proc/cpuinfo | head -1 | sed -e s+'^model name\t: '++)
V_SYSTEM=$(uname -rs)

# battery
BATT=$(grep -E "^POWER_SUPPLY_CAPACITY=" /sys/class/power_supply/BAT*/uevent | sed -e s+'^POWER_SUPPLY_CAPACITY='++ | sort -rn | head -1)
if test -n "${BATT}"
then
    echo "Battery: ${BATT}%"
fi

# PAD Battery
for PADBAT in /sys/class/power_supply/*/device/uevent
do
    # HID devices only
    PADNAME=$(grep -E '^HID_NAME=' "${PADBAT}" | sed -e s+'^HID_NAME='++)
    if test -n "${PADNAME}"
    then
	# parent of parent / uevent
	BATTUEVENT=$(dirname "${PADBAT}")
	BATTUEVENT=$(dirname "${BATTUEVENT}")/uevent
	BATT=$(grep -E "^POWER_SUPPLY_CAPACITY=" "${BATTUEVENT}" | sed -e s+'^POWER_SUPPLY_CAPACITY='++ | sort -rn | head -1)
	echo "${PADNAME}: ${BATT}%"
    fi
done

# temperature
# Unit: millidegree Celsius
TEMPE=$(cat /sys/devices/virtual/thermal/thermal_zone*/temp 2>/dev/null | sort -rn | head -1 | sed -e s+"[0-9][0-9][0-9]$"++)
if test -n "${TEMPE}"
then
    echo "Temperature: ${TEMPE}°"
fi

echo "Architecture: ${V_ARCH}"
echo "System: ${V_SYSTEM}"
if test "${V_ARCH}" = "x86" -o "${V_ARCH}" = "x86_64"
then
    V_OPENGLVERSION=$(DISPLAY=:0.0 glxinfo | grep -E '^OpenGL core profile version string:' | sed -e s+'^OpenGL core profile version string:[ ]*'++)
    if test -z "${V_OPENGLVERSION}"
    then
	V_OPENGLVERSION=$(DISPLAY=:0.0 glxinfo | grep -E '^OpenGL version string:' | sed -e s+'^OpenGL version string:[ ]*'++)
    fi
    echo "OpenGL: ${V_OPENGLVERSION}"
fi
echo "Cpu model: ${V_CPUMODEL1}"
echo "Cpu number: ${V_CPUNB}"
if grep -q " avx2" /proc/cpuinfo
then
    echo "Cpu feature: avx2"
fi
