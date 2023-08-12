#!/bin/sh

# keep customizable
test -e "/userdata/system/configs/emulationstation/scripts/system-selected/pixelcade.sh" && exit 0

GSYSTEM=$1

txt2http() {
    sed -e s+"&"+"%26"+g
}

for EXT in gif png
do
    NORMAL="/userdata/system/pixelcade/console/${GSYSTEM}.${EXT}"
    if test -e "${NORMAL}"
    then
	timeout 2 wget -qO - "http://localhost:8080/path/stream?imagePath=${NORMAL}" && exit 0 # success
    fi
done

# fallback : marquee
LOGO=$(wget "http://localhost:1234/systems/${GSYSTEM}?localpaths=true" -qO - | jq -r '.logo')

if test -n "${LOGO}" -a -e "${LOGO}"
then
    if rm -f /userdata/system/pixelcade/system/load.*
    then
	EXT=$(echo "${LOGO}" | sed -e s+"^.*\.\([^\.]*\)$"+"\1"+)
	if test "${EXT}" = svg
	then
	    # use cache here...
	    CHASH=$(echo "${LOGO}" | md5sum | cut -c 1-32)
	    if test -e "/var/run/pixelcade/cache/${CHASH}.png"
	    then
		timeout 2 wget -qO - "http://localhost:8080/path/stream?imagePath=/var/run/pixelcade/cache/${CHASH}.png" && exit 0 # success
	    else
		mkdir -p "/var/run/pixelcade/cache"
		if convert -background black "${LOGO}" -resize 300x300 "/var/run/pixelcade/cache/${CHASH}.png" # try to cache
		then
		    timeout 2 wget -qO - "http://localhost:8080/path/stream?imagePath=/var/run/pixelcade/cache/${CHASH}.png" && exit 0 # success
		fi
	    fi
	else
	    timeout 2 wget -qO - "http://localhost:8080/path/stream?imagePath=${LOGO}" && exit 0 # success
	fi
    fi
fi

# fallback : name
GNAME=$(wget "http://localhost:1234/systems/${GSYSTEM}?localpaths=true" -qO - | jq -r '.fullname' | txt2http)
if test -n "${GNAME}"
then
    timeout 2 wget -qO - "http://localhost:8080/text?t=${GNAME}" && exit 0 # success
fi


# fallback : empty
timeout 2 wget -qO - "http://localhost:8080/arcade/stream/black/dummy" || exit 1
exit 0
