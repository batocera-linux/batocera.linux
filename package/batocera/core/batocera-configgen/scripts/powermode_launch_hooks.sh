#!/bin/bash

if ! { [ -e /sys/devices/system/cpu/cpufreq/policy0/scaling_governor ] &&
       [ -e /sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors ]; }; then
    exit 0
fi

is_power_connected() {
    # Detect battery directory
    BATTERY_DIR=$(ls -d /sys/class/power_supply/*{BAT,bat}* 2>/dev/null | head -1)

    if [ -z "${BATTERY_DIR}" ]; then
        # If no battery directory, assume power supply is connected
        return 0
    fi

    # Check the battery status
    BATTERY_STATUS=$(cat "${BATTERY_DIR}/status" 2>/dev/null)

    if [[ "${BATTERY_STATUS}" == "Discharging" ]]; then
        # Battery is discharging
        return 1
    else
        # Battery is not discharging, assume power supply is connected
        return 0
    fi
}

handle_game_stop() {
    # Check if power connected
    if is_power_connected; then
        POWER_MODE="$(/usr/bin/batocera-settings-get-master global.powermode)"
    else
        POWER_MODE="$(/usr/bin/batocera-settings-get-master global.batterymode)"
    fi

    # Apply global power mode or fall back to default
    /usr/bin/batocera-power-mode "${POWER_MODE:-default}"
}

handle_game_start() {
    local SYSTEM_NAME="$1"
    local GAME_NAME="$2"

    # Extract the base game name
    GAME_NAME="${GAME_NAME##*/}"

    # Check for user set game-specific setting
    if [ -n "${GAME_NAME}" ]; then
        POWER_MODE_SETTING="${SYSTEM_NAME}[\"${GAME_NAME}\"].powermode"
        POWER_MODE="$(/usr/bin/batocera-settings-get-master "${POWER_MODE_SETTING}")"
    fi

    # If no user set game-specific setting, check for system-specific setting
    if [ -z "${POWER_MODE}" ] && [ -n "${SYSTEM_NAME}" ]; then
        POWER_MODE_SETTING="${SYSTEM_NAME}.powermode"
        POWER_MODE="$(/usr/bin/batocera-settings-get-master "${POWER_MODE_SETTING}")"
    fi

    # If no system-specific setting, check for global setting
    if [ -z "${POWER_MODE}" ]; then
        if is_power_connected; then
            POWER_MODE="$(/usr/bin/batocera-settings-get-master global.powermode)"
        else
            POWER_MODE="$(/usr/bin/batocera-settings-get-master global.batterymode)"
        fi
    fi

    # Apply power mode or fall back to default
    /usr/bin/batocera-power-mode "${POWER_MODE:-default}"
}

# Check for events
SYSTEM_NAME="$2"
GAME_NAME="$5"

case "$1" in
    gameStart)
        handle_game_start "$SYSTEM_NAME" "$GAME_NAME"
        ;;
    gameStop)
        handle_game_stop
        ;;
    *)
        exit 0
        ;;
esac

exit 0
