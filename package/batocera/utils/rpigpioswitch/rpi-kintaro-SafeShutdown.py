#!/usr/bin/python
# -*- coding: utf-8 -*-
#Copyright 2017 Michael Kirsch
#https://github.com/MichaelKirsch
#Added to BATOCERA 12.05.2020

try:
    import time
    import os
    import RPi.GPIO as GPIO
    import subprocess
except ImportError:
    raise ImportError('spidev or gpio not installed')

class SNES:

    def __init__(self):

        #GPIOs

        self.led_pin=7
        self.fan_pin=8
        self.reset_pin=3
        self.power_pin=5
        self.check_pin=10

        #vars

        self.fan_hysteresis = 20
        self.fan_starttemp = 60
        self.debounce_time = 0.1

        #path

        self.temp_command = 'vcgencmd measure_temp'

        #Set the GPIOs

        GPIO.setmode(GPIO.BOARD)  # Use the same layout as the pins
        GPIO.setwarnings(False)
        GPIO.setup(self.led_pin, GPIO.OUT)  # LED Output
        GPIO.setup(self.fan_pin, GPIO.OUT)  # FAN Output
        GPIO.setup(self.power_pin, GPIO.IN)  # set pin as input
        GPIO.setup(self.reset_pin, GPIO.IN,
                   pull_up_down=GPIO.PUD_UP)  # set pin as input and switch on internal pull up resistor
        GPIO.setup(self.check_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.pwm = GPIO.PWM(self.fan_pin, 50)  #PWM for the fan
        self.pwm.start(0)


    def power_interrupt(self, channel):
        time.sleep(self.debounce_time)  # debounce
        if GPIO.input(self.power_pin) == GPIO.HIGH and GPIO.input(
                self.check_pin) == GPIO.LOW:  # shutdown function if the powerswitch is toggled
            self.led(0)  # led and fan off
            os.system("shutdown -h now")

    def reset_interrupt(self, channel):
        if GPIO.input(self.reset_pin) == GPIO.LOW:  # reset function
            time.sleep(self.debounce_time)  # debounce time
            while GPIO.input(self.reset_pin) == GPIO.LOW:  # while the button is hold the counter counts up
                self.blink(15, 0.1)
                os.system("reboot")

    def pcb_interrupt(self, channel):
        GPIO.cleanup()  # when the pcb is pulled clean all the used GPIO pins

    def temp(self):     #returns the gpu temoperature
        res = os.popen(self.temp_command).readline()
        return float((res.replace("temp=", "").replace("'C\n", "")))

    def pwm_fancontrol(self,hysteresis, starttemp, temp):
        perc = 100.0 * ((temp - (starttemp - hysteresis)) / (starttemp - (starttemp - hysteresis)))
        perc=min(max(perc, 0.0), 100.0)
        self.pwm.ChangeDutyCycle(float(perc))

    def led(self,status):  #toggle the led on of off
        if status == 0:       #the led is inverted
            GPIO.output(self.led_pin, GPIO.LOW)
        if status == 1:
            GPIO.output(self.led_pin, GPIO.HIGH)

    def blink(self,amount,interval): #blink the led
        for x in range(amount):
            self.led(1)
            time.sleep(interval)
            self.led(0)
            time.sleep(interval)

    def check_fan(self):
        self.pwm_fancontrol(self.fan_hysteresis,self.fan_starttemp,self.temp())  # fan starts at 60 degrees and has a 5 degree hysteresis

    def attach_interrupts(self):
        if GPIO.input(self.check_pin) == GPIO.LOW:  # check if there is an pcb and if so attach the interrupts
            GPIO.add_event_detect(self.check_pin, GPIO.RISING,callback=self.pcb_interrupt)  # if not the interrupt gets attached
            if GPIO.input(self.power_pin) == GPIO.HIGH: #when the system gets startet in the on position it gets shutdown
                os.system("shutdown -h now")
            else:
                self.led(1)
                GPIO.add_event_detect(self.reset_pin, GPIO.FALLING, callback=self.reset_interrupt)
                GPIO.add_event_detect(self.power_pin, GPIO.RISING, callback=self.power_interrupt)
        else:       #no pcb attached so lets exit
            GPIO.cleanup()
            exit()

snes = SNES()

snes.attach_interrupts()

while True:
    time.sleep(5)
    snes.led(1)
    snes.check_fan()
