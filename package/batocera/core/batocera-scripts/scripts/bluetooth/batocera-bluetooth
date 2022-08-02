#!/bin/sh

ACTION=$1

do_help() {
    echo "${1} list" >&2
    echo "${1} trust" >&2
    echo "${1} trust-pad" >&2
    echo "${1} trust-audio" >&2
    echo "${1} starttrust" >&2
    echo "${1} stoptrust" >&2
    echo "${1} remove <device address>" >&2
    echo "${1} save" >&2
    echo "${1} restore" >&2
    echo "${1} live_devices" >&2
}

do_save() {
    BCK=/userdata/system/bluetooth/bluetooth.tar
    (cd /var/lib && tar cf "${BCK}" bluetooth)
}

do_restore() {
    BCK=/userdata/system/bluetooth/bluetooth.tar
    [ -f "${BCK}" ] && (cd /var/lib && tar xf "${BCK}")
}

do_list() {
    find /var/lib/bluetooth/ -type f -name info |
	while read FILE
	do
	    if grep -qE '^Trusted=true$' "${FILE}"
	    then
		DEVNAME=$(grep -E '^Name=' "${FILE}" | sed -e s+"^Name="++)
		DEVADDR=$(basename $(dirname "${FILE}"))
		echo "${DEVADDR} ${DEVNAME}"
	    fi
	done
}

do_remove() {
    DEV="${1}"

    # output is never nice
    (echo "untrust ${DEV}" ; echo "remove ${DEV}") | bluetoothctl >/dev/null 2>/dev/null
    find /var/lib/bluetooth -name "${DEV}" | while read X
    do
	rm -rf "${X}"
    done

    do_save # save
    return 0
}

do_devlist() {
    if ! > /var/run/bt_listing
    then
	exit 1
    fi

    NPID=$(cat /var/run/bluetooth-agent.pid)
    trap "kill -12 ${NPID} ; rm -f /var/run/bt_listing" 2 3

    kill -10 "${NPID}"
    # ok, not 10 lines should happen during this instant (between kill and tail)
    tail -f /var/run/bt_listing
}

do_trust() {
    TRUSTTYPE=$1
    NPID=$(cat /var/run/bluetooth-agent.pid)
    test -z "${NPID}" && return 0

    touch "/var/run/bt_status" || retrun 1
    LAST_MSG=$(cat "/var/run/bt_status")

    # empty, audio, pad
    if test "${TRUSTTYPE}" = "audio" -o "${TRUSTTYPE}" = "pad"
    then
	echo "${TRUSTTYPE}" > /var/run/bt_types || return 1
    else
	echo > /var/run/bt_types || return 1
    fi

    # trust device
    if echo "${TRUSTTYPE}" | grep -qE "^([0-9A-F]{2}:){5}[0-9A-F]{2}$"
    then
	echo "${TRUSTTYPE}" > /var/run/bt_device || return 1
    else
	echo "" > /var/run/bt_device || return 1
    fi

    # start discovering
    kill -10 "${NPID}"

    trap "kill -12 ${NPID}" 2 3

    N=60
    while test $N -gt 0
    do
	NEW_MSG=$(cat "/var/run/bt_status")
	if test "${LAST_MSG}" != "${NEW_MSG}"
	then
	    LAST_MSG="${NEW_MSG}"
	    echo "${NEW_MSG}"
	fi

	# check is in list and uniq trusting
	if echo "${TRUSTTYPE}" | grep -qE "^([0-9A-F]{2}:){5}[0-9A-F]{2}$"
	then
	    if do_list | grep -qE "^${TRUSTTYPE} "
	    then
		N=0
	    fi
	fi

	# wait
	test $N -gt 0 && sleep 1

	N=$((N-1))
    done

    # stop discovering
    kill -12 "${NPID}"

    do_save # save
}

do_starttrust() {
    NPID=$(cat /var/run/bluetooth-agent.pid)
    test -z "${NPID}" && return 0

    # start discovering
    kill -10 "${NPID}"
}

do_stoptrust() {
    NPID=$(cat /var/run/bluetooth-agent.pid)
    test -z "${NPID}" && return 0

    # stop discovering
    kill -12 "${NPID}"

    do_save # save
}

case "${ACTION}" in
    "list")
	do_list
	;;
    "trust")
	TRUSTTYPE=$2
	do_trust "${TRUSTTYPE}"
	;;
    "trust-audio")
	do_trust audio
	;;
    "trust-pad")
	do_trust pad
	;;
    "starttrust")
	do_starttrust
	;;
    "stoptrust")
	do_stoptrust
	;;
    "remove")
	if test $# = 2
	then
	    do_remove "${2}" || exit 1
	else
	    do_help "${0}"
	    exit 1
	fi
	;;
    "save")
	do_save
	;;
    "restore")
	do_restore
	;;
    "live_devices")
	do_devlist
	;;
    *)
	do_help "${0}"
	exit 1
esac

exit 0
