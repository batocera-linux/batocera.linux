#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/screensaver-start/pixelcade.sh" && exit 0

if rm -f /userdata/system/pixelcade/system/load.*
then
    if cp "/usr/share/pixelcade/images/system/batocera.png" "/userdata/system/pixelcade/system/load.png"
    then
	timeout 2 wget -qO - "http://localhost:8080/arcade/stream/system/load.png" && exit 0 # success
    fi
fi

# fallback : empty
timeout 2 wget -qO - "http://localhost:8080/arcade/stream/black/dummy" || exit 1
exit 0
