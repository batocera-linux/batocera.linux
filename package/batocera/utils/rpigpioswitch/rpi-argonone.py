#!/usr/bin/env python3
"""
Argon ONE fan and power control for Raspberry Pi 4 and Pi 5.
Original source: https://github.com/Elrondo46/argonone
@lbrpdx - Modified to run on Batocera.

Profiles: legacy (V1/V2/M.2), register (V3/register firmware), native (V5).
The auto profile uses architecture defaults, not case/firmware detection.
See README.md in the rpigpioswitch source directory for configuration.

Temperature mappings: /userdata/system/configs/argonone.conf
Defaults: 45=0, 55=10, 60=55, 65=100 (Celsius=percent).
FORCE_REBOOT=1 changes double click from emulator exit to reboot.
"""
import glob
import os
import sys
import time
from threading import Thread

FORCE_REBOOT = 0
DEBUG = 0
config_file = '/userdata/system/configs/argonone.conf'
shutdown_pin = 4


def resolve_profile(requested, arch):
    if requested not in ('auto', 'legacy', 'register', 'native'):
        raise ValueError(f"Unknown Argon ONE profile: {requested}")
    if arch not in ('bcm2711', 'bcm2712'):
        raise ValueError(f"Unsupported Argon ONE platform: {arch}")
    if requested == 'native' and arch != 'bcm2712':
        raise ValueError("The native Argon ONE V5 profile requires a Raspberry Pi 5")
    if requested == 'auto':
        return 'register' if arch == 'bcm2712' else 'legacy'
    return requested


class ArgonOneController:
    def __init__(self, bus, profile):
        if profile not in ('legacy', 'register'):
            raise ValueError(f"Not an I2C Argon ONE profile: {profile}")
        self.bus = bus
        self.profile = profile

    def set_fan_speed(self, speed):
        if not 0 <= speed <= 100:
            raise ValueError(f"Invalid fan speed: {speed}")
        if self.profile == 'register':
            self.bus.write_byte_data(0x1a, 0x80, speed)
        else:
            self.bus.write_byte(0x1a, speed)

    def poweroff(self):
        # Signal the MCU now; it cuts power only after the Pi has halted.
        if self.profile == 'register':
            self.bus.write_byte_data(0x1a, 0x86, 1)
        else:
            self.bus.write_byte(0x1a, 0xff)


# Read fan % speed from the config file
def get_fanspeed(tempval, configlist):
    for curconfig in configlist:
        curpair = curconfig.split("=")
        tempcfg = float(curpair[0])
        fancfg = int(float(curpair[1]))
        if tempval >= tempcfg:
            return fancfg
    return 0

# Load the config file to memory
def load_config(fname):
    newconfig = []
    try:
        with open(fname, "r") as fp:
            for curline in fp:
                if not curline:
                    continue
                tmpline = curline.strip()
                if not tmpline:
                    continue
                if tmpline[0] == "#":
                    continue
                tmppair = tmpline.split("=")
                if len(tmppair) != 2:
                    continue
                tempval = 0
                fanval = 0
                try:
                    tempval = float(tmppair[0])
                    if tempval < 0 or tempval > 100:
                        continue
                except:
                    continue
                try:
                    fanval = int(float(tmppair[1]))
                    if fanval < 0 or fanval > 100:
                        continue
                except:
                    continue
                newconfig.append("{:5.1f}={}".format(tempval, fanval))
        if len(newconfig) > 0:
            newconfig.sort(reverse=True)
    except:
        return []
    return newconfig

# Check the current temperature and adjust fan speed.
def temp_check(controller):
    check_interval = 15
    fanconfig = load_config(config_file) or ["65=100", "60=55", "55=10", "45=0"]
    prevblock = 0
    while True:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as sensor:
            val = int(sensor.readline()) / 1000
        block = get_fanspeed(val, fanconfig)
        if block < prevblock:
            time.sleep(check_interval)
        prevblock = block
        try:
            if DEBUG:
                print(f"Set fan speed {block}% for temp {val}C")
            controller.set_fan_speed(block)
        except OSError as error:
            print(f"Could not set fan speed: {error}", file=sys.stderr)
        time.sleep(check_interval)


def find_gpiochip(gpiod):
    matches = []
    for path in sorted(glob.glob('/dev/gpiochip*')):
        try:
            with gpiod.Chip(path) as chip:
                info = chip.get_info()
                if (info.label in ('pinctrl-bcm2711', 'pinctrl-bcm2835', 'pinctrl-rp1')
                        and info.num_lines > shutdown_pin
                        and chip.get_line_info(shutdown_pin).name == 'GPIO4'):
                    matches.append(path)
        except OSError:
            continue
    if len(matches) != 1:
        raise RuntimeError(f"Cannot uniquely identify header GPIO4: {matches}")
    return matches[0]


def request_power_action(action):
    # swissknife first closes running games and ES, preserving their state.
    # Its successful exit codes are 11 for shutdown and 10 for reboot.
    expected_status = (11 if action == 'shutdown' else 10) << 8
    if os.system(f'/usr/bin/batocera-es-swissknife --{action}') == expected_status:
        return True
    # Without ES, swissknife can return after closing the game without powering off.
    command = 'shutdown -h now' if action == 'shutdown' else 'shutdown -r now'
    if os.system(command) == 0:
        return True
    print(f'Could not request {action}; keeping button monitoring active', file=sys.stderr)
    return False


def shutdown_check(controller, gpiod):
    chip = find_gpiochip(gpiod)
    settings = gpiod.LineSettings(edge_detection=gpiod.line.Edge.BOTH)
    rising_ns = None
    previous_sequence = None
    with gpiod.request_lines(chip, consumer='argonone-button',
                             config={shutdown_pin: settings}) as request:
        while True:
            for event in request.read_edge_events():
                if previous_sequence is not None and event.line_seqno != previous_sequence + 1:
                    rising_ns = None
                previous_sequence = event.line_seqno
                if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                    rising_ns = event.timestamp_ns
                    continue
                if event.event_type != gpiod.EdgeEvent.Type.FALLING_EDGE or rising_ns is None:
                    continue
                pulse_ns = event.timestamp_ns - rising_ns
                rising_ns = None
                if 20_000_000 <= pulse_ns <= 30_000_000:
                    if FORCE_REBOOT:
                        try:
                            controller.set_fan_speed(0)
                        except OSError as error:
                            print(f"Could not stop fan: {error}", file=sys.stderr)
                        if request_power_action('reboot'):
                            return
                    else:
                        os.system('/usr/bin/batocera-es-swissknife --emukill')
                elif 40_000_000 <= pulse_ns <= 50_000_000:
                    # The service's halt hook signals power cut after OS shutdown.
                    if request_power_action('shutdown'):
                        return


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    action = args[0] if args else 'temp'
    if len(args) > 2 or action not in ('temp', 'start', 'stop', 'halt'):
        print('Usage: rpi-argonone [temp|start|stop|halt] [auto|legacy|register|native]', file=sys.stderr)
        return 2
    try:
        if action == 'temp':
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as sensor:
                print(f"Temp: {int(sensor.readline()) / 1000:5.1f}C")
            return 0
        with open('/usr/share/batocera/batocera.arch', 'r') as arch_file:
            profile = resolve_profile(args[1] if len(args) == 2 else 'auto', arch_file.read().strip())
        if profile == 'native':
            if action == 'start':
                print('Argon ONE V5: using the kernel fan and native power button')
            return 0
        import smbus
        bus = smbus.SMBus(1)
        try:
            controller = ArgonOneController(bus, profile)
            if action == 'stop':
                controller.set_fan_speed(0)
            elif action == 'halt':
                controller.poweroff()
            else:
                fan = Thread(target=temp_check, args=(controller,))
                fan.start()
                try:
                    import gpiod
                    shutdown_check(controller, gpiod)
                except Exception as error:
                    print(f"Argon ONE button unavailable; fan control remains active: {error}", file=sys.stderr)
                fan.join()
        finally:
            bus.close()
    except (OSError, ValueError, ImportError) as error:
        print(f"Argon ONE: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
