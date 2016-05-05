import RPi.GPIO as GPIO
import time
import os

POWERPLUS = 3
RESETPLUS = 2
LED = 14
  
GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering 
 
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
	for i in range(0,5):  
			blink(0.05)
	#GPIO.cleanup()
	# no clean up as it was turning off the LED but anyway the system is shutting down
	os.system("shutdown -r now")
	quit()
	
	
	
def blink(speed):
	GPIO.output(LED, False)
	time.sleep(speed)
	GPIO.output(LED, True)
	time.sleep(speed)


  

try:
	GPIO.add_event_detect(RESETPLUS, GPIO.FALLING, callback=button_pressed)
	GPIO.wait_for_edge(POWERPLUS, GPIO.RISING)
	for i in range(0,3):
			blink(0.15)
	os.system("shutdown -h now")
except KeyboardInterrupt:
	print ""
finally:
	#GPIO.cleanup()
	# no clean up as it was turning off the LED but anyway the system is shutting down
	print ""
