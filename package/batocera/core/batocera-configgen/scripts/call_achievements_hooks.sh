#!/bin/sh

for D in /var/run/emulationstation/scripts/achievements /userdata/system/configs/emulationstation/scripts/achievements
do
    find -L "${D}" -type f | while read X
    do
	"${X}" "${1}" "${2}" "${3}"
    done
done
