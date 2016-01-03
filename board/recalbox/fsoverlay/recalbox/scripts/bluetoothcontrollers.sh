#!/bin/bash

killall bluetoothd 
bluetoothd -u

repeat=1
lag=5

while true; do
#for i in $(seq 1 $repeat); do
	repeat=$(($repeat+1))
	echo "$i try"
	connected=`hcitool con | tail -n+2 | cut -f3 -d' '`
	waitForMe=""
	for bt in `cat /var/lib/bluetooth/*/hidd | cut -f 1 -d ' '`;do
		echo "found that $bt has been paired" 
		skip=0
		for skipping in $connected; do
			if [[ "$skipping" == "$bt" ]]; then
				echo "$skipping is already connected"
				skip=1
			fi
		done
		[ "$skip" == "1" ] && continue
		echo "trying to connect $bt"
		hidd --connect $bt &
		waitForMe="$waitForMe $!"
	done
	echo "i will wait for $waitForMe"
	for toWait in $waitForMe; do
		wait $toWait
	done
	if [[ "$repeat" -gt "10" ]];then
		lag=10
	fi
	sleep $lag
done
