#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/achievements/dmd-simulator.sh" && exit 0

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

# fallback : empty
dmd-play ${DMDOPT} -t "WOUHOU !" --once --moving-text

exit 0
