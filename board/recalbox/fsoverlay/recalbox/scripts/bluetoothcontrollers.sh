#!/bin/bash
#Check if the firmware is alerady loaded
ps | grep -v grep | grep -q "hciattach /dev/ttyAMA0 bcm43xx 921600"
btPi3Running=$?
if [ -f /boot/bcm2710-rpi-3-b.dtb ] && [ $btPi3Running -ne 0 ]; then
    /usr/bin/hciattach /dev/ttyAMA0 bcm43xx 921600
fi

/usr/bin/hciconfig hci0 up piscan
/usr/bin/hciconfig hci0 name Recalbox
exit 0

