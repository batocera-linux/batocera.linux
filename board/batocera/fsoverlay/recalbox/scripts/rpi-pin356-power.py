#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# GPIO on pin 5 is the GPIO 3 in BCM mode


def exitAllBatoceraEmulator(channel):
    print 'exitAllBatoceraEmulator'
    os.system('killall -9 retroarch PPSSPPSDL reicast.elf mupen64plus linapple-pie x64 fba2x scummvm dosbox advmame pifba vice amiberry fsuae dolphin-emu')


GPIO.add_event_detect(3, GPIO.FALLING, callback=exitAllBatoceraEmulator,
                      bouncetime=500)

while True:
    time.sleep(0.2)
