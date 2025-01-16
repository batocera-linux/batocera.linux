#!/usr/bin/python3

import gpiod
from gpiod.line import Edge, Direction, Value
import subprocess
from datetime import timedelta

# Pin Configuration
POWER_CHIP = "/dev/gpiochip0"
POWER_PIN = 26  # GPIO 26 in BCM mode
POWER_EN_PIN = 27  # GPIO 27 in BCM mode

def init_gpio():
    try:
        gpiod.request_lines(POWER_CHIP,
            config={
                POWER_EN_PIN: gpiod.LineSettings(
                    direction=Direction.OUTPUT, 
                    output_value=Value.ACTIVE
                )
            }
        )
        print("GPIO initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        exit(1)

def handle_gpio_event(event_line_offset):
    if event_line_offset == POWER_PIN:
        print("POWER button pressed")
        try:
            output = int(subprocess.check_output(['batocera-es-swissknife', '--espid']))
            if output:
                print("Exiting emulators and shutting down Batocera")
                subprocess.run("batocera-es-swissknife --emukill", shell=True, check=True)
                subprocess.run("batocera-es-swissknife --shutdown", shell=True, check=True)
            else:
                print("System shutdown")
                subprocess.run("shutdown -h now", shell=True, check=True)
        except Exception as e:
            print(f"Poweroff command error: {e}")

def watch_gpio_events():
    try:
        with gpiod.request_lines(
            POWER_CHIP,
            config={
                POWER_PIN: gpiod.LineSettings(
                    edge_detection=Edge.FALLING
                )
            },
        ) as request:
            print("GPIO event monitoring started")
            for event in request.read_edge_events():
                handle_gpio_event(event.line_offset)
    except Exception as e:
        print(f"Error watching GPIO events: {e}")
        exit(1)

def main():
    init_gpio()
    while True:
        watch_gpio_events()

if __name__ == "__main__":
    main()
