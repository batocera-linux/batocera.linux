#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/screensaver-start/dmd-simulator.sh" && exit 0

dmd-play -f "/usr/share/dmd-simulator/images/system/batocera.png" && exit 0 # success

dmd-play -t "batocera" || exit 1

exit 0
