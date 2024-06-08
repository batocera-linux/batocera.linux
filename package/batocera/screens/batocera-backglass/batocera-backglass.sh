#!/bin/sh

#EVENTS="game-selected system-selected game-start game-end screensaver-start screensaver-stop"
EVENTS="game-selected system-selected"
PIDFILE="/var/run/batocera-backglass.pid"
PARAMSFILE="/var/run/batocera-backglass.params"

# unset these variables while they causes issues on my side for webkit
export WEBKIT_DISABLE_DMABUF_RENDERER=1
export __GLX_VENDOR_LIBRARY_NAME=
export __NV_PRIME_RENDER_OFFLOAD=
export __VK_LAYER_NV_optimus=

do_help() {
    echo "${1} enable <x> <y> <width> <height> <http location|theme>" >&2
    echo "${1} enable" >&2
    echo "${1} enable <http location|theme>" >&2
    echo "${1} restart" >&2
    echo "${1} restart <http location|theme>" >&2
    echo "${1} disable" >&2
    echo "${1} location <http location|theme name|empty for the default theme>" >&2
}

ACTION=$1
if test -z "${ACTION}"
then
    do_help "${0}"
    exit 1
fi

shift

isRunning() {
    if test -e "${PIDFILE}"
    then
	test -e "/proc/"$(cat "${PIDFILE}") && return 0
	return 1
    else
	return 1
    fi
}

getUrl() {
    THEME=$1
    test -z "${THEME}" && THEME=backglass-default

    # allow http:// or https:// urls
    if echo "${THEME}" | grep -qE '^http://|^https://'
    then
	THEMEPATH=${THEME}
    else
	THEMEPATH="/userdata/system/backglass/${THEME}/index.htm"
	if ! test -e "${THEMEPATH}"
	then
	    THEMEPATH="/usr/share/batocera-backglass/www/${THEME}/index.htm"
	fi

	# not found => the default one
	if ! test -e "${THEMEPATH}"
	then
	    THEMEPATH="/usr/share/batocera-backglass/www/backglass-default/index.htm"
	fi
    fi
    echo "${THEMEPATH}"
}

case "${ACTION}" in
    "location")
	LURL=$(getUrl "${1}")
	curl "http://localhost:2033/location?url=${LURL}"
	;;

    "enable")
	if isRunning
	then
	    echo "batocera-backglass is already running" >&2
	    exit 1
	fi

	if test $# -le 1 -a -f "${PARAMSFILE}" # ok, we can reuse the last used parameters (to make easy restart)
	then
	    read X Y WIDTH HEIGHT THEME < "${PARAMSFILE}"
	else
	    #
	    X=$1
	    Y=$2
	    WIDTH=$3
	    HEIGHT=$4
	    THEME=$5 # can be empty
	    shift
	    shift
	    shift
	    shift
	    if test -z "${X}" -o -z "${Y}" -o -z "${WIDTH}" -o -z "${HEIGHT}"
	    then
		echo "${0} X Y WIDTH HEIGHT"
		exit 1
	    fi
	    echo "${X} ${Y} ${WIDTH} ${HEIGHT} ${THEME}" > "${PARAMSFILE}" || exit 1
	fi

	### theme
	THEMEPATH=$(getUrl "${THEME}")
	###

	batocera-backglass-window --x "${X}" --y "${Y}" --width "${WIDTH}" --height "${HEIGHT}" --www "${THEMEPATH}" &
	echo "$!" > "${PIDFILE}"

	# add hooks
        for EVT in ${EVENTS}
        do
            mkdir -p /var/run/emulationstation/scripts/${EVT} || exit 1
            ln -sf /usr/share/batocera-backglass/scripts/${EVT}.sh /var/run/emulationstation/scripts/${EVT}/batocera-backglass.sh || exit 1
        done
    ;;

    "disable")
	if isRunning
	then
	    kill -15 $(cat "${PIDFILE}")
	    rm -f "${PIDFILE}"
	else
	    echo "batocera-backglass is already disabled" >&2
	    exit 1
	fi

	# remove hooks
        for EVT in ${EVENTS}
        do
            unlink /var/run/emulationstation/scripts/${EVT}/batocera-backglass.sh
        done
	;;

    "restart")
	if isRunning
	then
	    kill -15 $(cat "${PIDFILE}")
	    rm -f "${PIDFILE}"
	fi

	if test -f "${PARAMSFILE}"
	then
	    read X Y WIDTH HEIGHT THEME < "${PARAMSFILE}"
	fi

	# reread theme from configuration in case it changed
	THEME=$(batocera-settings-get backglass.theme)
	THEMEPATH=$(getUrl "${THEME}")

	batocera-backglass-window --x "${X}" --y "${Y}" --width "${WIDTH}" --height "${HEIGHT}" --www "${THEMEPATH}" &
	echo "$!" > "${PIDFILE}"
	;;

    "list-themes")
	(ls /usr/share/batocera-backglass/www; ls /userdata/system/backglass) 2>/dev/null | sort -u
	;;
esac
