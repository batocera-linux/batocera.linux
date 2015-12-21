#!/bin/bash
log=/recalbox/share/system/logs/controllers.log
"ps3 usb controller detected" >> $log
sixpair >> $log
if [[ "$?" != "0" ]];then
	bluetoothd --udev &
	sleep 3
	sixpair >> $log
	killall bluetoothd
fi
