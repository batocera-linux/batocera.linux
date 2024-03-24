#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/game-selected/dmd-simulator.sh" && exit 0

GSYSTEM=$1
GPATH=$2

txt2http() {
    sed -e s+"&"+"%26"+g
}

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

# marquee
GHASH=$(echo -n "${GPATH}" | md5sum | cut -c 1-32)
GMARQUEE=$(wget "http://localhost:1234/systems/${GSYSTEM}/games/${GHASH}?localpaths=true" -qO - | jq -r '.marquee')

if test -n "${GMARQUEE}" -a -e "${GMARQUEE}"
then
    dmd-play ${DMDOPT} -f "${GMARQUEE}" && exit 0 # success
fi

# fallback : name
GNAME=$(wget "http://localhost:1234/systems/${GSYSTEM}/games/${GHASH}?localpaths=true" -qO - | jq -r '.name' | txt2http)
if test -n "${GNAME}"
then
    dmd-play ${DMDOPT} -t "${GNAME}" --once --moving-text && exit 0 # success
fi

# fallback : empty
dmd-play ${DMDOPT} --clear || exit 1

exit 0

