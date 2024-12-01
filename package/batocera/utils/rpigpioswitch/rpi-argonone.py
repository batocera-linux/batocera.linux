#!/usr/bin/env python3
"""
Argon One Fan Service Daemon
Original source: https://github.com/Elrondo46/argonone
@lbrpdx - Modified to run on Batocera (now both RPi4 and RPi5)

RPI4:
Make sure to add in /boot/config.txt:
 dtparam=i2c_arm=on
 dtparam=i2c-1=on

RPI5:
Make sure to add in /boot/config.txt:
 dtparam=i2c=on
 dtparam=uart0=on

(it should be installed by Batocera when you enable 
Argon One support case through S92switch setup)

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
import gpiod
from gpiod.line import Edge
import os
import time
import sys
from threading import Thread

# Choose 0 (kill emulator) or 1 (force reboot) on double click
FORCE_REBOOT = 0
DEBUG = 0

config_file='/userdata/system/configs/argonone.conf'

if not os.path.exists('/dev/i2c-1'):
    print("Fatal error: i2c bus can't be initialized, verify your /boot/config.txt")
    exit()

try:
    bus = smbus.SMBus(1)
except Exception as e:
    print(f"Fatal error: {e} ")
    exit()

address = 0x1a
shutdown_pin = 4
rpi_reg = 0x80

# Read fan % speed from the config file
def get_fanspeed(tempval, configlist):
    for curconfig in configlist:
        curpair = curconfig.split("=")
        tempcfg = float(curpair[0])
        fancfg = int(float(curpair[1]))
        if tempval >= tempcfg:
            return fancfg
    return 0

# Load the config file to memory
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

# Check the current temperature and adjust fan speed
def temp_check():
    check_interval = 15 # seconds between two temp changes
    fanconfig = ["65=100", "60=55", "55=10", "45=0"] # Default values when no config file
    tmpconfig = load_config(config_file)
    if len(tmpconfig) > 0:
        fanconfig = tmpconfig
    prevblock = 0
    while True:
        temp = open("/sys/class/thermal/thermal_zone0/temp","r").readline()
        val = float(int(temp)/1000)
        block = get_fanspeed(val, fanconfig)
        if block < prevblock:
            time.sleep(check_interval)
        prevblock = block
        try:
            if DEBUG:
                print(f"Set fan speed {block}% for temp {val}C ")
            bus.write_byte_data(address, rpi_reg, block)
        except IOError:
            temp = ""
        time.sleep(check_interval)

# Thread for the button for quitting an emulator (double click)
def shutdown_check():
    chip = "/dev/gpiochip0"
    request = gpiod.request_lines(chip, consumer="watch-line-falling",
                                      config={shutdown_pin: gpiod.LineSettings(edge_detection=Edge.FALLING)})
    while True:
        for event in request.read_edge_events():
            if DEBUG:
                print(f"Double click #{event.line_seqno}")
            if FORCE_REBOOT == 1:
                try:
                    # force fan stop (but not board power off)
                    bus.write_byte_data(address, rpi_reg, 0x00)
                except Exception as e:
                    print (f"Could not stop fan: {e}")
                os.system("/usr/bin/batocera-es-swissknife --reboot" )
            else:
                os.system("/usr/bin/batocera-es-swissknife --emukill" )

# argument: start, stop, or no argument = show temp
if len(sys.argv)>1:
    if str(sys.argv[1]) == "start":
        try:
            t = Thread(target=temp_check)
            t2 = Thread(target=shutdown_check)
            t.start()
            t2.start()
        except Exception as e:
            print (f"Could not launch daemon: {e}")
            t.stop()
            t2.stop()
    elif str(sys.argv[1]) == "stop":
        try:
            # force fan stop (but not board power off)
            bus.write_byte(address, 0x00)
        except Exception as e:
            print (f"Could not stop fan: {e}")
    elif str(sys.argv[1]) == "halt":
        try:
            # full power off
            bus.write_byte(address, 0xFF)
        except Exception as e:
            print (f"Could not power off: {e}")
else:
    with open("/sys/class/thermal/thermal_zone0/temp","r") as tp:
        temp = tp.readline().strip()
        val = float(int(temp)/1000)
        print ("Temp: {:5.1f}C".format(val))

