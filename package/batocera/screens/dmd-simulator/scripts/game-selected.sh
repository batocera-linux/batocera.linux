#!/bin/bash

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
# same name : we accept same name + .png/.gif
ROMBASE=$(basename "${GPATH}" | sed -e s+"\.[^\.]*$"++)
FOUNDCUS=
for EXT in gif png
do
    CUS="/userdata/system/dmd/games/${GSYSTEM}/${ROMBASE}.${EXT}"
    if test -e "${CUS}"
    then
	FOUNDCUS="${CUS}"
    fi
done

# minimized name : we accept : minimized name + .png/.gif and minimized name + _ + numbers + .gif/.png
ROMMIN=$(echo "${ROMBASE}" | sed -e s+"([^)]*)"+""+g -e s+"[^A-Za-z0-9]"+""+g | tr A-Z a-z) # lowercase and remove any but a-z and 0-9, remove things in parenthesis

if test "${ROMBASE}" = "${ROMMIN}"
then
    # ignore the image found on the rombase name to avoid duplicated images
    FOUNDCUS=
fi

CUSS=
while read X
do
    test -n "${CUSS}" && CUSS="${CUSS}:"
    CUSS=${CUSS}${X}
done < <(
    # first the same name image
    test -n "${FOUNDCUS}" && echo "${FOUNDCUS}"
    # second, the minimized name without numbers
    find "/userdata/system/dmd/games/${GSYSTEM}" -maxdepth 1 -type f -regextype posix-extended -regex ".*/${ROMMIN}\.(gif|png)$"
    # third, the minimized name with numbers
    find "/userdata/system/dmd/games/${GSYSTEM}" -maxdepth 1 -type f -regextype posix-extended -regex ".*/${ROMMIN}_[0-9]+\.(gif|png)$" | sort -V)
if test -n "${CUSS}"
then
    dmd-play ${DMDOPT} -f "${CUSS}"
    exit 0
fi

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

