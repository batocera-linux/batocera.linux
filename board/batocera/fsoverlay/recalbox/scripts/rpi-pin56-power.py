#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# GPIO on pin 5 is the GPIO 3 in BCM mode


def shutdownBatocera(channel):
    print 'shutdownBatocera'
    os.system('shutdown -h now')


GPIO.add_event_detect(3, GPIO.FALLING, callback=shutdownBatocera,
                      bouncetime=500)

while True:
    time.sleep(0.2)
