#!/bin/sh

PIDFILE="/var/run/batocera-controlcenter.pid"

getCCPID() {
    X=$(cat "${PIDFILE}" 2>/dev/null)
    test -z "${X}" && return 1

    # valiate that the pid is still running
    if test -e "/proc/${X}"
    then
	echo "${X}"
	return 0
    fi
    return 1
}

FLAGS=
test "$1" = "hidden" && FLAGS="--hidden"

PIDVALUE=$(getCCPID)
if test "$?" -eq 0
then
    # toogle
    kill -10 "${PIDVALUE}"
else
    # switch on
    export DISPLAY=$(getLocalXDisplay)
    . /etc/profile.d/wayland.sh 2>/dev/null

    batocera-controlcenter-app ${FLAGS} 20 >/dev/null &
    echo "$!" > "${PIDFILE}"
fi
