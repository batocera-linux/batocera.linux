#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/achievements/pixelcade.sh" && exit 0

IMG="/userdata/system/pixelcade/achievements/achievements1.gif"
if test -e "${IMG}"
then
    if cp "${IMG}" "/userdata/system/pixelcade/system/load.gif"
    then
	timeout 2 wget -qO - "http://localhost:8080/arcade/stream/system/load.gif" && exit 0 # success
    fi
fi

# fallback : empty
timeout 2 wget -qO - "http://localhost:8080/text?t=WOUHOU !" || exit 1
exit 0
