#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)                                 # no warnings
GPIO.setmode(GPIO.BCM)                                  # BCM mode
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # Powerbutton - GPIO on pin 5 is the GPIO 3 in BCM mode
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # Resetbutton - GPIO on pin 3 is the GPIO 5 in BCM mode 
GPIO.setup(4, GPIO.OUT)                                 # LED         - GPIO on pin 7 is the GPIO 4 in BCM mode
GPIO.output(4, GPIO.HIGH)                               # Turn on LED

def shutdownBatocera(channel):
    print 'shutdownBatocera'
    os.system('shutdown -h now')
    #os.system('batocera-es-swissknife --shutdown')
    
def exitAllBatoceraEmulator(channel):
    print 'exitAllBatoceraEmulator'
    os.system('killall -9 retroarch PPSSPPSDL reicast.elf mupen64plus linapple-pie x64 scummvm dosbox vice amiberry fsuae dolphin-emu')
    #os.system('batocera-es-swissknife --emukill')

GPIO.add_event_detect(3, GPIO.FALLING, callback=exitAllBatoceraEmulator,
                      bouncetime=500)

GPIO.add_event_detect(21, GPIO.FALLING, callback=shutdownBatocera,
                      bouncetime=500)

while True:
    time.sleep(0.2)
