import RPi.GPIO as GPIO
import time
import os
import thread

POWERPLUS = 3
RESETPLUS = 2
LED = 14

GPIO.setwarnings(False)		# no warnings
GPIO.setmode(GPIO.BCM)		# set up BCM GPIO numbering 
 
GPIO.setup(RESETPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO on pin 3 is the GPIO 2 in BCM mode
#to Reset+

GPIO.setup(POWERPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO on pin 5 is the GPIO 3 in BCM mode
#to Power+

GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, True)
# GPIO on pin 8 is the GPIO 14 in BCM mode
#to LED+

  
# Define a threaded callback function to run in another thread when events are detected  
def button_pressed(channel):
	if channel == POWERPLUS:
		speed=0.15
		shutdownstring="shutdown -h now"
	elif channel == RESETPLUS:
		speed=0.05
		shutdownstring="shutdown -r now"
	
	thread.start_new_thread( blink, (speed, ))
	flag=True
	pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
	os.system("/etc/init.d/S31emulationstation stop")
	while flag:
		flag = False
		for pid in pids:
				try:
					print pid
					commandpath = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
					if "emulationstation" in commandpath:
						flag = True
				except IOError:
					continue
	os.system(shutdownstring)
	#GPIO.cleanup()
	# no clean up as it was turning off the LED but anyway the system is shutting down
	quit()
	
def blink(speed):
	while True:  
			GPIO.output(LED, False)
			time.sleep(speed)
			GPIO.output(LED, True)
			time.sleep(speed)

GPIO.add_event_detect(RESETPLUS, GPIO.FALLING, callback=button_pressed)
GPIO.add_event_detect(POWERPLUS, GPIO.RISING, callback=button_pressed)
while True:
	time.sleep(0.2)
