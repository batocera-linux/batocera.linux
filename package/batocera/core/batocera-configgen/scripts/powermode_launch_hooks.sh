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

# Determine which governors to set based on powermode setting
handle_powermode() {
	local POWERMODE_NAME=$1
		case "$POWERMODE_NAME" in
			"highperformance")
				set_governor "performance"
				;;
			"balanced")
				if check_governor "schedutil"; then
					set_governor "schedutil"
				# If 'schedutil' is not available, check for 'ondemand' governor
				elif check_governor "ondemand"; then
					set_governor "ondemand"
				# If neither are available, fall back to 'performance'
				else
					set_governor "performance"
				fi
				;;
			"powersaver")
				set_governor "powersave"
				;;
			*)
		esac				
}

# Check for events
EVENT=$1
SYSTEM_NAME=$2

# Exit if the event is neither gameStart nor gameStop
if [ "$EVENT" != "gameStart" ] && [ "$EVENT" != "gameStop" ]; then
    exit 0
fi

# Handle gameStop event
if [ "$EVENT" = "gameStop" ]; then
    SYSTEM_GOVERNOR="$(/usr/bin/batocera-settings-get system.cpu.governor)"
    set_governor "$SYSTEM_GOVERNOR"
	exit 0
fi

# Check for user set system specific setting
if [ -n "${SYSTEM_NAME}" ]; then
    POWER_MODE_SETTING="${SYSTEM_NAME}.powermode"
    POWER_MODE="$(/usr/bin/batocera-settings-get-master "${POWER_MODE_SETTING}")"
fi

# If no user set system specific setting check for user set global setting
if [ -z "${POWER_MODE}" ]; then
    POWER_MODE="$(/usr/bin/batocera-settings-get-master global.powermode)"
fi

# If no user set system or global setting try default user setting if exists
if [ -z "${POWER_MODE}" ]; then
    POWER_MODE="$(/usr/bin/batocera-settings-get system.cpu.governor)"
fi

# Finally, use the master setting if no user settings
if [ -z "${POWER_MODE}" ]; then
    POWER_MODE="$(/usr/bin/batocera-settings-get-master system.cpu.governor)"
fi

# If no value is found exit
if [ -z "${POWER_MODE}" ]; then
    exit 0
fi

# select powermode
if ! [ -z "${POWER_MODE}" ]; then
	handle_powermode "${POWER_MODE}"
fi
