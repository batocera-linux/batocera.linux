#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/game-selected/dmd-simulator.sh" && exit 0

GSYSTEM=$1
GPATH=$2

txt2http() {
    sed -e s+"&"+"%26"+g
}

# stop any running sequence loop from a previous game selection
DMD_SEQ_PID="/tmp/dmd-sequence.pid"
if [ -f "$DMD_SEQ_PID" ]; then
    kill "$(cat "$DMD_SEQ_PID")" 2>/dev/null
    rm -f "$DMD_SEQ_PID"
fi

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

# Play files matching a glob pattern in sequence (name_1.gif, name_2.gif, ...)
# Returns 0 if at least one file was found, 1 otherwise
play_sequence() {
    FILES=$(find "/userdata/system/dmd/games/${GSYSTEM}" -maxdepth 1 -name "$1" 2>/dev/null | sort)
    test -z "$FILES" && return 1
    N=$(echo "$FILES" | wc -l)
    if [ "$N" -le 1 ]; then
	dmd-play ${DMDOPT} -f "$FILES"
    else
	(while true; do
	    echo "$FILES" | while read F; do
		dmd-play ${DMDOPT} --once -f "$F"
	    done
	done) &
	echo $! > "$DMD_SEQ_PID"
    fi
    return 0
}

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

# sequence matching (name_1.gif, name_2.gif, ...)
for EXT in gif png
do
    if play_sequence "${ROMBASE}_*.${EXT}"; then
	exit 0
    fi
done

# exact matching (normalized)
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

# sequence matching (normalized)
for EXT in gif png
do
    if play_sequence "${ROMMIN}_*.${EXT}"; then
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
