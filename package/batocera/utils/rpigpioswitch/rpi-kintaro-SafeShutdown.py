#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Copyright 2017 Michael Kirsch
#https://github.com/MichaelKirsch
#Added to BATOCERA 12.05.2020
#Moved to use python-gpiod by dmanlfc - 01.12.2024

try:
    from datetime import timedelta
    import os
    import gpiod
    from gpiod.line import Edge, Direction, Value
    import subprocess
    import threading
    import time
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
        self.init_gpio()

    def init_gpio(self):
        try:
            gpiod.request_lines('/dev/gpiochip0',
                config={
                    self.led_pin: gpiod.LineSettings(
                        direction=Direction.OUTPUT, 
                        output_value=Value.ACTIVE
                    ),
                    self.fan_pin: gpiod.LineSettings(
                        direction=Direction.OUTPUT, 
                        output_value=Value.INACTIVE
                    ),
                    self.check_pin: gpiod.LineSettings(
                        direction=Direction.INPUT,
                        output_value=Value.ACTIVE
                    )
                }
            )
            print("GPIO initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize GPIO: {e}")
            exit(1)

    def handle_gpio_event(self, event_line_offset):
        if event_line_offset == self.reset_pin:
            print("RESET button pressed")
            self.reset_function()
        elif event_line_offset == self.power_pin:
            print("POWER button pressed")
            self.power_function()

    def reset_function(self):
        time.sleep(self.debounce_time)  # debounce time
        while True:
            self.blink(15, 0.1)
            subprocess.run("reboot", shell=True)

    def power_function(self):
        time.sleep(self.debounce_time)  # debounce
        if self.check.get_value() == 0:  # shutdown function if the power switch is toggled
            self.led.set_value(0)  # led and fan off
            subprocess.run("shutdown -h now", shell=True)

    def temp(self):     #returns the gpu temperature
        res = os.popen(self.temp_command).readline()
        return float((res.replace("temp=", "").replace("'C\n", "")))

    def pwm_fancontrol(self,hysteresis, starttemp, temp):
        perc = 100.0 * ((temp - (starttemp - hysteresis)) / (starttemp - (starttemp - hysteresis)))
        perc=min(max(perc, 0.0), 100.0)
        self.pwm = perc

    def blink(self,amount,interval): #blink the led
        for x in range(amount):
            self.led.set_value(1)
            time.sleep(interval)
            self.led.set_value(0)
            time.sleep(interval)

    def check_fan(self):
        self.pwm_fancontrol(self.fan_hysteresis,self.fan_starttemp,self.temp())  # fan starts at 60 degrees and has a 5 degree hysteresis

    def check_fan_periodically(self):
        while True:
            self.check_fan()
            time.sleep(5)

    def watch_gpio_events(self):
        try:
            with gpiod.request_lines(
                '/dev/gpiochip0',
                config={
                    self.reset_pin: gpiod.LineSettings(
                        edge_detection=Edge.RISING,
                        debounce_period=timedelta(milliseconds=50)
                    ),
                    self.power_pin: gpiod.LineSettings(
                        edge_detection=Edge.FALLING
                    )
                },
            ) as request:
                print("GPIO event monitoring started")
                for event in request.read_edge_events():
                    self.handle_gpio_event(event.line_offset)
        except Exception as e:
            print(f"Error watching GPIO events: {e}")
            exit(1)

    def start(self):
        fan_thread = threading.Thread(target=self.check_fan_periodically)
        fan_thread.daemon = True  # So that the thread dies when the main program exits
        fan_thread.start()
        while True:
            self.watch_gpio_events()

def main():
    snes = SNES()
    snes.start()

if __name__ == "__main__":
    main()
