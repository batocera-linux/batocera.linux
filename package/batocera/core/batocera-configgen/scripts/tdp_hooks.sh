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
    echo "Game ${2} requested setting AMD Mobile Processor TDP to ${1} Watts" >> $log
    /usr/bin/batocera-amd-tdp $1
}

# determine the new TDP value based on max TDP
handle_tdp() {
    TDP_PERCENTAGE=$1
    ROM_NAME=$2
    MAX_TDP=$(/usr/bin/batocera-settings-get system.cpu.tdp)
    # Check if MAX_TDP is defined and non-empty
    if [ -n "$MAX_TDP" ]; then
        # round the value up or down to make bash happy
        TDP_VALUE=$(awk -v max_tdp="$MAX_TDP" -v tdp_percentage="$TDP_PERCENTAGE" 'BEGIN { printf("%.0f\n", max_tdp * tdp_percentage / 100) }')
        set_tdp "${TDP_VALUE}" "${ROM_NAME}"
    else
        echo "A maximum TDP is not defined, cannot set TDP." >> $log
        exit 1
    fi
}

# Check for events
EVENT=$1
SYSTEM_NAME=$2
ROM_PATH=$5

# Get the rom name from ROM_PATH
ROM_NAME=$(basename "$ROM_PATH")

# exit accordingly if the event is neither gameStart nor gameStop
if [ "$EVENT" != "gameStart" ] && [ "$EVENT" != "gameStop" ]; then
    exit 0
fi

# handle gameStop event
if [ "$EVENT" == "gameStop" ]; then
    # set either user global setting or default tdp
    TDP_SETTING=$(printf "%.0f" "$(/usr/bin/batocera-settings-get global.tdp)")
    if [ -z "${TDP_SETTING}" ]; then
        TDP_SETTING="$(/usr/bin/batocera-settings-get system.cpu.tdp)"
        
        if [ -n "$TDP_SETTING" ]; then
            set_tdp "${TDP_SETTING}" "STOP"
        else
            echo "No TDP setting defined, cannot set TDP." >> $log
            exit 1
        fi
        exit 0
    fi
    handle_tdp "${TDP_SETTING}" "STOP"
    exit 0
fi

# run through determining the desired TDP setting
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

# If no value is found ensure tdp is default before exiting
if [ -z "${TDP_SETTING}" ]; then
    TDP_SETTING="$(/usr/bin/batocera-settings-get-master system.cpu.tdp)"
    if [ -n "${TDP_SETTING}" ]; then
        set_tdp "${TDP_SETTING}" "${ROM_NAME}"
    else
        echo "No TDP setting defined, cannot set TDP." >> $log
        exit 1
    fi    
    exit 0
fi

# now apply TDP percentage accordingly
if [ -n "${TDP_SETTING}" ]; then
    handle_tdp "${TDP_SETTING}" "${ROM_NAME}"
else
    echo "No TDP setting defined, cannot set TDP." >> $log
    exit 1
fi
