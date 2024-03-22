#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/screensaver-start/dmd-simulator.sh" && exit 0

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

dmd-play ${DMDOPT} -f "/usr/share/dmd-simulator/images/system/batocera.png" && exit 0 # success

dmd-play ${DMDOPT} -t "batocera" || exit 1

exit 0
