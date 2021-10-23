#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import os
# Configuration
WAIT_TIME = 0.5  # [s] Time to wait between each refresh
sndVol = 0
sndVolOld = 0
hyst = 1
# Volume Controller
try:
    while 1:
        # Read Volume
        sndVolFile = open("/sys/kernel/xpi_gamecon/volume", "r")
        sndVol = int(sndVolFile.read())
        sndVolFile.close()
        if abs(sndVol - sndVolOld) > hyst:
            # Set Volume
            #sndSet = "amixer sset 'Headphone' " + str(sndVol) + "% > /dev/null"
            sndSet = "batocera-audio setSystemVolume " + str(sndVol)
            os.system(sndSet)

        sndVolOld = sndVol
        # Wait until next refresh
        time.sleep(WAIT_TIME)


# If a keyboard interrupt occurs (ctrl + c)
except KeyboardInterrupt:
    print("Sound ctrl interrupted by keyboard")
    sys.exit()
