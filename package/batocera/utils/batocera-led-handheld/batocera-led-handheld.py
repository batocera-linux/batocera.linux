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
  15=ESCOLOR
  100=009900

100 is when a charger is plugged in
You can use PULSE, RAINBOW and OFF as rgb_color for special effects.

ESCOLOR is the default one set with sliders in EmulationStation

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
CHECK_INTERVAL  = 3  # seconds between two checks
LED_CHANGE_TIME = 30 # seconds to prevent changes while entering the settings menu
CONFIG_FILE='/userdata/system/configs/leds.conf'
BLOCK_FILE='/var/run/led-handheld-block'

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
    ledconfig = ["100=009900", "15=ESCOLOR", "10=CC3333", "5=FF0000", "3=PULSE"] # Default values when no config file
    tmpconfig = load_config(CONFIG_FILE)
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
                if color_changes_allowed():
                    led.set_color(block)
            except Exception as e:
                print (f"Error: {e}") 
            time.sleep(CHECK_INTERVAL)

# Prevent color changes when entering color selection
def block_color_changes(block):
    with open(BLOCK_FILE, "w+") as fp:
        if block:
            fp.write(str(time.time()))
        else:
            fp.write("0")

def color_changes_allowed():
    try:
        with open(BLOCK_FILE, "r") as fp:
            line = fp.read().strip()
            diff = time.time() - float(line)
            if diff < LED_CHANGE_TIME:
                return (False)
        with open(BLOCK_FILE, "w+") as fp:
            fp.write("0")
        return (True)
    except:
        return (True)

# argument: start, stop, or no argument = show battery %
PATH = check_support()
if PATH == None:
    exit()
if len(sys.argv)>1:
    led = batoled.led()
    if sys.argv[1] == "start":
        try:
            led.set_brightness_conf()
            t = Thread(target=led_check, args=(led,))
            t.start()
        except Exception as e:
            print (f"Could not launch daemon: {e}")
            t.stop()
    elif sys.argv[1] == "stop" or sys.argv[1] == "off":
        led.turn_off()
    elif sys.argv[1] == "retroachievement" or sys.argv[1] == "rainbow":
        if color_changes_allowed():
            led.rainbow_effect()
    elif sys.argv[1] == "pulse":
        if color_changes_allowed():
            led.pulse_effect()
    elif sys.argv[1] == "set_color" and sys.argv[2] != None:
        if color_changes_allowed():
            led.set_color(sys.argv[2])
    elif sys.argv[1] == "get_color":
        print(led.get_color())
    elif sys.argv[1] == "set_color_dec" and sys.argv[2] != None:
        if color_changes_allowed():
            rgb = ""
            for p in (sys.argv[2:]):
                rgb += str(p) + ' '
            led.set_color_dec(rgb)
    elif sys.argv[1] == "set_color_force_dec" and sys.argv[2] != None:
        rgb = ""
        for p in (sys.argv[2:]):
            rgb += str(p) + ' '
        led.set_color_dec(rgb)
    elif sys.argv[1] == "get_color_dec":
        print(led.get_color_dec())
    elif sys.argv[1] == "block_color_changes":
        block_color_changes(True)
    elif sys.argv[1] == "unblock_color_changes":
        block_color_changes(False)
    elif sys.argv[1] == "set_brightness" and sys.argv[2] != None:
        led.set_brightness(sys.argv[2])
    elif sys.argv[1] == "get_brightness":
        (b, m) = led.get_brightness()
        print(f'{b} {m}')
else:
    with open(PATH + '/capacity', 'r') as tp, \
            open(PATH + '/status','r') as st:
        bt = tp.readline().strip()
        ch = st.readline().strip()
        print (f"Battery: {bt}% ({ch})")

