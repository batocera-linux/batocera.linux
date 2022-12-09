#!/bin/sh

D=$(find /sys/class/backlight/* 2>/dev/null | grep backlight | head -n1)
CYCLESTEP=20 # % additional brightbess at each step

if test ! -e "${D}"/brightness
then
    echo "no brightness found" >&2
    exit 1
else
    B="${D}"/brightness
    XMAX=$(cat "${D}"/max_brightness)
fi

setValue() {
    NEWVAL=$1
    XMAX=$2

    test "${NEWVAL}" -lt 0         && NEWVAL=0
    test "${NEWVAL}" -gt "${XMAX}" && NEWVAL="${XMAX}"
    
    echo "${NEWVAL}" > "${B}"
}

cycle() {
    X=$(cat "${B}")
    FVALUE=$(echo "scale=3;${X}" "*" "100" / "${XMAX}" | bc)
    LC_ALL=C FVALUE=$(printf '%.*f\n' 0 "${FVALUE}") # round
    NEWVAL=$(echo "${FVALUE} + ${CYCLESTEP}" | bc)
    [ "${NEWVAL}" -gt 100 ] && NEWVAL=0
    echo "Brightness cycling to ${NEWVAL}%"
    NEWVAL=$(expr "${NEWVAL}" "*" "${XMAX}" / 100)
    setValue "${NEWVAL}" "${XMAX}"
    exit 0
}

# get
if test $# = 0
then
    X=$(cat "${B}")
    FVALUE=$(echo "scale=3;${X}" "*" "100" / "${XMAX}" | bc)
    LC_ALL=C printf '%.*f\n' 0 "${FVALUE}" # round
    exit 0
fi

# set
if test $# = 1
then
    if [ "${1}" = "cycle" ]; then
       cycle
    else
       NEWVAL=$(expr "${1}" "*" "${XMAX}" / 100)
       setValue "${NEWVAL}" "${XMAX}"
       exit 0
    fi
fi

# set +
if test $# = 2
then
    X=$(cat "${B}")
    DELTA=$(expr "${2}" '*' ${XMAX} / 100)
    NEWVAL=$(expr "${X}" "${1}" "${DELTA}")
    setValue "${NEWVAL}" "${XMAX}"
    exit 0
fi

# help
echo "${0}"      >&2
echo "${0} + 10" >&2
echo "${0} - 20" >&2
echo "${0} cycle" >&2
exit 1
