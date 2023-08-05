#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/game-selected/pixelcade.sh" && exit 0

GSYSTEM=$1
GPATH=$2

txt2http() {
    sed -e s+"&"+"%26"+g
}

BASENAME=$(basename "${GPATH}" | sed -e s+'\.[^\.]*$'++)
for EXT in gif png
do
    NORMAL="/userdata/system/pixelcade/${GSYSTEM}/${BASENAME}.${EXT}"
    if test -e "${NORMAL}"
    then
	if rm -f /userdata/system/pixelcade/system/load.*
	then
	    if cp "${NORMAL}" "/userdata/system/pixelcade/system/load.${EXT}"
	    then
		timeout 2 wget -qO - "http://localhost:8080/arcade/stream/system/load.${EXT}" && exit 0 # success
	    fi
	fi
    fi
done

# fallback : marquee
GHASH=$(echo -n "${GPATH}" | md5sum | cut -c 1-32)
GMARQUEE=$(wget "http://localhost:1234/systems/${GSYSTEM}/games/${GHASH}?localpaths=true" -qO - | jq -r '.marquee')

if test -n "${GMARQUEE}" -a -e "${GMARQUEE}"
then
    if rm -f /userdata/system/pixelcade/system/load.*
    then
	EXT=$(echo "${GMARQUEE}" | sed -e s+"^.*\.\([^\.]*\)$"+"\1"+)
	if cp "${GMARQUEE}" "/userdata/system/pixelcade/system/load.${EXT}"
	then
	    timeout 2 wget -qO - "http://localhost:8080/arcade/stream/system/load.${EXT}" && exit 0 # success
	fi
    fi
fi

# fallback : name
GNAME=$(wget "http://localhost:1234/systems/${GSYSTEM}/games/${GHASH}?localpaths=true" -qO - | jq -r '.name' | txt2http)
if test -n "${GNAME}"
then
    timeout 2 wget -qO - "http://localhost:8080/text?t=${GNAME}" && exit 0 # success
fi

# fallback : empty
timeout 2 wget -qO - "http://localhost:8080/arcade/stream/black/dummy" || exit 1
exit 0

