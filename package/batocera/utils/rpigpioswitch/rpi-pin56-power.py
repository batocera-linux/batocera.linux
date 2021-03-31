#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import signal

GPIO.setwarnings(False)                             # no warnings
GPIO.setmode(GPIO.BCM)                              # BCM mode
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # GPIO on pin 5 is the GPIO 3 in BCM mode

def shutdownBatocera(channel):
    print ('shutdownBatocera')
    os.system('shutdown -h now')
    #os.system('batocera-es-swissknife --shutdown')

GPIO.add_event_detect(3, GPIO.FALLING, callback=shutdownBatocera,
                      bouncetime=500)

while True:
    signal.pause()
