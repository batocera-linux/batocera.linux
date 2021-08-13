#!/bin/bash

es_add_game_begin() {
    echo "<gameList>" > /tmp/batocera-steam-update.tmp || return 1
}

es_add_game_end() {
    ES_SERVER="http://127.0.0.1:1234"

    echo "</gameList>" >> /tmp/batocera-steam-update.tmp || return 1
    curl -s -X POST -H "Content-type: application/x-www-form-urlencoded" -H "Accept: text/plain" "${ES_SERVER}/addgames/steam" -d "@/tmp/batocera-steam-update.tmp" > /dev/null || return 1
}

es_add_game() {
    GAME_BASENAME=$1
    GAME_NAME=$2
    GAME_IMAGE=$3

    (cat <<EOF
<game>
  <path>./${GAME_BASENAME}</path>
  <name>${GAME_NAME}</name>
  <desc></desc>
  <rating></rating>
  <releasedate></releasedate>
  <developer></developer>
  <publisher></publisher>
  <genre></genre>
  <players></players>
  <image>${GAME_IMAGE}</image>
  <manual></manual>
  <video></video>
</game>
EOF
) >> /tmp/batocera-steam-update.tmp || return 1
}

mkdir -p "/userdata/roms/steam" || exit 1

#if ! test -e "/userdata/roms/steam/Steam.steam"
#then
#   touch "/userdata/roms/steam/Steam.steam" || exit 1
#fi

# add applications
find /userdata/saves/flatpak/data/.var/app/com.valvesoftware.Steam/.local/share/applications -name "*.desktop" |
    (
N=0
es_add_game_begin || return 1
while read STEAMAPP
do
    if grep -qE '^[ ]*Categories[ ]*=.*Game.*$' "${STEAMAPP}" # game
    then
	BASEAPP=$(basename "${STEAMAPP}" | sed -e s+"\.desktop$"++)
	if ! test -e "/userdata/roms/steam/${BASEAPP}.steam"
	then
	    echo "adding ${BASEAPP}"
	    GAMEID=$(cat "${STEAMAPP}" | grep -E '^Exec=' | sed -e s+"Exec="++ -e s+"[ ]*steam[ ]*"++ | head -1)

	    # add image
	    ICON=$(grep -E "^Icon=" "${STEAMAPP}" | sed -e s+"^Icon=steam_icon_"++)_logo.png
	    IMGFILE="/userdata/saves/flatpak/data/.var/app/com.valvesoftware.Steam/.local/share/Steam/appcache/librarycache/${ICON}"
	    IMGARG=
	    if test -e "${IMGFILE}"
	    then
		IMGARG="./images/${BASEAPP}.png"
		mkdir -p "/userdata/roms/steam/images" || return 1
		cp "${IMGFILE}" "/userdata/roms/steam/${IMGARG}" || return 1
	    fi
	    # add game
	    echo "${GAMEID}" > "/userdata/roms/steam/${BASEAPP}.steam" || return 1

	    # add game in es
	    if ! es_add_game "${BASEAPP}.steam" "${BASEAPP}" "${IMGARG}"
	    then
		echo "adding game in es failed" >&2
		return 1
	    fi
	    let N++
	fi
    fi
done
test ${N} -gt 0 && es_add_game_end
)
exit 0
