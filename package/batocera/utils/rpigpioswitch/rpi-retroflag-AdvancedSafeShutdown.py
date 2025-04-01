#!/usr/bin/python3

# IMPORTS
import gpiod
from gpiod.line import Bias, Edge, Direction, Value
import os
from datetime import timedelta
import subprocess
import signal
import sys
import threading
import time

# PIN CONFIGURATION
POWER_CHIP = "/dev/gpiochip0"
POWER_PIN = 3    # pin 5
LED_PIN = 14     # TXD - pin 8
RESET_PIN = 2    # pin 3
POWEREN_PIN = 4  # pin 7

#############################
## RETROFLAGS NESPI 4 CASE ##
## POWER AND RESET BUTTONS ##
#############################
# START OF USER CONFIGURATION
#############################

# RESET BUTTON
# threshold between short and long RESET button press set in seconds
LONG_PRESS_THRESHOLD = 2.0

# SPLASH IMAGES & LED BLINKS
# if splash image path is set to "" it will default to system fallback paths
# set custom splash image by replacing "" with "/path/to/your/image.png"
# set custom fallback path only if you just want a single splash image
# splash image display duration is set for each button press in seconds
# LED blinks are set for each button press in seconds, format = [(off_time, on_time), ...]

# Quick blink when button is pressed to acknowledge button press
LED_PATTERN_BUTTON_PRESS_ACKNOWLEDGE = [(0.05, 0.05)]

# Short RESET button press in emulator (exit emulator)
# to set a custom emulator splash you need to change /usr/share/emulationstation/resources/logo.png"
# this script does not provide this option - see https://wiki.batocera.org/splash_boot for more info
LED_PATTERN_EXIT_EMULATOR = [(0.3, 0.3), (0.3, 0.3), (0.3, 0.3)]

# Short RESET button press in ES (restart ES)
SPLASH_RESTART_ES_PATH = ""
SPLASH_RESTART_ES_DURATION = 2.0
LED_PATTERN_RESTART_ES = [(0.3, 0.3), (0.3, 0.3), (0.3, 0.3)]

# Long RESET button press (reboot system)
SPLASH_REBOOT_PATH = ""
SPLASH_REBOOT_DURATION = 2.0
LED_PATTERN_REBOOT = [(0.3, 0.6), (0.3, 0.6), (0.3, 0.6)]

# POWER button press (shutdown system)
SPLASH_SHUTDOWN_PATH = ""
SPLASH_SHUTDOWN_DURATION = 2.0
LED_PATTERN_SHUTDOWN = [(0.45, 0.9), (0.45, 0.9), (0.45, 0.9)]

# Fallback paths in order of preference
SPLASH_FALLBACK_PATHS = [
    # Custom fallback path
    "",
    # System default fallback paths - do not change
    "/usr/share/emulationstation/resources/logo.png",
    "/usr/share/batocera/splash/boot-logo.png"
]

# FRAMEBUFFER DELAY
# delay to ensure framebuffer is ready and splash is shown for set duration
# only change if the splash image is on screen shorter than set duration
FRAMEBUFFER_DELAY = 5.5 # seconds - default is 5.5

###########################
# END OF USER CONFIGURATION
###########################

# GLOBAL VARIABLES
led_request = None
poweren_request = None
reset_press_start = None

# Setup and Cleanup Functions
def init_gpio():
    """Initialize GPIO pins for LED and power control"""
    global led_request, poweren_request
    try:
        # Initialize LED pin as output and set to HIGH
        led_request = gpiod.request_lines(POWER_CHIP,
            config={
                LED_PIN: gpiod.LineSettings(
                    direction=Direction.OUTPUT, 
                    output_value=Value.ACTIVE
                )
            }
        )
        
        # Initialize POWEREN pin as output and set to HIGH
        poweren_request = gpiod.request_lines(POWER_CHIP,
            config={
                POWEREN_PIN: gpiod.LineSettings(
                    direction=Direction.OUTPUT, 
                    output_value=Value.ACTIVE
                )
            }
        )
        print("GPIO initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        exit(1)

def cleanup():
    """Release GPIO resources and prepare for script termination"""
    global led_request, poweren_request
    print("Cleaning up GPIO...")
    
    # Set POWEREN pin to LOW before exiting
    try:
        if poweren_request:
            poweren_request.set_value(POWEREN_PIN, Value.INACTIVE)
            time.sleep(0.5)  # Wait for the signal to take effect
            poweren_request.release()
    except Exception as e:
        print(f"Error releasing POWEREN pin: {e}")
        
    # Release LED pin
    try:
        if led_request:
            led_request.release()
    except Exception as e:
        print(f"Error releasing LED pin: {e}")

def signal_handler(sig, frame):
    """Handle system signals for clean shutdown"""
    print("Signal received, cleaning up...")
    cleanup()
    sys.exit(0)

def prepare_for_shutdown():
    """Prepare hardware for system shutdown"""
    global poweren_request
    print("Preparing for shutdown...")
    
    # Set POWEREN pin to LOW to allow case to cut power after shutdown
    try:
        if poweren_request:
            poweren_request.set_value(POWEREN_PIN, Value.INACTIVE)
            print("POWEREN pin set to LOW for shutdown")
    except Exception as e:
        print(f"Error setting POWEREN pin for shutdown: {e}")

# LED Control
def blink_led_pattern(pattern):
    """Blink LED according to the given pattern"""
    global led_request
    for off_time, on_time in pattern:
        led_request.set_value(LED_PIN, Value.INACTIVE)
        time.sleep(off_time)
        if on_time > 0:
            led_request.set_value(LED_PIN, Value.ACTIVE)
            time.sleep(on_time)
    # Ensure LED is turned back on at the end
    led_request.set_value(LED_PIN, Value.ACTIVE)

def blink_led_background(pattern):
    """Blink LED in a background thread"""
    thread = threading.Thread(target=blink_led_pattern, args=(pattern,))
    thread.daemon = True
    thread.start()
    return thread

# Display Management  
def show_splash_image(specific_path=None, display_duration=0):
    """Display a splash image using the fbv tool with duration handling"""
    try:
        # Create prioritized list of paths to try
        image_paths = []
        if specific_path and specific_path.strip():
            image_paths.append(specific_path)
        image_paths.extend(SPLASH_FALLBACK_PATHS)
        
        # Try each image path until one works
        for path in image_paths:
            if os.path.exists(path):
                print(f"Displaying splash image: {path} for {display_duration}s")
                
                # Start fbv
                cmd = ["fbv", "-d", "/dev/fb0", "-f", "-e", "-r", path]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Wait for the specified duration
                if display_duration > 0:
                    time.sleep(display_duration)
                
                # Kill the process
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                return True
                
        print("No splash images found in configured paths")
        return False
    except Exception as e:
        print(f"Failed to show splash image: {e}")
        return False

def clear_framebuffer():
    """Clear the framebuffer to ensure no image remains"""
    print("Clearing framebuffer...")
    try:
        # Get framebuffer size dynamically
        buf_size = os.path.getsize("/dev/fb0")
        subprocess.run(
            f"dd if=/dev/zero of=/dev/fb0 bs={buf_size} count=1",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except Exception as e:
        print(f"Failed to clear framebuffer: {e}")
        return False

# Button Handlers
def handle_reset_button(is_pressed):
    """Handle RESET button press and release events"""
    global led_request, reset_press_start
    
    if is_pressed:
        # Button is pressed down - record the time
        reset_press_start = time.time()
        # Quick LED blink to acknowledge button press
        blink_led_pattern(LED_PATTERN_BUTTON_PRESS_ACKNOWLEDGE)
    else:
        # Button is released - calculate duration
        if reset_press_start is not None:
            press_duration = time.time() - reset_press_start
            print(f"RESET button released after {press_duration:.2f} seconds")
            
            try:
                # Check if in emulator or ES
                output = int(subprocess.check_output(['batocera-es-swissknife', '--espid']))
                output_rc = int(subprocess.check_output(['batocera-es-swissknife', '--emupid']))
                
                # Take action based on current state and press duration
                if output_rc:
                    # in an emulator = kill emulator regardless of press duration
                    print("In emulator - killing emulator")
                    blink_led_pattern(LED_PATTERN_EXIT_EMULATOR)
                    subprocess.run("batocera-es-swissknife --emukill", shell=True, check=True)
                elif output:
                    # In ES - action depends on press duration
                    if press_duration >= LONG_PRESS_THRESHOLD:
                        # Long press = reboot system
                        print("Long press detected - rebooting system")
                        blink_thread = blink_led_background(LED_PATTERN_REBOOT)
                        subprocess.run("/etc/init.d/S31emulationstation stop", shell=True, check=True)
                        time.sleep(FRAMEBUFFER_DELAY)
                        show_splash_image(SPLASH_REBOOT_PATH, SPLASH_REBOOT_DURATION)
                        clear_framebuffer()
                        time.sleep(0.2)
                        blink_thread.join()
                        subprocess.run("shutdown -r now", shell=True, check=True)
                    else:
                        # Short press = restart ES
                        print("Short press detected - restarting ES")
                        blink_thread = blink_led_background(LED_PATTERN_RESTART_ES)
                        subprocess.run("/etc/init.d/S31emulationstation stop", shell=True, check=True)
                        time.sleep(FRAMEBUFFER_DELAY)
                        show_splash_image(SPLASH_RESTART_ES_PATH, SPLASH_RESTART_ES_DURATION)
                        clear_framebuffer()
                        time.sleep(0.2)
                        blink_thread.join()
                        subprocess.run("batocera-es-swissknife --restart", shell=True, check=True)
                else:
                    # Neither in ES nor in an emulator = reboot system
                    print("Not in ES or emulator - rebooting")
                    blink_thread = blink_led_background(LED_PATTERN_REBOOT)
                    subprocess.run("/etc/init.d/S31emulationstation stop", shell=True, check=True)
                    time.sleep(FRAMEBUFFER_DELAY)
                    show_splash_image(SPLASH_REBOOT_PATH, SPLASH_REBOOT_DURATION)
                    clear_framebuffer()
                    time.sleep(0.2)
                    blink_thread.join()
                    subprocess.run("shutdown -r now", shell=True, check=True)
                    
            except Exception as e:
                print(f"Reset command error: {e}")
            
            reset_press_start = None

def handle_power_button():
    """Handle POWER button press"""
    global led_request
    
    print("POWER button pressed")
    try:
        # Visual feedback
        blink_thread = blink_led_background(LED_PATTERN_SHUTDOWN)
        
        # Check ES state
        output = int(subprocess.check_output(['batocera-es-swissknife', '--espid']))
        
        # Stop ES and show splash
        subprocess.run("/etc/init.d/S31emulationstation stop", shell=True, check=True)
        time.sleep(FRAMEBUFFER_DELAY)
        show_splash_image(SPLASH_SHUTDOWN_PATH, SPLASH_SHUTDOWN_DURATION)
        clear_framebuffer()
        time.sleep(0.2)
        blink_thread.join()
        
        # Prepare hardware
        prepare_for_shutdown()
        
        # Execute shutdown
        if output:
            subprocess.run("batocera-es-swissknife --shutdown", shell=True, check=True)
        else:
            subprocess.run("shutdown -h now", shell=True, check=True)
            
    except Exception as e:
        print(f"Poweroff error: {e}")

def handle_gpio_event(event):
    """Process GPIO events from buttons"""
    if event.line_offset == RESET_PIN:
        # Falling edge (0) is button press, rising edge (1) is button release
        handle_reset_button(event.event_type == gpiod.EdgeEvent.Type.FALLING_EDGE)
    elif event.line_offset == POWER_PIN and event.event_type == gpiod.EdgeEvent.Type.FALLING_EDGE:
        # POWER button only needs falling edge (button press)
        handle_power_button()

def watch_gpio_events():
    """Monitor GPIO pins for button events"""
    try:
        with gpiod.request_lines(
            POWER_CHIP,
            config={
                POWER_PIN: gpiod.LineSettings(
                    edge_detection=Edge.FALLING,
                    bias=Bias.PULL_UP,
                    debounce_period=timedelta(milliseconds=250)
                ),
                RESET_PIN: gpiod.LineSettings(
                    # Monitor both rising and falling edges to detect press and release
                    edge_detection=Edge.BOTH,
                    bias=Bias.PULL_UP,
                    debounce_period=timedelta(milliseconds=100)
                )
            },
        ) as request:
            print("GPIO event monitoring started")
            for event in request.read_edge_events():
                handle_gpio_event(event)
    except Exception as e:
        print(f"Error watching GPIO events: {e}")
        cleanup()
        exit(1)

# Main Execution
def main():
    """Main entry point for the script"""
    # Register signal handlers for proper cleanup
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        init_gpio()
        while True:
            watch_gpio_events()
    except Exception as e:
        print(f"Main loop error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
