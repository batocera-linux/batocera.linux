#!/bin/bash

# this configgen script leverages the S93amdtdp init.d and
# the batocera-amd-tdp scripts to allow adjustments to TDP
# of supported AMD CPUs. this can improve performance
# but also improve battery life.
#
# users can set a higher or lower manufacturer TDP accordingly.

log="/userdata/system/logs/amd-tdp.log"

# check we have a max system TDP value
CPU_TDP=$(/usr/bin/batocera-settings-get system.cpu.tdp)

# if not, we exit as the CPU is not supported by the TDP values
if [ -z "$CPU_TDP" ]; then
    echo "No CPU TDP value found."
    exit 0
fi

# set the final tdp value
set_tdp() {
    local TDP_VALUE=$1
    local ROM_NAME=$2

    if [ -z "${ROM_NAME}" ]; then
        echo "Setting AMD Mobile Processor TDP to ${TDP_VALUE} Watts" >> $log
    else
        echo "Game ${ROM_NAME} requested setting AMD Mobile Processor TDP to ${TDP_VALUE} Watts" >> $log
    fi

    /usr/bin/batocera-amd-tdp "$TDP_VALUE"
}

# determine the new TDP value based on max TDP
handle_tdp() {
    local TDP_PERCENTAGE=$1
    local ROM_NAME=$2

    # Check if TDP is defined and non-empty
    if [ -n "$CPU_TDP" ]; then
        # round the value up or down to make bash happy
        TDP_VALUE=$(awk -v max_tdp="$CPU_TDP" -v tdp_percentage="$TDP_PERCENTAGE" 'BEGIN { printf("%.0f\n", max_tdp * tdp_percentage / 100) }')
        set_tdp "${TDP_VALUE}" "${ROM_NAME}"
    else
        echo "A maximum TDP is not defined, cannot set TDP." >> $log
        exit 1
    fi
}

handle_game_stop() {
    TDP_SETTING=$(printf "%.0f" "$(/usr/bin/batocera-settings-get global.tdp)")
    if [ -z "${TDP_SETTING}" ]; then
        local CURRENT_TDP=$(ryzenadj -i | grep 'PPT LIMIT FAST' | awk '{printf "%.0f\n", $6}')

        if [[ "$CURRENT_TDP" =~ ^[0-9]+$ && "$CPU_TDP" =~ ^[0-9]+$ ]] && [ "$CURRENT_TDP" -ne "$CPU_TDP" ]; then
            set_tdp "${CPU_TDP}"
        fi
    else
        handle_tdp "${TDP_SETTING}"
    fi

    exit 0
}

handle_game_start() {
    local SYSTEM_NAME="$1"
    local ROM_PATH="$2"

    # Extract the base game name
    ROM_NAME="${ROM_PATH##*/}"

    # check for user set system specific setting
    if [ -n "${SYSTEM_NAME}" ]; then
        # check for rom specific config
        TDP_SETTING=$(/usr/bin/batocera-settings-get "${SYSTEM_NAME}[\"${ROM_NAME}\"].tdp")
        if [ -z "${TDP_SETTING}" ]; then
            TDP_SETTING="$(/usr/bin/batocera-settings-get ${SYSTEM_NAME}.tdp)"
        fi
    fi

    # If no user set system specific setting check for user set global setting
    if [ -z "${TDP_SETTING}" ]; then
        TDP_SETTING=$(printf "%.0f" "$(/usr/bin/batocera-settings-get global.tdp)")
    fi

    # now apply TDP percentage accordingly
    if [ -n "${TDP_SETTING}" ]; then
        handle_tdp "${TDP_SETTING}" "${ROM_NAME}"
    else
        echo "No TDP setting defined, cannot set TDP." >> $log
        exit 1
    fi
}

# Check for events
SYSTEM_NAME="$2"
ROM_PATH="$5"

case "$1" in
    gameStart)
        handle_game_start "$SYSTEM_NAME" "$ROM_PATH"
        ;;
    gameStop)
        handle_game_stop
        ;;
    *)
        exit 0
        ;;
esac

exit 0
