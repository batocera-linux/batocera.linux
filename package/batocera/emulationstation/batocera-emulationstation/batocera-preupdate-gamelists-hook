#!/bin/bash

if test -d "/usr/share/emulationstation/hooks"
then
    find "/usr/share/emulationstation/hooks" -name "preupdate-gamelists-*" |
	while read HOOK
	do
	    echo "hooking ${HOOK}" >&2
	    "${HOOK}"
	done
fi

