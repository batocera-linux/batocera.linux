#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import os.path

# Configuration
WAIT_TIME = 5  # [s] Time to wait between each refresh
cpuTemp = 0
cpuTempOld = 0
hyst = 1
fphihi = 242
fphi = 194
fpmed = 147
fplo = 110
fplolo = 90
fpdefault = 75

#Read Fan.ini file
if os.path.isfile('/usr/share/piboy/fan.ini'):
	from configparser import ConfigParser
	config_object = ConfigParser()
	config_object.read("/usr/share/piboy/fan.ini")

	userinfo = config_object["FAN"]

	fphihi = (userinfo["75DegC"])
	fphi = (userinfo["70DegC"])
	fpmed = (userinfo["65DegC"])
	fplo = (userinfo["60DegC"])
	fplolo = (userinfo["55DegC"])
	fpdefault = (userinfo["50DegC"])

# Fan Controller
try:
    while 1:
        # Read CPU temperature
        cpuTempFile = open("/sys/class/thermal/thermal_zone0/temp", "r")
        cpuTemp = float(cpuTempFile.read()) / 1000
        cpuTempFile.close()
        if abs(cpuTemp - cpuTempOld) > hyst:
            # Calculate desired fan speed
            if cpuTemp >= 75:
                fanFile = open("/sys/kernel/xpi_gamecon/fan", "w")
                fanFile.write(str(fphihi))
                fanFile.close()
            elif cpuTemp >= 70:
                fanFile = open("/sys/kernel/xpi_gamecon/fan", "w")
                fanFile.write(str(fphi))
                fanFile.close()
            elif cpuTemp >= 65:
                fanFile = open("/sys/kernel/xpi_gamecon/fan", "w")
                fanFile.write(str(fpmed))
                fanFile.close()
            elif cpuTemp >= 60:
                fanFile = open("/sys/kernel/xpi_gamecon/fan", "w")
                fanFile.write(str(fplo))
                fanFile.close()
            elif cpuTemp >= 55:
                fanFile = open("/sys/kernel/xpi_gamecon/fan", "w")
                fanFile.write(str(fplolo))
                fanFile.close()
            else:
                fanFile = open("/sys/kernel/xpi_gamecon/fan", "w")
                fanFile.write(str(fpdefault))
                fanFile.close()
        cpuTempOld = cpuTemp
        # Wait until next refresh
        time.sleep(WAIT_TIME)

# If a keyboard interrupt occurs (ctrl   c)
except KeyboardInterrupt:
    sys.exit()
