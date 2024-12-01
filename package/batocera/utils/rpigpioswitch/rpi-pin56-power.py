#!/usr/bin/python3

import gpiod
import subprocess
import time

# Pin Configuration
GPIO_CHIP = "/dev/gpiochip0"
SHUTDOWN_PIN = 3  # Pin 5 in BCM mode

def init_gpio():
    try:
        chip = gpiod.Chip(GPIO_CHIP)
        
        shutdown_lines = chip.get_lines([SHUTDOWN_PIN])

        shutdown_lines.request(
            consumers=['shutdown'],
            types=[gpiod.LINE_REQ_EV_FALLING_EDGE],
            flags=[gpiod.LINE_REQ_FLAG_PULL_UP]
        )
        
        shutdown_button = shutdown_lines[0]
        
        return chip, shutdown_button
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        exit(1)

def handle_shutdown():
    print('Shutting down Batocera')
    subprocess.run('shutdown -h now', shell=True)

def watch_gpio_events():
    try:
        chip, shutdown_button = init_gpio()
        print("GPIO event monitoring started")

        while True:
            if shutdown_button.event_wait(sec=1):
                shutdown_button.event_read()
                handle_shutdown()
            
    except Exception as e:
        print(f"Error watching GPIO events: {e}")
        exit(1)

def main():
    watch_gpio_events()

if __name__ == "__main__":
    main()
