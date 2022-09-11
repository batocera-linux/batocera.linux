#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import time
import signal

GPIO.setwarnings(False)                                 # no warnings
GPIO.setmode(GPIO.BCM)                                  # BCM mode
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # Powerbutton - GPIO on pin 5 is the GPIO 3 in BCM mode
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # Resetbutton - GPIO on pin 3 is the GPIO 2 in BCM mode 
GPIO.setup(4, GPIO.OUT)                                 # LED         - GPIO on pin 7 is the GPIO 4 in BCM mode
GPIO.output(4, GPIO.HIGH)                               # Turn on LED

def shutdownBatocera(channel):
    print ('shutdownBatocera')
    os.system('(sleep 2; shutdown -h now) &')
    #os.system('batocera-es-swissknife --shutdown &')
    blinkLED()
    
def exitAllBatoceraEmulator(channel):
    print ('exitAllBatoceraEmulator')
    os.system('killall -9 retroarch PPSSPPSDL reicast.elf mupen64plus x64 scummvm dosbox vice amiberry fsuae dolphin-emu')
    #os.system('batocera-es-swissknife --emukill')

def blinkLED():
    while True:
        GPIO.output(4, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(4, GPIO.HIGH)
        time.sleep(0.5)
    
GPIO.add_event_detect(2, GPIO.FALLING, callback=exitAllBatoceraEmulator,
                      bouncetime=1000)

GPIO.add_event_detect(3, GPIO.FALLING, callback=shutdownBatocera,
                      bouncetime=500)

while True:
    signal.pause()
