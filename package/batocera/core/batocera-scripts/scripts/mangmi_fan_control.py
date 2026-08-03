#!/usr/bin/env python3
import time
import os

PWM_PATH = "/sys/devices/platform/gpio-fan/hwmon/hwmon20/pwm1"
TEMP_PATH = "/sys/class/thermal/thermal_zone0/temp"

# Enable manual control of the fan
os.system("echo 1 > /sys/devices/platform/gpio-fan/hwmon/hwmon20/pwm1_enable")

def get_temp():
    try:
        with open(TEMP_PATH, "r") as f:
            return int(f.read().strip()) / 1000.0
    except:
        return 50.0

try:
    fd = os.open(PWM_PATH, os.O_WRONLY)
except Exception as e:
    print(f"Error opening fan path: {e}")
    exit(1)

# PWM Configuration (15ms total cycle period for quiet switching)
PERIOD = 0.015  

# Hysteresis Temperature Thresholds (Celsius)
TEMP_ON_QUIET = 50.0    # Turn Quiet Mode ON when reaching 50°C
TEMP_OFF_QUIET = 45.0   # Turn Quiet Mode OFF only when dropping below 45°C

TEMP_ON_MEDIUM = 62.0   # Turn Medium Mode ON when reaching 62°C
TEMP_OFF_MEDIUM = 56.0  # Drop back to Quiet Mode only when falling below 56°C

TEMP_ON_HIGH = 74.0     # Turn High Mode ON when reaching 74°C
TEMP_OFF_HIGH = 68.0    # Drop back to Medium Mode only when falling below 68°C

TEMP_ON_MAX = 85.0      # Turn Max Mode ON only at 85°C (throttling boundary)
TEMP_OFF_MAX = 79.0     # Drop back to High Mode only when falling below 79°C

# State variables: 0=Off, 1=Quiet(65%), 2=Medium(75%), 3=High(85%), 4=Max(100%)
state = 0
prev_duty = 0.0

def run_pwm_cycle(duty, duration):
    """Runs the fake PWM loop for the specified duration (in seconds)"""
    if duty <= 0.0:
        os.pwrite(fd, b"0\n", 0)
        time.sleep(duration)
        return
    elif duty >= 1.0:
        os.pwrite(fd, b"255\n", 0)
        time.sleep(duration)
        return

    # Calculate active ON and OFF times for the pulse
    on_time = PERIOD * duty
    off_time = PERIOD * (1 - duty)
    cycles = int(duration / PERIOD)

    for _ in range(cycles):
        os.pwrite(fd, b"255\n", 0)
        time.sleep(on_time)
        os.pwrite(fd, b"0\n", 0)
        time.sleep(off_time)

def ramp_duty(start_duty, target_duty, duration_sec=1.5):
    """Gradually ramps the duty cycle to prevent start-up motor rattle"""
    steps = 15
    step_duration = duration_sec / steps
    for i in range(1, steps + 1):
        # Linearly interpolate between the start and target duty cycle
        temp_duty = start_duty + (target_duty - start_duty) * (i / steps)
        run_pwm_cycle(temp_duty, step_duration)

try:
    while True:
        temp = get_temp()

        # State machine transition logic (Hysteresis)
        if state == 0:  # Currently OFF
            if temp >= TEMP_ON_QUIET:
                state = 1
        elif state == 1:  # Currently in QUIET (65%)
            if temp < TEMP_OFF_QUIET:
                state = 0
            elif temp >= TEMP_ON_MEDIUM:
                state = 2
        elif state == 2:  # Currently in MEDIUM (75%)
            if temp < TEMP_OFF_MEDIUM:
                state = 1
            elif temp >= TEMP_ON_HIGH:
                state = 3
        elif state == 3:  # Currently in HIGH (85%)
            if temp < TEMP_OFF_HIGH:
                state = 2
            elif temp >= TEMP_ON_MAX:
                state = 4
        elif state == 4:  # Currently in MAX (100%)
            if temp < TEMP_OFF_MAX:
                state = 3

        # Map selected state to the target duty cycle
        if state == 0:
            duty = 0.0
        elif state == 1:
            duty = 0.65  # 65% Quiet Speed (minimum stable speed)
        elif state == 2:
            duty = 0.75  # 75% Medium Speed
        elif state == 3:
            duty = 0.85  # 85% High Speed
        else:
            duty = 1.0   # 100% Maximum cooling

        # If the speed has changed, execute a smooth ramp sequence first
        if duty != prev_duty:
            ramp_duty(prev_duty, duty, duration_sec=1.5)
            prev_duty = duty

        # Run normal steady-state cycles for 4 seconds before reading temp again
        run_pwm_cycle(duty, 4.0)

except KeyboardInterrupt:
    # Safely turn off the fan on manual exit
    os.pwrite(fd, b"0\n", 0)
    os.close(fd)
