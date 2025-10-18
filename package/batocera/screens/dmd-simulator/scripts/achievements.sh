#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/achievements/dmd-simulator.sh" && exit 0

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

# custom
for EXT in gif png
do
    CUS="/userdata/system/dmd/achievement.${EXT}"
    if test -e "${CUS}"
    then
	dmd-play ${DMDOPT} -f "${CUS}" --once --overlay
	exit 0
    fi
done

# fallback : empty
dmd-play ${DMDOPT} -t "WOUHOU !" --once --moving-text --overlay

exit 0
