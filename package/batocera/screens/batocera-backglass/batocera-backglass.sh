#!/bin/sh

#EVENTS="game-selected system-selected game-start game-end screensaver-start screensaver-stop"
EVENTS="game-selected system-selected"
PIDFILE="/var/run/batocera-backglass.pid"
PARAMSFILE="/var/run/batocera-backglass.params"

do_help() {
    echo "${1} enable <output_device> [theme]" >&2
    echo "${1} enable" >&2
    echo "${1} restart" >&2
    echo "${1} disable" >&2
    echo "${1} location <theme name>" >&2
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

getTheme() {
    THEME=$1
    test -z "${THEME}" && THEME=backglass-default
    echo "${THEME}"
}

case "${ACTION}" in
    "location")
        THEME=$(getTheme "${1}")
        curl -s "http://localhost:2033/location?url=${THEME}" >/dev/null
        ;;

    "enable")
        if isRunning
        then
            echo "batocera-backglass is already running" >&2
            exit 1
        fi

        # Load parameter cache or assign CLI arguments directly
	if test $# -le 1 -a -f "${PARAMSFILE}" # ok, we can reuse the last used parameters (to make easy restart)
	then
	    read -r X Y WIDTH HEIGHT THEME < "${PARAMSFILE}"
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
	    shift
	    if test -z "${X}" -o -z "${Y}" -o -z "${WIDTH}" -o -z "${HEIGHT}"
	    then
		echo "${0} X Y WIDTH HEIGHT"
		exit 1
	    fi
	    echo "${X} ${Y} ${WIDTH} ${HEIGHT} ${THEME}" > "${PARAMSFILE}" || exit 1
	fi

        # Fire background native renderer directly to the targeted connector display
        batocera-backglass-window -x "${X}" -y "${Y}" --width "${WIDTH}" --height "${HEIGHT}" --www "${THEME}" &
        echo "$!" > "${PIDFILE}"

        # Register hook scripts directly inside EmulationStation
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

        # Clean script links
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
	    read -r X Y WIDTH HEIGHT THEME < "${PARAMSFILE}"
        fi

        # Pull system settings overrides if chosen
        THEME=$(batocera-settings-get backglass.theme)
        THEME=$(getTheme "${THEME}")

        # Update params cache
	echo "${X} ${Y} ${WIDTH} ${HEIGHT} ${THEME}" > "${PARAMSFILE}" || exit 1

        # Launch again with the native configuration target parameters
        batocera-backglass-window -x "${X}" -y "${Y}" --width "${WIDTH}" --height "${HEIGHT}" --www "${THEME}" &
        echo "$!" > "${PIDFILE}"
        ;;

    "list-themes")
        # Direct list of the built-in C++ native renderer presets and optional custom configurations
        echo "backglass-default"
        echo "backglass-boxart"
        echo "backglass-fanart"
        echo "backglass-image"
        echo "backglass-marquee"
        ;;
esac
