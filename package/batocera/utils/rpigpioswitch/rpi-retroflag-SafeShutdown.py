#!/usr/bin/python3
import gpiod
import subprocess
import time

# Pin Configuration
GPIO_CHIP = "/dev/gpiochip0"
POWER_PIN = 3       # GPIO 3 in BCM mode (pin 5)
RESET_PIN = 2       # GPIO 2 in BCM mode (pin 3)
LED_PIN = 14        # GPIO 14 in BCM mode (TXD, pin 8)
POWER_EN_PIN = 4    # GPIO 4 in BCM mode (pin 7)

def init_gpio():
    try:
        chip = gpiod.Chip(GPIO_CHIP)
        
        # Use get_lines method for version 2.2.0
        lines = chip.get_lines([POWER_PIN, RESET_PIN, LED_PIN, POWER_EN_PIN])
        
        # Request lines with configuration
        lines.request(
            consumers=["power_button", "reset_button", "led", "power_enable"],
            types=[
                gpiod.LINE_REQ_EV_FALLING_EDGE,  # power_button
                gpiod.LINE_REQ_EV_FALLING_EDGE,  # reset_button
                gpiod.LINE_REQ_DIR_OUT,          # led
                gpiod.LINE_REQ_DIR_OUT           # power_enable
            ],
            flags=[
                gpiod.LINE_REQ_FLAG_PULL_UP,  # power_button
                gpiod.LINE_REQ_FLAG_PULL_UP,  # reset_button
                0,                            # led
                0                             # power_enable
            ]
        )
        
        # Separate the lines after requesting
        power_button, reset_button, led, power_enable = lines
        
        # Set initial states
        led.set_value(1)  # LED off (active low)
        power_enable.set_value(1)  # Power enable high
        
        return power_button, reset_button, led, chip
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        exit(1)

def handle_poweroff(power_button):
    try:
        while True:
            if power_button.event_wait(sec=1):
                power_button.event_read()
                print("Power button pressed. Shutting down.")
                subprocess.run("shutdown -h now", shell=True)
    except Exception as e:
        print(f"Error in handle_poweroff: {e}")

def handle_led_blink(power_button, led):
    try:
        while True:
            if power_button.event_wait(sec=1):
                power_button.event_read()
                while not power_button.get_value():
                    led.set_value(0)  # LED on
                    time.sleep(0.2)
                    led.set_value(1)  # LED off
                    time.sleep(0.2)
    except Exception as e:
        print(f"Error in handle_led_blink: {e}")

def handle_reset(reset_button):
    try:
        while True:
            if reset_button.event_wait(sec=1):
                reset_button.event_read()
                print("Reset button pressed. Restarting.")
                subprocess.run("shutdown -r now", shell=True)
    except Exception as e:
        print(f"Error in handle_reset: {e}")

def main():
    power_button, reset_button, led, chip = init_gpio()
    
    try:
        # Run handlers (no need for multiprocessing; they are independent loops)
        handle_poweroff(power_button)  # Power off handler
        handle_led_blink(power_button, led)  # LED blink handler
        handle_reset(reset_button)  # Reset handler
    finally:
        # Properly close the chip to release resources
        chip.close()

if __name__ == "__main__":
    main()
