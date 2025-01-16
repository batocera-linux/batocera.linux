#!/usr/bin/python3

import gpiod
from gpiod.line import Edge
import subprocess
from datetime import timedelta

# Pin Configuration
GPIO_CHIP = "/dev/gpiochip0"
SHUTDOWN_PIN = 3  # Pin 5 in BCM mode

def handle_shutdown():
    print('Shutting down Batocera')
    subprocess.run('shutdown -h now', shell=True)

def watch_gpio_events():
    try:
        with gpiod.request_lines(
            GPIO_CHIP,
            config={
                SHUTDOWN_PIN: gpiod.LineSettings(
                    edge_detection=Edge.FALLING,
                    debounce_period=timedelta(milliseconds=50)
                )
            },
        ) as request:
            print("GPIO event monitoring started")
            for event in request.read_edge_events():
                handle_shutdown()
    except Exception as e:
        print(f"Error watching GPIO events: {e}")
        exit(1)

def main():
    while True:
        watch_gpio_events()

if __name__ == "__main__":
    main()
