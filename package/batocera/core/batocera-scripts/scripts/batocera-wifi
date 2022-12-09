#!/bin/sh

do_help() {
    echo "$0 scanlist" >&2
    echo "$0 list" >&2
}

do_list() {
    connmanctl services | sed 's/^...[ ]*//' | awk -F '[ ]*[ ]wifi_[[:alnum:]]*_' '{if (NF==2) print $1}' | sort -u # remove duplicates (a single wifi can appear under 2 interfaces)
}

do_scanlist() {
    connmanctl scan wifi >/dev/null 2>/dev/null
    do_list
}


if [ $# -eq 0 ]; then
	do_help
	exit 1
fi

ACTION=$1
shift

case "${ACTION}" in
    "list")
	do_list
	;;
    "scanlist")
	do_scanlist
	;;
    "start")
	/etc/init.d/S08connman restart
	;;
    "enable")
	batocera-settings-set wifi.enabled 1
	if [ "$#" -eq 2 ]; then
		batocera-settings-set wifi.ssid "$1"
		batocera-settings-set wifi.key "$2"
	fi
	/etc/init.d/S08connman reload

	# wait up to 5 sec for an IP address
	N=0
	ifconfig | grep "inet addr" | grep -qv "127\.0\.0\.1"
	while test $? -ne 0 -a $N -lt 10 # 10 tries
	do
		N=$((N+1))
		sleep 0.5
		ifconfig | grep "inet addr" | grep -qv "127\.0\.0\.1"
	done

	;;
    "disable")
	batocera-settings-set wifi.enabled 0
	/etc/init.d/S08connman reload
	;;
	*)
		do_help
		>&2 echo "error: invalid command ${ACTION}"
		exit 1
esac
exit 0
