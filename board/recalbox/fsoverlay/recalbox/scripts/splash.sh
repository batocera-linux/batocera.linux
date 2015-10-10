#!/bin/sh

if [[ "$1" == "shutdown" ]]; then
	sleep 1
	fbv -f -i /root/.splash/logo-wait.png &
else
	fbv -f -i /root/.splash/logo-loading.png &
fi
sleep 2
killall fbv
