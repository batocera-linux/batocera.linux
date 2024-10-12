#!/bin/bash

if test -z "${DISPLAY}"
then
    export DISPLAY=$(getLocalXDisplay)
fi

export XDG_CONFIG_HOME=/userdata/system/configs
export XDG_CONFIG_DIRS=/userdata/system/configs
export XDG_DATA_HOME=/userdata/saves/dreamcast
export FLYCAST_DATADIR=/userdata/saves/dreamcast
export FLYCAST_BIOS_PATH=/userdata/bios/dc 

/usr/bin/flycast
