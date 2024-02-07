#!/bin/sh

STARTDBUS=
DBUSLAUNCH=/usr/bin/dbus-launch
VERBOSE=$1

if test -z "${VERBOSE}"
then
	EXTRA=""
else
	EXTRA="--verbose"
fi

if [ -z "$DBUS_SESSION_BUS_ADDRESS" ] && [ -x "$DBUSLAUNCH" ]; then
  STARTDBUS=yes
fi

if [ -n "$STARTDBUS" ]; then
  eval "$($DBUSLAUNCH --exit-with-session --sh-syntax)"
fi

if [ -n "$DBUS_SESSION_BUS_ADDRESS" ] && \
    [ -x "/usr/bin/dbus-update-activation-environment" ]; then
  # subshell so we can unset environment variables
  (
    # unset login-session-specifics
    unset XDG_SEAT
    unset XDG_SESSION_ID
    unset XDG_VTNR

    # tell dbus-daemon --session
    # to put the Xsession's environment in activated services'
    # environments
    dbus-update-activation-environment ${EXTRA} --all
  )
fi

if [ -z "$XDG_RUNTIME_DIR" ]; then
  export XDG_RUNTIME_DIR=/var/run
fi
