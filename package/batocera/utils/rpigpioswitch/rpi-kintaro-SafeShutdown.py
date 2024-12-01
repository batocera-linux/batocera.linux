#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Copyright 2017 Michael Kirsch
#https://github.com/MichaelKirsch
#Added to BATOCERA 12.05.2020
#Moved to use python-gpiod by dmanlfc - 01.12.2024

try:
    import time
    import os
    import gpiod
    import subprocess
except ImportError:
    raise ImportError('spidev or gpio not installed')

class SNES:

    def __init__(self):

        #GPIOs
        self.led_pin = 7
        self.fan_pin = 8
        self.reset_pin = 3
        self.power_pin = 5
        self.check_pin = 10

        #vars
        self.fan_hysteresis = 20
        self.fan_starttemp = 60
        self.debounce_time = 0.1

        #path
        self.temp_command = 'vcgencmd measure_temp'

        #Set the GPIOs
        self.chip = gpiod.Chip('gpiochip0')  # Access the GPIO chip
        
        # Use get_lines for multiple pin configuration
        self.gpio_lines = self.chip.get_lines([
            self.led_pin, 
            self.fan_pin, 
            self.reset_pin, 
            self.power_pin, 
            self.check_pin
        ])

        # Request lines with appropriate configurations
        self.gpio_lines.request(
            consumers=[
                "SNES_LED", 
                "SNES_FAN", 
                "SNES_RESET", 
                "SNES_POWER", 
                "SNES_CHECK"
            ],
            types=[
                gpiod.LINE_REQ_DIR_OUT,      # LED
                gpiod.LINE_REQ_DIR_OUT,      # FAN
                gpiod.LINE_REQ_DIR_IN,       # RESET
                gpiod.LINE_REQ_DIR_IN,       # POWER
                gpiod.LINE_REQ_DIR_IN        # CHECK
            ],
            flags=[
                0,                           # LED
                0,                           # FAN
                gpiod.LINE_REQ_FLAG_PULL_UP, # RESET
                0,                           # POWER
                gpiod.LINE_REQ_FLAG_PULL_UP  # CHECK
            ]
        )

        # Unpack the lines for easier access
        (self.led, 
         self.fan, 
         self.reset, 
         self.power, 
         self.check) = self.gpio_lines

        #PWM for the fan
        self.pwm = 0

    def power_interrupt(self, channel):
        time.sleep(self.debounce_time)  # debounce
        if self.power.get_value() == 1 and self.check.get_value() == 0:  # shutdown function if the power switch is toggled
            self.led.set_value(0)  # led and fan off
            os.system("shutdown -h now")

    def reset_interrupt(self, channel):
        if self.reset.get_value() == 0:  # reset function
            time.sleep(self.debounce_time)  # debounce time
            while self.reset.get_value() == 0:  # while the button is held the counter counts up
                self.blink(15, 0.1)
                os.system("reboot")

    def pcb_interrupt(self, channel):
        self.chip.close()  # when the pcb is pulled, clean all the used GPIO pins

    def temp(self):     #returns the gpu temperature
        res = os.popen(self.temp_command).readline()
        return float((res.replace("temp=", "").replace("'C\n", "")))

    def pwm_fancontrol(self,hysteresis, starttemp, temp):
        perc = 100.0 * ((temp - (starttemp - hysteresis)) / (starttemp - (starttemp - hysteresis)))
        perc=min(max(perc, 0.0), 100.0)
        self.pwm = perc

    def led(self,status):  #toggle the led on or off
        if status == 0:       #the led is inverted
            self.led.set_value(0)
        if status == 1:
            self.led.set_value(1)

    def blink(self,amount,interval): #blink the led
        for x in range(amount):
            self.led.set_value(1)
            time.sleep(interval)
            self.led.set_value(0)
            time.sleep(interval)

    def check_fan(self):
        self.pwm_fancontrol(self.fan_hysteresis,self.fan_starttemp,self.temp())  # fan starts at 60 degrees and has a 5 degree hysteresis

    def attach_interrupts(self):
        if self.check.get_value() == 0:  # check if there is a PCB and if so attach the interrupts
            if self.power.get_value() == 1: # when the system gets started in the on position, it gets shut down
                os.system("shutdown -h now")
            else:
                self.led.set_value(1)

        else:       # no PCB attached, so let's exit
            self.chip.close()
            exit()

def main():
    snes = SNES()
    snes.attach_interrupts()

    while True:
        time.sleep(5)
        snes.led.set_value(1)
        snes.check_fan()

if __name__ == "__main__":
    main()
