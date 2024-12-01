#!/usr/bin/python3

import gpiod
import subprocess

# Pin Configuration
GPIO_CHIP = "/dev/gpiochip0"
POWER_PIN = 26  # GPIO 26 in BCM mode
POWER_EN_PIN = 27  # GPIO 27 in BCM mode

def init_gpio():
    try:
        chip = gpiod.Chip(GPIO_CHIP)
        power_button = chip.get_line(POWER_PIN)
        power_en = chip.get_line(POWER_EN_PIN)

        power_button.request(
            consumer="power_button",
            type=gpiod.LINE_REQ_EV_FALLING_EDGE,
            flags=gpiod.LINE_REQ_FLAG_PULL_UP
        )
        power_en.request(consumer="power_en", type=gpiod.LINE_REQ_DIR_OUT)
        power_en.set_value(1)  # Set power enable pin high

        return power_button
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        exit(1)

def handle_poweroff(power_button):
    try:
        while True:
            if power_button.event_wait(sec=1):
                power_button.event_read()
                output = int(subprocess.check_output(['batocera-es-swissknife', '--espid']).strip())
                if output:
                    print("Exiting emulators and shutting down Batocera")
                    subprocess.run("batocera-es-swissknife --emukill", shell=True)
                    subprocess.run("batocera-es-swissknife --shutdown", shell=True)
                else:
                    print("System shutdown")
                    subprocess.run("shutdown -h now", shell=True)
    except Exception as e:
        print(f"Error in handle_poweroff: {e}")

def main():
    power_button = init_gpio()
    handle_poweroff(power_button)

if __name__ == "__main__":
    main()
