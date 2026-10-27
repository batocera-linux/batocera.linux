#!/usr/bin/env python3
"""
Argon ONE fan and power control for Raspberry Pi 4 and Pi 5.
Original source: https://github.com/Elrondo46/argonone
@lbrpdx - Modified to run on Batocera.

Temperature mappings: /userdata/system/configs/argonone.conf
FORCE_REBOOT=1 changes double click from emulator exit to reboot.
"""
import fcntl
import glob
import os
import signal
import sys
import time
from threading import Thread

FORCE_REBOOT = 0
DEBUG = 0
config_file = '/userdata/system/configs/argonone.conf'
shutdown_pin = 4


def detect_profile(bus):
    # Probe the duty-cycle register as in Argon's argonregister_checksupport().
    try:
        old = bus.read_byte_data(0x1a, 0x80)
    except OSError:
        return 'legacy'
    if not 0 <= old <= 100:
        return 'legacy'
    speed = old + 1 if old < 99 else 98
    try:
        bus.write_byte_data(0x1a, 0x80, speed)
        time.sleep(1)
        return 'register' if bus.read_byte_data(0x1a, 0x80) == speed else 'legacy'
    except OSError:
        return 'legacy'
    finally:
        bus.write_byte_data(0x1a, 0x80, old)
        time.sleep(1)


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
    flag = '/tmp/shutdown.please'
    created = action == 'shutdown' and not os.path.exists(flag)
    if action == 'shutdown':
        try:
            with open(flag, 'a'):
                pass
        except OSError as error:
            print(f'Could not mark shutdown: {error}', file=sys.stderr)
            return False
    # Swissknife closes games and ES; success is 11 for shutdown, 10 for reboot.
    expected_status = (11 if action == 'shutdown' else 10) << 8
    if os.system(f'/usr/bin/batocera-es-swissknife --{action}') == expected_status:
        return True
    command = 'shutdown -h now' if action == 'shutdown' else 'shutdown -r now'
    if os.system(command) == 0:
        return True
    if created:
        try:
            os.unlink(flag)
        except OSError as error:
            print(f'Could not clear shutdown flag: {error}', file=sys.stderr)
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
                if 15_000_000 <= pulse_ns < 35_000_000:
                    if FORCE_REBOOT:
                        try:
                            controller.set_fan_speed(0)
                        except OSError as error:
                            print(f"Could not stop fan: {error}", file=sys.stderr)
                        if request_power_action('reboot'):
                            return
                    else:
                        os.system('/usr/bin/batocera-es-swissknife --emukill')
                elif 35_000_000 <= pulse_ns <= 60_000_000:
                    # The service's halt hook signals power cut after OS shutdown.
                    if request_power_action('shutdown'):
                        return


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    action = args[0] if args else 'temp'
    if len(args) > 1 or action not in ('temp', 'start', 'stop', 'halt'):
        print('Usage: rpi-argonone [temp|start|stop|halt]', file=sys.stderr)
        return 2
    try:
        if action == 'temp':
            return run_action(action)
        with open('/var/run/argonone.lock', 'a') as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print('Argon ONE controller already running', file=sys.stderr)
                return 1
            return run_action(action)
    except OSError as error:
        print(f'Argon ONE: {error}', file=sys.stderr)
        return 1


def run_action(action):
    try:
        if action == 'temp':
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as sensor:
                print(f"Temp: {int(sensor.readline()) / 1000:5.1f}C")
            return 0
        if action != 'start':
            with open('/var/run/argonone.profile') as state:
                profile = state.read().strip()
            if profile not in ('legacy', 'register'):
                raise ValueError(f'Invalid cached Argon ONE protocol: {profile}')
        import smbus
        bus = smbus.SMBus(1)
        try:
            if action == 'start':
                # Let startup restore the probe and cache its result before stop.
                mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})
                try:
                    profile = detect_profile(bus)
                    with open('/var/run/argonone.profile', 'w') as state:
                        state.write(profile + '\n')
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, mask)
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
        if action in ('stop', 'halt'):
            os.unlink('/var/run/argonone.profile')
    except (OSError, ValueError, ImportError) as error:
        print(f"Argon ONE: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
