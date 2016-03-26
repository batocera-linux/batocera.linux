import RPi.GPIO as GPIO
import os
import argparse

parser = argparse.ArgumentParser(description='power manager')
parser.add_argument("-m", help="mode onoff or push", type=str, required=True)
args = parser.parse_args()

mode = args.m

GPIO.setmode(GPIO.BCM)
# GPIO on pin 5 is the GPIO 3 in BCM mode
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shutdown():
  os.system("shutdown -h now")

try:
  if mode == "onoff" :
    GPIO.wait_for_edge(3, GPIO.RISING)
    shutdown()
  elif mode == "push":
    GPIO.wait_for_edge(3, GPIO.FALLING)
    shutdown()
  else:
    print("Unrecognized mode")
except KeyboardInterrupt:
    print ""

finally:
    print "cleaning up gpio"
    GPIO.cleanup()
