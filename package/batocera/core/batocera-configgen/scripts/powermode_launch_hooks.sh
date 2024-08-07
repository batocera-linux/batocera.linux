#!/bin/bash

if ! { [ -e /sys/devices/system/cpu/cpufreq/policy0/scaling_governor ] && 
       [ -e /sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors ]; }; then
    exit 0
fi

# Check if governor exists for CPU
check_governor() {
  local GOVERNOR_TO_CHECK=$1
  local AVAILABLE_GOVERNORS_PATH="/sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors"

  local AVAILABLE_GOVERNORS=$(cat "$AVAILABLE_GOVERNORS_PATH")

  if echo "$AVAILABLE_GOVERNORS" | grep -q "\b$GOVERNOR_TO_CHECK\b"; then
    return 0
  else
    return 1
  fi
}

# Set governor
set_governor() {
    local GOVERNOR_NAME=$1

    # Apply the governor to all policies
    for policy in /sys/devices/system/cpu/cpufreq/policy*; do
        if [ -e "$policy/scaling_governor" ]; then
            local CURRENT_GOVERNOR=$(cat "$policy/scaling_governor")
            if [ "$CURRENT_GOVERNOR" != "$GOVERNOR_NAME" ]; then
                echo $GOVERNOR_NAME > "$policy/scaling_governor" 2>/dev/null
            fi
        fi
    done
}

# Check if Energy Performance Preferences are available
epp_available() {
    if [ -e /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_available_preferences ]; then
        return 0
    else
        return 1
    fi
}

# Set EPP
set_epp() {
    local PREFERENCE=$1
    local AVAILABLE_PREFERENCES
    AVAILABLE_PREFERENCES=$(cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_available_preferences)

    # Check if the specified preference is available
    if ! echo "$AVAILABLE_PREFERENCES" | grep -q "\b$PREFERENCE\b"; then
        return 1
    fi

    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do
        if [ -e "$cpu" ]; then
            echo "$PREFERENCE" > "$cpu" 2>/dev/null
        fi
    done
}

is_power_connected() {
    # Detect battery
    BATTERY_DIR=$(ls -d /sys/class/power_supply/*{BAT,bat}* 2>/dev/null | head -1)
    BATT=$(cat ${BATTERY_DIR}/uevent 2>/dev/null | grep -E "^POWER_SUPPLY_CAPACITY=" | sed -e s+'^POWER_SUPPLY_CAPACITY='++ | sort -rn | head -1)
    PLUGGED=$(cat /sys/class/power_supply/*/online 2>/dev/null | grep -E "^1")
    if [ -n "${PLUGGED}" ]; then
        echo 1  # Power supply is connected
    elif [ -z "${BATT}" ]; then
        echo 1  # No battery detected, assume power supply is connected
    else
        echo 0  # Power supply is not connected
    fi
}

# Check for events
EVENT=$1
SYSTEM_NAME=$2
GAME_NAME=$5
GAME_NAME="${GAME_NAME##*/}"

# Exit if the event is neither gameStart nor gameStop
if [ "$EVENT" != "gameStart" ] && [ "$EVENT" != "gameStop" ]; then
    exit 0
fi

# Handle gameStop event
if [ "$EVENT" == "gameStop" ]; then
    POWER_CONNECTED=$(is_power_connected)
    if [[ "$POWER_CONNECTED" == 0 ]]; then
        POWER_MODE="$(/usr/bin/batocera-settings-get-master global.batterymode)"
    else
        POWER_MODE="$(/usr/bin/batocera-settings-get-master global.powermode)"
    fi
    if ! [ -z "${POWER_MODE}" ]; then
        /usr/bin/batocera-power-mode "${POWER_MODE}"
        exit 0
    fi
    SYSTEM_GOVERNOR="$(/usr/bin/batocera-settings-get-master system.cpu.governor)"
    if check_governor "$SYSTEM_GOVERNOR"; then
        set_governor "$SYSTEM_GOVERNOR"
		if epp_available; then
		    set_epp "default"
		fi
    fi    
    exit 0
fi

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
    POWER_CONNECTED=$(is_power_connected)
    if [[ "$POWER_CONNECTED" == 0 ]]; then
        POWER_MODE="$(/usr/bin/batocera-settings-get-master global.batterymode)"
    else
        POWER_MODE="$(/usr/bin/batocera-settings-get-master global.powermode)"
    fi
fi

# If a value is found, call the batocera-power-profile script
if ! [ -z "${POWER_MODE}" ]; then
    /usr/bin/batocera-power-mode "${POWER_MODE}"
    exit 0
fi

# If no value is found ensure governor is system default before exiting
SYSTEM_GOVERNOR="$(/usr/bin/batocera-settings-get-master system.cpu.governor)"
if check_governor "$SYSTEM_GOVERNOR"; then
    set_governor "$SYSTEM_GOVERNOR"
	if epp_available; then
	    set_epp "default"
	fi
fi
