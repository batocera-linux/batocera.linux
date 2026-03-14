#!/bin/bash

#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#

# this configgen script leverages the S93amdtdp init.d and
# the batocera-amd-tdp scripts to allow adjustments to TDP
# of supported AMD CPUs. this can improve performance
# but also improve battery life.
#
# users can set a higher or lower manufacturer TDP accordingly.

log="/userdata/system/logs/amd-tdp.log"
STATE_FILE="/var/run/amd-tdp.changed"

# Check we have a max system TDP value
CPU_TDP=$(/usr/bin/batocera-settings-get system.cpu.tdp)

# If not, we exit as the CPU is not supported by the TDP values
if [ -z "$CPU_TDP" ]; then
    echo "No CPU TDP value found."
    exit 0
fi

# Set the final tdp value
set_tdp() {
    local TDP_VALUE=$1
    local ROM_NAME=$2

    echo "Game ${ROM_NAME} requested setting AMD Processor TDP to ${TDP_VALUE} Watts" >> $log

    /usr/bin/batocera-amd-tdp "$TDP_VALUE"
}

# Determine the new TDP value based on max TDP
handle_tdp() {
    local TDP_PERCENTAGE=$1
    local ROM_NAME=$2

    local MAX_TDP
    MAX_TDP=$(/usr/bin/batocera-settings-get system.cpu.tdp)

    # Check if TDP is defined and non-empty
    if [ -z "$MAX_TDP" ]; then
        echo "A maximum TDP is not defined, cannot set TDP." >> $log
        exit 1
    fi

    # Round the value up or down to make bash happy
    local TDP_VALUE
    TDP_VALUE=$(awk -v max_tdp="$MAX_TDP" -v tdp_percentage="$TDP_PERCENTAGE" 'BEGIN { printf("%.0f\n", max_tdp * tdp_percentage / 100) }')
    set_tdp "${TDP_VALUE}" "${ROM_NAME}"
}

do_game_start() {
    local SYSTEM_NAME="$1"
    local ROM_NAME="$2"
    local TDP_SETTING=""
    local RAW_GLOBAL=""

    # Clear previous state file if present
    rm -f "$STATE_FILE" 2>/dev/null

    # Check for user set rom or system specific setting
    if [ -n "${SYSTEM_NAME}" ]; then
        TDP_SETTING=$(/usr/bin/batocera-settings-get "${SYSTEM_NAME}[\"${ROM_NAME}\"].tdp")
        [ -z "$TDP_SETTING" ] && TDP_SETTING=$(/usr/bin/batocera-settings-get "${SYSTEM_NAME}.tdp")
    fi

    # If no user set system specific setting check for user set global setting
    if [ -z "${TDP_SETTING}" ]; then
        RAW_GLOBAL=$(/usr/bin/batocera-settings-get global.tdp)
        if [ -n "${RAW_GLOBAL}" ]; then
            TDP_SETTING=$(printf "%.0f" "${RAW_GLOBAL}")
        fi
    fi

    # Now apply TDP percentage accordingly
    if [ -n "${TDP_SETTING}" ]; then
        handle_tdp "${TDP_SETTING}" "${ROM_NAME}"
        : > "$STATE_FILE"
    else
        echo "Game START, but no TDP setting defined. Leaving TDP unchanged." >> $log
        echo "" >> "$log"
        echo "*** ------------------------------------- ***" >> "$log"
        echo "" >> "$log"
        exit 0
    fi
}

do_game_stop() {
    # Check if we actually changed anything on game start
    if [ ! -e "$STATE_FILE" ]; then
        echo "Game STOP, but no prior TDP change. Nothing to do." >> "$log"
        echo "" >> "$log"
        echo "*** ------------------------------------- ***" >> "$log"
        echo "" >> "$log"
        exit 0
    fi

    local RAW_GLOBAL
    RAW_GLOBAL=$(/usr/bin/batocera-settings-get global.tdp)

    if [ -n "${RAW_GLOBAL}" ]; then
        TDP_SETTING=$(printf "%.0f" "${RAW_GLOBAL}")
        handle_tdp "$TDP_SETTING" "STOP"
    else
        local SYSTEM_TDP
        SYSTEM_TDP=$(/usr/bin/batocera-settings-get system.cpu.tdp)
        if [ -n "$SYSTEM_TDP" ]; then
            set_tdp "$SYSTEM_TDP" "STOP"
        else
            echo "No default TDP setting defined, cannot set TDP on game stop." >> $log
            exit 1
        fi
    fi

    rm -f "$STATE_FILE" 2>/dev/null
    exit 0
}

# Check for events
SYSTEM_NAME="$2"
ROM_PATH="$5"

# Get the rom name from ROM_PATH
ROM_NAME=$(basename "$ROM_PATH")

case "$1" in
    gameStart)
        do_game_start "$SYSTEM_NAME" "$ROM_NAME"
        ;;
    gameStop)
        do_game_stop
        ;;
    *)
        exit 0
        ;;
esac

exit 0
