#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/system-selected/dmd-simulator.sh" && exit 0

GSYSTEM=$1

txt2http() {
    sed -e s+"&"+"%26"+g
}

DMDOPT=
DMDFORMAT=$(batocera-settings-get dmd.format)
test "${DMDFORMAT}" = "hd" && DMDOPT="--hd"

# marquee
LOGO=$(wget "http://localhost:1234/systems/${GSYSTEM}?localpaths=true" -qO - | jq -r '.logo')

if test -n "${LOGO}" -a -e "${LOGO}"
then
    EXT=$(echo "${LOGO}" | sed -e s+"^.*\.\([^\.]*\)$"+"\1"+)
    if test "${EXT}" = svg
    then
	# use cache here...
	CHASH=$(echo "${LOGO}" | md5sum | cut -c 1-32)
	HPATH="/var/run/dmd-simulator/cache/${CHASH}.png"
	if test -e "${HPATH}"
	then
	    dmd-play ${DMDOPT} -f "${HPATH}" && exit 0 # success
	else
	    mkdir -p "/var/run/dmd-simulator/cache"
	    if convert -background black "${LOGO}" -resize 300x300 "${HPATH}" # try to cache
	    then
		dmd-play ${DMDOPT} -f "${HPATH}" && exit 0 # success
	    fi
	fi
    else
	dmd-play ${DMDOPT} -f "${LOGO}" && exit 0 # success
    fi
fi

# fallback : name
GNAME=$(wget "http://localhost:1234/systems/${GSYSTEM}?localpaths=true" -qO - | jq -r '.fullname' | txt2http)
if test -n "${GNAME}"
then
    dmd-play ${DMDOPT} -t "${GNAME}" && exit 0 # success
fi

# fallback : empty
dmd-play ${DMDOPT} --clear || exit 1
exit 0
