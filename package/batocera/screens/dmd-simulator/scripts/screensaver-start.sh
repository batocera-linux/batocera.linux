#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/screensaver-start/dmd-simulator.sh" && exit 0

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

# custom
for EXT in gif png
do
    CUS="/userdata/system/dmd/screensaver.${EXT}"
    if test -e "${CUS}"
    then
	dmd-play ${DMDOPT} -f "${CUS}"
	exit 0
    fi
done

dmd-play ${DMDOPT} -f "/usr/share/dmd-simulator/images/system/batocera.png"
exit 0
