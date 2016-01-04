#!/bin/bash

killall bluetoothd 
bluetoothd -u

repeat=1
lag=5

while true
do
    let repeat++
    connected=`hcitool con | tail -n+2 | cut -f3 -d' ' 2>/dev/null`
    waitForMe=""
    for bt in $(cat /var/lib/bluetooth/*/hidd 2>/dev/null | cut -f 1 -d ' ')
    do
	skip=0
	for skipping in $connected; do
	    if [[ "$skipping" == "$bt" ]]; then
		skip=1
	    fi
	done

	[ "$skip" == "1" ] && continue
	hidd --connect $bt 2>/dev/null &
	waitForMe="$waitForMe $!"
    done

    for toWait in $waitForMe; do
	wait $toWait
    done
    
    if [[ "$repeat" -gt "10" ]];then
	lag=10
    fi

    sleep $lag
done
