#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import os
import subprocess
from multiprocessing import Process

#initialize pins
powerPin = 26
powerenPin = 27

#initialize GPIO settings
def init():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(powerPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(powerenPin, GPIO.OUT)
	GPIO.output(powerenPin, GPIO.HIGH)

#waits for user to hold button up to 1 second before issuing poweroff command
def poweroff():
	while True:
		GPIO.wait_for_edge(powerPin, GPIO.FALLING)
		output = int(subprocess.check_output(['batocera-es-swissknife', '--espid']))
		if output:
			os.system("batocera-es-swissknife --emukill")
			os.system("batocera-es-swissknife --shutdown")
		else:
			os.system("shutdown -h now")

if __name__ == "__main__":
	#initialize GPIO settings
	init()
	#create a multiprocessing.Process instance for each function to enable parallelism 
	powerProcess = Process(target = poweroff)
	powerProcess.start()

	powerProcess.join()
