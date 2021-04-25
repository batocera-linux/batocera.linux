#!/bin/bash

case "${1}" in
    start)
	killall evmapy # in case one was remaining
	mkdir -p /var/run/evmapy || exit 1
	touch /var/run/evmapy/ready || exit 1
	inotifywait /var/run/evmapy/ready -t 5 -q & # wait the evmapy ready flag
	X=$!
	nohup evmapy &
	wait "${X}"
	exit 0
	;;
    stop)
	killall -9 evmapy # in case one was remaining
	exit 0
	;;
    clear)
	rm -rf /var/run/evmapy || exit 1
	mkdir /var/run/evmapy  || exit 1
	exit 0
	;;
esac
