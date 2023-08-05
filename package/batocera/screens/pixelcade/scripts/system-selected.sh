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
	    if test -e "/var/run/pixelcade/cache/${CHASH}"
	    then
		if cp "/var/run/pixelcade/cache/${CHASH}" "/userdata/system/pixelcade/system/load.png"
		then
		    wget -qO - "http://localhost:8080/arcade/stream/system/load.png" && exit 0 # success
		fi		    
	    else
		if convert -background black "${LOGO}" -resize 300x300 "/userdata/system/pixelcade/system/load.png"
		then
		    mkdir -p "/var/run/pixelcade/cache" && cp "/userdata/system/pixelcade/system/load.png" "/var/run/pixelcade/cache/${CHASH}" # try to cache
		    wget -qO - "http://localhost:8080/arcade/stream/system/load.png" && exit 0 # success
		fi
	    fi
	else
	    if cp "${LOGO}" "/userdata/system/pixelcade/system/load.${EXT}"
	    then
		wget -qO - "http://localhost:8080/arcade/stream/system/load.${EXT}" && exit 0 # success
	    fi  
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
