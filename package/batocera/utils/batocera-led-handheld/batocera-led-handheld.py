#!/usr/bin/env python3
"""
LED Service Daemon for handheld devices
Show battery level and retroachievements through LED controllers
Written for Batocera - @lbrpdx

In order to configure your own color mapping
edit a file /userdata/system/configs/leds.conf with:

Battery in %
Color in RGB syntax
Each line is: battery_threshold=rgb_color
default is:

  3=PULSE
  5=FF0000
  10=CC3333
  25=AA8888
  50=AA00AA
  90=00AA00
  100=88FF88

100 is when a charger is plugged in
You can use PULSE, RAINBOW and OFF as rgb_color for special effects.

Also, if you want to trigger a fancy rainbow effect when you unlock a retroachievement,
SSH into Batocera and type the 3 commands:

   mkdir -p /userdata/system/configs/emulationstation/scripts/achievements/
   echo "/usr/bin/batocera-led-handheld rainbow" > /userdata/system/configs/emulationstation/scripts/achievements/leds.sh
   chmod +x /userdata/system/configs/emulationstation/scripts/achievements/leds.sh

"""
import os
import time
import sys
import glob
import batoled
from threading import Thread

DEBUG = 0
CHECK_INTERVAL = 4 # seconds between two checks

config_file='/userdata/system/configs/leds.conf'

def check_support():
    model = batoled.batocera_model()
    if model in [ "pwm" ]:
        return ('/sys/class/power_supply/qcom-battery/')
    if model in [ "rgb" ]:
        return ('/sys/class/power_supply/BAT0/')
    else:
        print ("Device unsupported.")
        return None

# Read color from the config file
def read_color(tempval, configlist):
    for curconfig in configlist:
        curpair = curconfig.split("=")
        tempcfg = int(curpair[0])
        fancfg = curpair[1]
        if int(tempval) >= tempcfg:
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
                    tempval = int(tmppair[0])
                    if tempval < 0 or tempval > 100:
                        continue
                except:
                    continue
                try:
                    fanval = tmppair[1]
                except:
                    continue
                newconfig.append(f'{tempval:3.0f}={fanval}')
        if len(newconfig) > 0:
            newconfig.sort(reverse=True)
    except:
        return []
    return newconfig

# Check the current battery level and adjust led color
def led_check(led):
    ledconfig = ["100=88FF88", "90=00AA00", "50=AA00AA", "25=AA8888", "10=CC3333", "5=FF0000", "3=pulse"] # Default values when no config file
    tmpconfig = load_config(config_file)
    if len(tmpconfig) > 0:
        ledconfig = tmpconfig
    if (DEBUG):
        print(ledconfig)
    prevblock = 0
    while True:
        with open(PATH + '/capacity', 'r') as tp, \
                open(PATH + '/status','r') as st:
            bt = tp.readline().strip()
            ch = st.readline().strip()
            if (ch == "Charging") or (ch == "Full"):
                bt = '100'
            if (ch == "Discharging") and (bt == "100"):
                bt = '99'
            block = read_color(bt, ledconfig)
            prevblock = block
            try:
                if DEBUG:
                    print(f"Set color to {block} for {bt}%")
                led.set_color(block)
            except Exception as e:
                print (f"Error: {e}") 
            time.sleep(CHECK_INTERVAL)

# argument: start, stop, or no argument = show battery %
PATH = check_support()
if PATH == None:
    exit()
if len(sys.argv)>1:
    led = batoled.led()
    if sys.argv[1] == "start":
        try:
            t = Thread(target=led_check, args=(led,))
            t.start()
        except Exception as e:
            print (f"Could not launch daemon: {e}")
            t.stop()
    elif sys.argv[1] == "stop" or sys.argv[1] == "off":
        led.turn_off()
    elif sys.argv[1] == "retroachievement" or sys.argv[1] == "rainbow":
        led.rainbow_effect()
    elif sys.argv[1] == "pulse":
        led.pulse_effect()
    elif sys.argv[1] == "color" and sys.argv[2] != None:
        led.set_color(sys.argv[2])
else:
    with open(PATH + '/capacity', 'r') as tp, \
            open(PATH + '/status','r') as st:
        bt = tp.readline().strip()
        ch = st.readline().strip()
        print (f"Battery: {bt}% ({ch})")

