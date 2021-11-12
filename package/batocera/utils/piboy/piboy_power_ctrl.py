#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import os
# Configuration
WAIT_TIME = 1.0  # [s] Time to wait between each refresh
pwrctrl = 0
pwrctrlOld = 0
battctrl = 100
battctrlOld = 100
hyst = 1
# Power Switch
try:
    while 1:
        # Read Power Switch
        pwrctrlFile = open("/sys/kernel/xpi_gamecon/status", "r")
        pwrctrl = int(pwrctrlFile.read())
        pwrctrlFile.close()
        if abs(pwrctrl - pwrctrlOld) > hyst:
            if pwrctrl == 6:
                os.system("/etc/init.d/S31emulationstation stop && echo 0 > /sys/kernel/xpi_gamecon/flags && /sbin/rmmod xpi_gamecon && shutdown -h now")
            if pwrctrl == 134:
                os.system("/etc/init.d/S31emulationstation stop && echo 0 > /sys/kernel/xpi_gamecon/flags && /sbin/rmmod xpi_gamecon && shutdown -h now")
        pwrctrlOld = pwrctrl
        # Read Battery < 5% shutdown
        battctrlFile = open("/sys/kernel/xpi_gamecon/percent", "r")
        battctrl = int(battctrlFile.read())
        battctrlFile.close()
        if abs(battctrl - battctrlOld) > hyst:
            if battctrl <= 10:
                os.system("echo 20 > /sys/kernel/xpi_gamecon/green && echo 20 > /sys/kernel/xpi_gamecon/red")
            if battctrl <= 5:
                os.system("/etc/init.d/S31emulationstation stop && echo 0 > /sys/kernel/xpi_gamecon/flags && /sbin/rmmod xpi_gamecon && shutdown -h now")
        battctrlOld = battctrl
        # Wait until next refresh
        time.sleep(WAIT_TIME)

# If a keyboard interrupt occurs (ctrl   c)
except KeyboardInterrupt:
    sys.exit()
