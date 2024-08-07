#!/bin/bash

# Set mali gpu clock scaling mode, requires CONFIG_MALI_MIDGARD_DVFS=y
# Default 1
# 1: automatic adjustment
# 2: disable adjustment (all PP cores enabled and max clock)
# 3: turbo mode, running at the highest frequency
set_mali_gpu_scale() {
    if [ -e "/sys/class/mpgpu/scale_mode" ]; then
        echo $1 > "/sys/class/mpgpu/scale_mode"
    fi
}

# Check for events
EVENT=$1
SYSTEM_NAME=$2
GAME_NAME=$5
GAME_NAME="${GAME_NAME##*/}"

# Case selection for first parameter parsed, our event.
case $EVENT in
    gameStart)
        # Check for user set game specific setting
        if  [ -n "${GAME_NAME}" ]; then
            POWER_MODE_SETTING="${SYSTEM_NAME}[\"${GAME_NAME}\"].powermode"
            POWER_MODE="$(/usr/bin/batocera-settings-get-master "${POWER_MODE_SETTING}")"
        fi
        # If no user set game specific setting check for user set system specific setting
        if [ -z "${POWER_MODE}" ] && [ -n "${SYSTEM_NAME}" ]; then
            POWER_MODE_SETTING="${SYSTEM_NAME}.powermode"
            POWER_MODE="$(/usr/bin/batocera-settings-get-master "${POWER_MODE_SETTING}")"
        fi
        # If no user set system specific setting check for user set global setting
        if [ -z "${POWER_MODE}" ]; then
            POWER_MODE="$(/usr/bin/batocera-settings-get-master global.powermode)"
            if [ -z "${POWER_MODE}" ]; then
                set_mali_gpu_scale 1
                exit 0
            fi
        fi
        # Handle highperformance and balanced
        if [ "${POWER_MODE}" = "highperformance" ] || [ "${POWER_MODE}" = "balanced" ]; then
            set_mali_gpu_scale 2
        else
            set_mali_gpu_scale 1
        fi
    ;;
    gameStop)
        set_mali_gpu_scale 1
    ;;
esac
