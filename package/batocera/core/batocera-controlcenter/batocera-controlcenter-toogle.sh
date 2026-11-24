#!/bin/sh
# Shows or hides the control center; "hidden" starts it in the background at boot.

PIDFILE="/var/run/batocera-controlcenter.pid"

getCCPID() {
    X=$(cat "${PIDFILE}" 2>/dev/null)
    test -n "${X}" && test -e "/proc/${X}" && echo "${X}"
}

test "$(/usr/bin/batocera-settings-get bcc.disabled)" = "1" && exit 0

if test "$1" != "hidden"; then
    curl -sf --max-time 1 http://127.0.0.1:1234/controlcenter >/dev/null 2>&1 && exit 0
fi

PIDVALUE=$(getCCPID)
if test -n "${PIDVALUE}"; then
    # don't toggle if the hidden argument is given
    test "$1" = "hidden" || kill -USR1 "${PIDVALUE}"
    exit 0
fi

export DISPLAY=$(getLocalXDisplay)
if [ -f "/etc/profile.d/wayland.sh" ]; then
    . /etc/profile.d/wayland.sh
fi
export HOME=/userdata/system

settings_lang="$(/usr/bin/batocera-settings-get system.language)"
if test -n "${settings_lang}"; then
    export LC_ALL="${settings_lang}.UTF-8"
    export LANG="${LC_ALL}"
fi

FLAGS=
test "$1" = "hidden" && FLAGS="--controlcenter-hidden"

emulationstation --controlcenter ${FLAGS} --home /userdata/system >/dev/null 2>&1 &
echo "$!" >"${PIDFILE}"
