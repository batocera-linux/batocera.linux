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

# custom
# exact matching
ROMBASE=$(basename "${GPATH}" | sed -e s+"\.[^\.]*$"++)
for EXT in gif png
do
    CUS="/userdata/system/dmd/games/${GSYSTEM}/${ROMBASE}.${EXT}"
    if test -e "${CUS}"
    then
	dmd-play ${DMDOPT} -f "${CUS}"
	exit 0
    fi
done

# exact matching
ROMMIN=$(echo "${ROMBASE}" | sed -e s+"([^)]*)"+""+g -e s+"[^A-Za-z0-9]"+""+g | tr A-Z a-z) # lowercase and remove any but a-z and 0-9, remove things in parenthesis
for EXT in gif png
do
    CUS="/userdata/system/dmd/games/${GSYSTEM}/${ROMMIN}.${EXT}"
    if test -e "${CUS}"
    then
	dmd-play ${DMDOPT} -f "${CUS}"
	exit 0
    fi
done

# marquee
GHASH=$(echo -n "${GPATH}" | md5sum | cut -c 1-32)
GMARQUEE=$(wget "http://localhost:1234/systems/${GSYSTEM}/games/${GHASH}?localpaths=true" -qO - | jq -r '.marquee')

if test -n "${GMARQUEE}" -a -e "${GMARQUEE}"
then
    dmd-play ${DMDOPT} -f "${GMARQUEE}"
    exit 0
fi

# fallback : name
GNAME=$(wget "http://localhost:1234/systems/${GSYSTEM}/games/${GHASH}?localpaths=true" -qO - | jq -r '.name' | txt2http)
if test -n "${GNAME}"
then
    dmd-play ${DMDOPT} -t "${GNAME}"
    exit 0
else
    # fallback : empty
    dmd-play ${DMDOPT} --clear
    exit 0
fi

