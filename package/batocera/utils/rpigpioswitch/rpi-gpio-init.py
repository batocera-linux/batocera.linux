#!/usr/bin/env python2
# Required to initialize GPIO pins on RPi4
import RPi.GPIO as GPIO
if __name__ == '__main__':
     GPIO.setmode(GPIO.BCM)
     GPIO.setwarnings(False)
     btn_list = range(2,28)
     GPIO.setup(btn_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)
