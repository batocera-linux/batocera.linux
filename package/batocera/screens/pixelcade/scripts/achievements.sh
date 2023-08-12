#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/achievements/pixelcade.sh" && exit 0

IMG="/userdata/system/pixelcade/achievements/achievements1.gif"
if test -e "${IMG}"
then
    timeout 2 wget -qO - "http://localhost:8080/path/stream?imagePath=${IMG}" && exit 0 # success
fi

# fallback : empty
timeout 2 wget -qO - "http://localhost:8080/text?t=WOUHOU !" || exit 1
exit 0
