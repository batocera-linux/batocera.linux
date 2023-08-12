#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/screensaver-start/pixelcade.sh" && exit 0

timeout 2 wget -qO - "http://localhost:8080/path/stream?imagePath=/usr/share/pixelcade/images/system/batocera.png" && exit 0 # success

# fallback : empty
timeout 2 wget -qO - "http://localhost:8080/arcade/stream/black/dummy" || exit 1
exit 0
