#!/bin/sh

if [[ "$1" == "shutdown" ]]; then
	sleep 1
	fbv -f -i /recalbox/system/resources/splash/logo-wait.png &
else
	fbv -f -i /recalbox/system/resources/splash/logo-loading.png &
fi
sleep 2
killall fbv
