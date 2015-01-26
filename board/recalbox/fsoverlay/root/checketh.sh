#!/bin/sh

if [ "$ACTION" == "add" ] && [ "$INTERFACE" == "eth0" ]; then
	/usr/bin/logger eth0 woken up, bringing up interface
	/sbin/ifup eth0
fi


