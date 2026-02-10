#!/bin/sh

PIDFILE="/var/run/batocera-controlcenter.pid"

getCCPID() {
    X=$(cat "${PIDFILE}" 2>/dev/null)
    test -z "${X}" && return 1

    # valiate that the pid is still running
    if test -e "/proc/${X}"; then
        echo "${X}"
        return 0
    fi
    return 1
}


FLAGS=
test "$1" = "hidden" && FLAGS="--hidden"

NB_SCREENS=$(batocera-resolution listOutputs | wc -l)
if [ "$NB_SCREENS" -ge 2 ]; then
	COMP=$(batocera-resolution getDisplayComp)
	if test "$COMP" = "labwc"; then
		RC=/userdata/system/.config/labwc/rc.xml
		BCC_SCREEN=$(grep -A5 "Batocera Control Center" "$RC" | grep output | sed 's,.*<output>[[:space:]]*\([[:alnum:]_-][[:alnum:]_-]*\)[[:space:]]*</output>.*,\1,')
		RESO=$(batocera-resolution --screen "$BCC_SCREEN" currentResolution)
		FLAGS="$FLAGS --window $RESO"
	fi
fi
PIDVALUE=$(getCCPID)
if test "$?" -eq 0; then
    # don't toogle if the hidden argument is given
    if test "$1" != "hidden"; then
        # toogle
        kill -10 "${PIDVALUE}"
    fi
else
    # switch on
    export DISPLAY=$(getLocalXDisplay)
    . /etc/profile.d/wayland.sh 2>/dev/null

    batocera-controlcenter-app ${FLAGS} 20 >/dev/null &
    echo "$!" >"${PIDFILE}"
fi
