#!/bin/bash

systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"
WAITMODE="`$systemsetting  -command load -key kodi.network.waitmode`"

# if the mode is required or wish,
# kodi waits for the network before starting
# in fact, it waits that an ip is available (such as a db service for example)
if test "${WAITMODE}" = "required" -o "${WAITMODE}" = "wish"
then
    WAITTIME="`$systemsetting  -command load -key kodi.network.waittime`"
    WAITHOST="`$systemsetting  -command load -key kodi.network.waithost`"

    DOCONT=1
    NWAITED=0
    while test "${DOCONT}" = 1
    do
	if ping -c 1 "${WAITHOST}" -W 3
	then
	    DOCONT=0
	else
	    sleep 1 # wait, in case the host is not correct
	    let NWAITED=$NWAITED+4
	    if test "${NWAITED}" -gt "${WAITTIME}"
	    then
		DOCONT=0
		if test "${WAITMODE}" = "required"
		then
		    exit 1
		fi
	    fi
	fi
    done
fi

LD_LIBRARY_PATH="/usr/lib/mysql" /usr/lib/kodi/kodi.bin --standalone -fs
