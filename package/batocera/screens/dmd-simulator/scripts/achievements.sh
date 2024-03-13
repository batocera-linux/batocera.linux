#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/achievements/dmd-simulator.sh" && exit 0

# fallback : empty
dmd-play -t "WOUHOU !" --once --moving-text

exit 0
