#!/usr/bin/env python2
"""
Argon One Fan Service Daemon
Original source: https://github.com/Elrondo46/argonone
@lbrpdx - Modified to run on Batocera

Make sure to add in /boot/config.txt:
 dtparam=i2c_arm=on
 dtparam=i2c-1=on

(it should be installed by Batocera when you enable 
Argon One support case)

This daemon is launched through /etc/init.d/S92switch

In order to configure your own temperature/fan mapping
edit a file /userdata/system/configs/argonone.conf with:

# temperatures are in Celsius
# fan_speed are from 0-100 percent of max speed
# syntax is: temp_threashold=fan_speed
# default is:
# 45=0
# 55=10
# 60=55
# 65=100

In this script, put the following parameter
FORCE_REBOOT=1
In order to force a reboot on double click (by default
double click kills the current emulator and returns to
EmulationStation menu)
"""
import smbus
import RPi.GPIO as GPIO
import os
import time
import sys
from threading import Thread

# Choose 0 (kill emulator) or 1 (force reboot) on double click
FORCE_REBOOT=0

config_file='/userdata/system/configs/argonone.conf'
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    try:
        bus = smbus.SMBus(1)
    except:
        print("Fatal error: No Argon One case or kernel modules not loaded. Exiting now.")
        exit()
else:
    bus = smbus.SMBus(0)

address = 0x1a
shutdown_pin=4
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(shutdown_pin, GPIO.IN,  pull_up_down=GPIO.PUD_DOWN)

def get_fanspeed(tempval, configlist):
    for curconfig in configlist:
        curpair = curconfig.split("=")
        tempcfg = float(curpair[0])
        fancfg = int(float(curpair[1]))
        if tempval >= tempcfg:
            return fancfg
    return 0

def load_config(fname):
    newconfig = []
    try:
        with open(fname, "r") as fp:
            for curline in fp:
                if not curline:
                    continue
                tmpline = curline.strip()
                if not tmpline:
                    continue
                if tmpline[0] == "#":
                    continue
                tmppair = tmpline.split("=")
                if len(tmppair) != 2:
                    continue
                tempval = 0
                fanval = 0
                try:
                    tempval = float(tmppair[0])
                    if tempval < 0 or tempval > 100:
                        continue
                except:
                    continue
                try:
                    fanval = int(float(tmppair[1]))
                    if fanval < 0 or fanval > 100:
                        continue
                except:
                    continue
                newconfig.append("{:5.1f}={}".format(tempval, fanval))
        if len(newconfig) > 0:
            newconfig.sort(reverse=True)
    except:
        return []
    return newconfig


def temp_check():
    check_interval=15 # seconds between two temp changes
    fanconfig =  ["65=100", "60=55", "55=10", "45=0"] # Default values when no config file
    tmpconfig = load_config(config_file)
    if len(tmpconfig) > 0:
        fanconfig = tmpconfig
    prevblock = 0
    while True:
        temp = open("/sys/class/thermal/thermal_zone0/temp","r").readline()
        val = float(int(temp)/1000)
        # print (val)
        block = get_fanspeed(val, fanconfig)
        if block < prevblock:
            time.sleep(check_interval)
        prevblock = block
        try:
            bus.write_byte_data(address,0,block)
        except IOError:
            temp = ""
        time.sleep(check_interval)

def shutdown_check():
    while True:
        pulsetime = 1
        GPIO.wait_for_edge(shutdown_pin, GPIO.RISING)
        time.sleep(0.01)
        while GPIO.input(shutdown_pin) == GPIO.HIGH:
            time.sleep(0.01)
            pulsetime += 1
        if pulsetime >=2 and pulsetime <=3:
            if FORCE_REBOOT == 1:
                try:
                    # force fan stop (but not board power off)
                    bus.write_byte_data(address,0,0x00)
                except:
                    print ("Could not stop fan")
                os.system("/usr/bin/batocera-es-swissknife --reboot" )
            else:
                os.system("/usr/bin/batocera-es-swissknife --emukill" )
        elif pulsetime >=4 and pulsetime <=5:
            try:
                # full power off
                bus.write_byte_data(address,0,0xFF)
            except:
                print ("Could not power off")
            os.system("/usr/bin/batocera-es-swissknife --shutdown" )

# argument: start, stop, or no argument = show temp
if len(sys.argv)>1:
    if str(sys.argv[1]) == "start":
        try:
            t = Thread(target=temp_check)
            t2 = Thread(target=shutdown_check)
            t.start()
            t2.start()
        except:
            print ("Could not launch daemon")
            t.stop()
            t2.stop()
    elif str(sys.argv[1]) == "stop":
        try:
            # force fan stop (but not board power off)
            bus.write_byte_data(address,0,0x00)
        except:
            print ("Could not stop fan")
    elif str(sys.argv[1]) == "halt":
        try:
            # full power off
            bus.write_byte_data(address,0,0xFF)
        except:
            print ("Could not power off")
else:
        temp = open("/sys/class/thermal/thermal_zone0/temp","r").readline()
        val = float(int(temp)/1000)
        print ("Temp: {}C".format(val))

