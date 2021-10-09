#!/bin/bash

GAME=$1

DISPLAY=:0.0 unclutter-remote -s

# bad hack in a first time to get audio for user batocera                                                                                                                                          
chown -R root:audio /var/run/pulse
chmod -R g+rwX /var/run/pulse

if test -z "${GAME}"
then
    su - batocera -c "DISPLAY=:0.0 flatpak run com.valvesoftware.Steam"
else
    su - batocera -c "DISPLAY=:0.0 flatpak run com.valvesoftware.Steam -silent ${GAME}" 2>&1 |
	while read LINE
	do
	    echo "${LINE}"
	    # steam has no option to exit when quitting a game.
	    if echo "${LINE}" | grep -E '^Exiting app |^Game process removed'
	    then
		su - batocera -c "DISPLAY=:0.0 flatpak run com.valvesoftware.Steam -shutdown"
	    fi
	done
fi
DISPLAY=:0.0 unclutter-remote -h
