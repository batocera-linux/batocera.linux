#!/usr/bin/env python3
"""
PWM + RGB + Multi-LED unified LED driver 
Written for Batocera - @lbrpdx
Updated for kernel module updates - @dmanlfc
Updated for multi-led platform - @dmanlfc
Updated for dual_multiled platform - @dmanlfc
Updated for AYN Odin (odin_mono) platform - @dmanlfc
Updated for Anbernic RG CubeXX - @dmanlfc
Updated for Anbernic RG Vita Pro - @dmanlfc
Updated for R36 Ultra - @ImanolBarba
Updated for Legion Go / Go 2 - @dmanlfc
"""
import glob
import os
import time

from batocera_common.paths import BATOCERA_CONF

DEBUG = 0            # set to 1 for debugging
EFFECT_STEP = 60     # how many colors in the effect
EFFECT_DURATION = 2  # how many seconds
PULSE_DURATION  = 1  # how many seconds
DEFAULT_ES_COLOR = '255 0 165'

####################
# Is your handheld supported by this library?
def batocera_model():
    # Anbernic RG Vita Pro check
    if glob.glob('/sys/class/leds/*::joystick-left'):
        return "rg_vita_pro"
    # Anbernic RG CubeXX check
    if os.path.exists('/proc/device-tree/compatible'):
        with open('/proc/device-tree/compatible', 'r') as f:
            comp = f.read()
            if 'rgcubexx' in comp:
                return "cubexx"
    # Odin 1 Monochrome GPIO layout
    if os.path.exists('/sys/class/leds/left_joystick/brightness'):
        return "odin_mono"
    # Dual Multi-LED check
    if glob.glob('/sys/devices/platform/multi-ledl1/leds/rgb:l1/multi_intensity'):
        return "dual_multiled"
    # Multi-led check (e.g. Mangmi Air X)
    if glob.glob('/sys/devices/platform/multi-led-l1/leds/rgb:l1/multi_intensity'):
        return "multiled"
    # Legion Go S check
    l = '/sys/class/leds/go_s:rgb:joystick_rings/effect'
    if os.path.exists(l):
        return("legiongos")
    # Legion Go / Go 2 check
    l_go = '/sys/class/leds/go:rgb:joystick_rings/effect'
    if os.path.exists(l_go):
        return("legiongo")
    # Generic check for modern joystick ring LEDs from ayaneo-platform/ayn-platform
    if glob.glob('/sys/class/leds/*:rgb:joystick_rings/multi_intensity'):
        return "rgb"
    # R36 Ultra check
    l = '/sys/class/leds/keros::ambient/brightness'
    if os.path.exists(l):
        return("r36ultra")
    # Standard RGB check
    l = '/sys/class/leds/multicolor:chassis/multi_intensity'
    if os.path.exists(l):
        return("rgb")
    # Addressable RGB check
    c = glob.glob('/sys/class/leds/l:b?')
    if c:
        return("rgbaddr")
    # PWM check
    c = glob.glob('/sys/class/pwm/pwmchip*/device/name')
    for t in c:
        with open (t) as f:
            m = f.readline().strip()
            if m == 'htr3212-pwm':
                return("pwm")
    return "Unsupported"


####################
# Get a value from batocera.conf
def batoconf(key):
    with open(BATOCERA_CONF) as f:
        for line in f:
            if not line.startswith(key+"="):
                continue
            rest = line.split("=", 1)[1]
            nocomment = rest.split("#", 1)[0].strip()
            return(nocomment) # First one is enough
    return None

def batoconf_color():
    rgb = batoconf("led.colour")
    if rgb == None:
        rgb = DEFAULT_ES_COLOR
    try:
        [ r, g, b ] = rgb.split(" ")
    except:
        if len (rgb) == 6:
            r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
        else:
            [ r, g, b ] = DEFAULT_ES_COLOR.split(" ")
    if DEBUG:
        print (f"batocera.conf said led.colour = {r} {g} {b}")
    return [ r, g, b ]


####################
# Anbernic RG Vita Pro LED Controller
class rgvitaproled(object):
    def __init__(self):
        left_glob = glob.glob('/sys/class/leds/*::joystick-left')
        right_glob = glob.glob('/sys/class/leds/*::joystick-right')
        
        self.left_path = left_glob[0] if left_glob else None
        self.right_path = right_glob[0] if right_glob else None
        
        self.sysfs_path = None
        if self.left_path:
            try:
                # Equivalent to readlink -f on the left joystick device path
                self.sysfs_path = os.path.realpath(os.path.join(self.left_path, 'device'))
            except Exception:
                pass
                
        self.max_val = 255
        self.current_color = "000000"
        self._init_hardware()

    def _init_hardware(self):
        if self.sysfs_path:
            try:
                # Enable the MCU switch
                with open(os.path.join(self.sysfs_path, 'led_switch'), 'w') as f:
                    f.write('1')
            except Exception:
                pass

    def _write_hardware(self, brightness, r, g, b):
        if self.sysfs_path:
            try:
                # Force mode 5 (custom/static RGB mode)
                with open(os.path.join(self.sysfs_path, 'led_mode'), 'w') as f:
                    f.write('5')
            except Exception:
                pass

        # Write parameters to both left and right joystick rings
        for path in [self.left_path, self.right_path]:
            if path:
                try:
                    with open(os.path.join(path, 'brightness'), 'w') as f:
                        f.write(str(brightness))
                except Exception:
                    pass
                try:
                    with open(os.path.join(path, 'multi_intensity'), 'w') as f:
                        f.write(f"{r} {g} {b}")
                except Exception:
                    pass

    def set_color(self, rgb):
        if rgb in ["OFF", "000000"]:
            self.turn_off()
            return

        b_conf = batoconf("led.brightness")
        if b_conf is None:
            b_conf = 255
        else:
            try:
                pct = float(b_conf)
                if pct <= 100:
                    b_conf = int((pct / 100.0) * 255)
                else:
                    b_conf = int(pct)
            except ValueError:
                b_conf = 255

        if rgb == "ESCOLOR":
            r, g, b = batoconf_color()
            self.current_color = f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "PULSE":
            self.pulse_effect()
            return
        else:
            r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
            self.current_color = rgb
        
        self._write_hardware(b_conf, r, g, b)

    def set_color_dec(self, rgb_str):
        try:
            r, g, b = [int(x) for x in rgb_str.split()]
            b_conf = batoconf("led.brightness") or 255
            try:
                pct = float(b_conf)
                if pct <= 100:
                    b_conf = int((pct / 100.0) * 255)
                else:
                    b_conf = int(pct)
            except ValueError:
                b_conf = 255
            self.current_color = f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
            self._write_hardware(b_conf, r, g, b)
        except Exception:
            pass

    def get_color(self) -> str:
        if self.left_path:
            try:
                with open(os.path.join(self.left_path, 'multi_intensity'), 'r') as f:
                    rgb = f.readline().strip()
                    r, g, b = rgb.split()
                    return f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
            except Exception:
                pass
        return self.current_color

    def get_color_dec(self) -> str:
        if self.left_path:
            try:
                with open(os.path.join(self.left_path, 'multi_intensity'), 'r') as f:
                    return f.readline().strip()
            except Exception:
                pass
        r = hex_to_dec(self.current_color[0:2])
        g = hex_to_dec(self.current_color[2:4])
        b = hex_to_dec(self.current_color[4:6])
        return f"{r} {g} {b}"

    def rainbow_effect(self):
        # Maps "RAINBOW" to Hardware Mode 3 (rainbowfade) with speed 5
        if self.sysfs_path:
            try:
                with open(os.path.join(self.sysfs_path, 'led_switch'), 'w') as f:
                    f.write('1')
                with open(os.path.join(self.sysfs_path, 'led_mode'), 'w') as f:
                    f.write('3')
                with open(os.path.join(self.sysfs_path, 'led_speed'), 'w') as f:
                    f.write('5')
            except Exception:
                pass

    def pulse_effect(self):
        # Maps "PULSE" to Hardware Mode 2 (breathing/pulse)
        if self.sysfs_path:
            try:
                with open(os.path.join(self.sysfs_path, 'led_switch'), 'w') as f:
                    f.write('1')
                with open(os.path.join(self.sysfs_path, 'led_mode'), 'w') as f:
                    f.write('2')
            except Exception:
                pass

    def turn_off(self):
        self.current_color = "000000"
        if self.sysfs_path:
            try:
                with open(os.path.join(self.sysfs_path, 'led_switch'), 'w') as f:
                    f.write('0')
            except Exception:
                pass
        for path in [self.left_path, self.right_path]:
            if path:
                try:
                    with open(os.path.join(path, 'brightness'), 'w') as f:
                        f.write('0')
                except Exception:
                    pass

    def set_brightness(self, b):
        self.set_color("ESCOLOR")

    def set_brightness_conf(self):
        self.set_color("ESCOLOR")

    def get_brightness(self):
        if self.left_path:
            try:
                with open(os.path.join(self.left_path, 'brightness'), 'r') as f:
                    b = f.readline().strip()
                return (b, "255")
            except Exception:
                pass
        b_conf = batoconf("led.brightness") or "100"
        return (str(b_conf), "100")


####################
# Anbernic RG CubeXX LED Controller
class cubexxled(object):
    def __init__(self):
        self.serial_dev = '/dev/ttyS2'
        self.gpio_path = '/sys/class/leds/rgb:kbd_backlight/brightness'
        self.max_val = 255
        self.current_color = "000000"
        self._init_hardware()

    def _init_hardware(self):
        try:
            # Configure serial parameters
            os.system(f'stty -F {self.serial_dev} 115200 -opost -isig -icanon -echo')
        except Exception:
            pass

    def _write_hardware(self, brightness, r, g, b):
        try:
            # Enable GPIO power to the LED MCU
            with open(self.gpio_path, 'w') as f:
                f.write('1')
            
            # Construct the fixed-length 51-byte packet
            payload = bytearray()
            payload.append(1)                 # LED_MODE
            payload.append(int(brightness))   # BRIGHTNESS
            
            # 8 LEDs for the Right Ring
            for _ in range(8):
                payload.extend([int(r), int(g), int(b)])
                
            # 8 LEDs for the Left Ring
            for _ in range(8):
                payload.extend([int(r), int(g), int(b)])
                
            # Generate the 8-bit checksum
            checksum = sum(payload) & 0xFF
            payload.append(checksum)
            
            # Write out payload
            with open(self.serial_dev, 'wb') as f:
                f.write(payload)
        except Exception as e:
            if DEBUG:
                print(f"Error writing to CubeXX hardware: {e}")

    def set_color(self, rgb):
        if rgb in ["OFF", "000000"]:
            self.turn_off()
            return

        b_conf = batoconf("led.brightness")
        if b_conf is None:
            b_conf = 255
        else:
            # Handle config values scaling correctly (percentage to absolute 255 value)
            try:
                pct = float(b_conf)
                if pct <= 100:
                    b_conf = int((pct / 100.0) * 255)
                else:
                    b_conf = int(pct)
            except ValueError:
                b_conf = 255

        if rgb == "ESCOLOR":
            r, g, b = batoconf_color()
            self.current_color = f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "PULSE":
            self.pulse_effect()
            return
        else:
            r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
            self.current_color = rgb
        
        self._write_hardware(b_conf, r, g, b)

    def set_color_dec(self, rgb_str):
        try:
            r, g, b = [int(x) for x in rgb_str.split()]
            b_conf = batoconf("led.brightness") or 255
            try:
                pct = float(b_conf)
                if pct <= 100:
                    b_conf = int((pct / 100.0) * 255)
                else:
                    b_conf = int(pct)
            except ValueError:
                b_conf = 255
            self.current_color = f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
            self._write_hardware(b_conf, r, g, b)
        except Exception:
            pass

    def get_color(self) -> str:
        return self.current_color

    def get_color_dec(self) -> str:
        r = hex_to_dec(self.current_color[0:2])
        g = hex_to_dec(self.current_color[2:4])
        b = hex_to_dec(self.current_color[4:6])
        return f"{r} {g} {b}"

    def rainbow_effect(self):
        prev = self.get_color()
        for i in range(0, EFFECT_STEP):
            o = getRainbowRGB(float(i/EFFECT_STEP))
            self.set_color(o)
            time.sleep(EFFECT_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def pulse_effect(self):
        prev = self.get_color()
        for i in range(0, EFFECT_STEP):
            o = getPulseRGB(i, EFFECT_STEP, prev)
            self.set_color(o)
            time.sleep(PULSE_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def turn_off(self):
        self.current_color = "000000"
        # Zero out RGB color registry
        self._write_hardware(0, 0, 0, 0)
        # Power down the MCU
        try:
            with open(self.gpio_path, 'w') as f:
                f.write('0')
        except Exception:
            pass

    def set_brightness(self, b):
        self.set_color("ESCOLOR")

    def set_brightness_conf(self):
        self.set_color("ESCOLOR")

    def get_brightness(self):
        b_conf = batoconf("led.brightness") or "100"
        return (str(b_conf), "100")


####################
# AYN Odin 1 Monochrome (Blue-only GPIO LEDs, Binary On/Off)
class odinmono(object):
    def __init__(self):
        self.paths = [
            '/sys/class/leds/left_joystick/',
            '/sys/class/leds/right_joystick/',
            '/sys/class/leds/left_side/',
            '/sys/class/leds/right_side/'
        ]
        self.max_val = 1
        # Unlock manual control on boot
        self.disable_triggers()

    def disable_triggers(self):
        for p in self.paths:
            try:
                with open(p + 'trigger', 'w') as f:
                    f.write('none')
            except Exception:
                pass

    def _write_hardware(self, value):
        # Convert any non-zero value/brightness percentage to binary 1 (On)
        hw_value = 1 if int(value) > 0 else 0
        for p in self.paths:
            try:
                with open(p + 'brightness', 'w') as f:
                    f.write(str(hw_value))
            except Exception:
                pass

    def set_color(self, rgb):
        if rgb in ["OFF", "000000"]:
            self.turn_off()
            return

        if rgb == "ESCOLOR":
            b_conf = batoconf("led.brightness")
            if b_conf is None: 
                b_conf = 1
            self._write_hardware(b_conf)
        elif rgb in ["RAINBOW", "PULSE"]:
            self.pulse_effect()
        else:
            r = hex_to_dec(rgb[0:2])
            g = hex_to_dec(rgb[2:4])
            b = hex_to_dec(rgb[4:6])
            if r > 0 or g > 0 or b > 0:
                self._write_hardware(1)
            else:
                self.turn_off()

    def set_color_dec(self, rgb_str):
        try:
            vals = [int(x) for x in rgb_str.split()]
            if any(v > 0 for v in vals):
                self._write_hardware(1)
            else:
                self.turn_off()
        except Exception:
            pass

    def get_color(self) -> str:
        try:
            with open(self.paths[0] + 'brightness', 'r') as f:
                b = int(f.readline().strip())
                if b > 0:
                    return "FFFFFF"
        except Exception:
            pass
        return "000000"

    def get_color_dec(self) -> str:
        try:
            with open(self.paths[0] + 'brightness', 'r') as f:
                b = int(f.readline().strip())
                if b > 0:
                    return "255 255 255"
        except Exception:
            pass
        return "0 0 0"

    def rainbow_effect(self):
        self.pulse_effect()

    def pulse_effect(self):
        # Simple blinking notification pulse
        try:
            with open(self.paths[0] + 'brightness', 'r') as f:
                prev = int(f.readline().strip())
        except Exception:
            prev = 1

        self._write_hardware(0)
        time.sleep(0.2)
        self._write_hardware(1)
        time.sleep(0.2)
        self._write_hardware(0)
        time.sleep(0.2)
        self._write_hardware(prev)

    def turn_off(self):
        self._write_hardware(0)

    def set_brightness(self, b):
        self._write_hardware(b)

    def set_brightness_conf(self):
        self.set_color("ESCOLOR")

    def get_brightness(self):
        try:
            with open(self.paths[0] + 'brightness', 'r') as f:
                b = f.readline().strip()
            return (b, "1")
        except Exception:
            return ("-1", "-1")

####################
# Handhelds using the Dual Multi-LED Platform
class dual_multiled(object):
    def __init__(self):
        # Scan for both left (l1-l3) and right (r1-r3) paths
        self.left_paths = glob.glob('/sys/devices/platform/multi-ledl*/leds/rgb:l*/')
        self.right_paths = glob.glob('/sys/devices/platform/multi-ledr*/leds/rgb:r*/')
        self.all_paths = self.left_paths + self.right_paths
        self.max_val = 255

    def _write_hardware(self, brightness, r, g, b):
        # Driver expects "Blue Green Red" format
        color_str = f"{r} {g} {b}"
        for p in self.all_paths:
            try:
                with open(p + 'brightness', 'w') as f:
                    f.write(str(brightness))
                with open(p + 'multi_intensity', 'w') as f:
                    f.write(color_str)
            except Exception:
                pass

    def set_color(self, rgb):
        if rgb == "OFF":
            self.turn_off()
            return

        # Fetch system brightness configuration
        b_conf = batoconf("led.brightness")
        if b_conf is None: 
            b_conf = 255
        
        if rgb == "ESCOLOR":
            r, g, b = batoconf_color()
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "PULSE":
            self.pulse_effect()
            return
        else:
            r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
        
        self._write_hardware(b_conf, r, g, b)

    def set_color_dec(self, rgb_str):
        try:
            r, g, b = [int(x) for x in rgb_str.split()]
            b_conf = batoconf("led.brightness") or 255
            self._write_hardware(b_conf, r, g, b)
        except Exception:
            pass

    def get_color(self):
        if not self.all_paths:
            return "000000"
        try:
            with open(self.all_paths[0] + 'multi_intensity', 'r') as f:
                r, g, b = f.readline().strip().split()
                return f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
        except Exception:
            return "000000"

    def get_color_dec(self):
        if not self.all_paths:
            return "0 0 0"
        try:
            with open(self.all_paths[0] + 'multi_intensity', 'r') as f:
                r, g, b = f.readline().strip().split()
                return f"{r} {g} {b}"
        except Exception:
            return "0 0 0"

    def rainbow_effect(self):
        prev = self.get_color()
        for i in range(0, EFFECT_STEP):
            o = getRainbowRGB(float(i/EFFECT_STEP))
            self.set_color(o)
            time.sleep(EFFECT_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def pulse_effect(self):
        prev = self.get_color()
        for i in range(0, EFFECT_STEP):
            o = getPulseRGB(i, EFFECT_STEP, prev)
            self.set_color(o)
            time.sleep(PULSE_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def turn_off(self):
        self._write_hardware(0, 0, 0, 0)

    def set_brightness(self, b):
        self.set_color("ESCOLOR")

    def set_brightness_conf(self):
        self.set_color("ESCOLOR")

    def get_brightness(self):
        if not self.all_paths:
            return ("-1", "-1")
        try:
            with open(self.all_paths[0] + 'brightness', 'r') as f:
                b = f.readline().strip()
            return (b, "255")
        except Exception:
            return ("-1", "-1")

####################
# Handhelds using the Multi-LED Platform (i.e. Mangmi Air X)
class multiled(object):
    def __init__(self):
        # Glob all possible LED nodes (l1..l7, r1..r7)
        self.paths = glob.glob('/sys/devices/platform/multi-led-*/leds/rgb:*/')
        self.max_val = 255

    def _write_hardware(self, brightness, r, g, b):
        # Based on user shell script: multi_intensity expects "Blue Green Red"
        color_str = f"{r} {g} {b}"
        for p in self.paths:
            try:
                with open(p + 'brightness', 'w') as f:
                    f.write(str(brightness))
                with open(p + 'multi_intensity', 'w') as f:
                    f.write(color_str)
            except:
                pass

    def set_color(self, rgb):
        if rgb == "OFF":
            self.turn_off()
            return

        # Get brightness from config
        b_conf = batoconf("led.brightness")
        if b_conf is None: b_conf = 255
        
        if rgb == "ESCOLOR":
            r, g, b = batoconf_color()
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "PULSE":
            self.pulse_effect()
            return
        else:
            r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
        
        self._write_hardware(b_conf, r, g, b)

    def set_color_dec(self, rgb_str):
        try:
            r, g, b = [int(x) for x in rgb_str.split()]
            b_conf = batoconf("led.brightness") or 255
            self._write_hardware(b_conf, r, g, b)
        except:
            pass

    def get_color(self):
        try:
            with open(self.paths[0] + 'multi_intensity', 'r') as f:
                r, g, b = f.readline().strip().split()
                return f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
        except:
            return "000000"

    def get_color_dec(self):
        try:
            with open(self.paths[0] + 'multi_intensity', 'r') as f:
                b, g, r = f.readline().strip().split()
                return f"{r} {g} {b}"
        except:
            return "0 0 0"

    def rainbow_effect(self):
        prev = self.get_color()
        for i in range(0, EFFECT_STEP):
            o = getRainbowRGB(float(i/EFFECT_STEP))
            self.set_color(o)
            time.sleep(EFFECT_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def pulse_effect(self):
        prev = self.get_color()
        for i in range(0, EFFECT_STEP):
            o = getPulseRGB(i, EFFECT_STEP, prev)
            self.set_color(o)
            time.sleep(PULSE_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def turn_off(self):
        self._write_hardware(0, 0, 0, 0)

    def set_brightness(self, b):
        self.set_color("ESCOLOR")

    def set_brightness_conf(self):
        self.set_color("ESCOLOR")

    def get_brightness(self):
        try:
            with open(self.paths[0] + 'brightness', 'r') as f:
                b = f.readline().strip()
            return (b, "255")
        except:
            return ("-1", "-1")

####################
# Generic Lenovo Legion Go Family Base Class
class legiongo_family_led(object):
    def __init__(self, prefix):
        self.bpath           = f'/sys/class/leds/{prefix}:rgb:joystick_rings/'
        self.effect_file     = self.bpath + 'effect'
        self.mode_file       = self.bpath + 'mode'
        self.speed_file      = self.bpath + 'speed'
        self.enabled_file    = self.bpath + 'enabled'
        self.color_file      = self.bpath + 'multi_intensity'
        self.brightness_file = self.bpath + 'brightness'
        self.max_brightness  = self.bpath + 'max_brightness'

        if not self._write_verified(self.mode_file, 'custom'):
            print(f"Warning: could not confirm Legion Go ({prefix}) mode=custom after retries")
        if not self._write_verified(self.enabled_file, 'true'):
            print(f"Warning: could not confirm Legion Go ({prefix}) enabled=true after retries")

    def _write_verified(self, path, value, retries=10, delay=0.5):
        for attempt in range(retries):
            try:
                with open(path, 'w') as f:
                    f.write(value)
                with open(path, 'r') as f:
                    if f.read().strip() == value:
                        if DEBUG:
                            print(f"{path} -> {value} confirmed on attempt {attempt+1}")
                        return True
            except Exception as e:
                if DEBUG:
                    print(f"Attempt {attempt+1} writing {value} to {path} failed: {e}")
            time.sleep(delay)
        return False

    def set_color (self, rgb):
        if len(rgb) != 6 and rgb not in [ "PULSE", "RAINBOW", "OFF", "ESCOLOR" ]:
            print (f'Error Color {rgb} is invalid')
            return

        # Always ensure the LEDs are on, unless explicitly turned off
        if rgb != "OFF":
            self._write_verified(self.enabled_file, 'true')
            self.set_brightness_conf()

        try:
            if rgb == "PULSE":
                if DEBUG: print('Set effect to: breathe')
                self._write_verified(self.effect_file, 'breathe')
                return
            elif rgb == "RAINBOW":
                if DEBUG: print('Set effect to: rainbow')
                self._write_verified(self.effect_file, 'rainbow')
                return
            elif rgb == "OFF":
                self.turn_off()
                return

            # For static colors, set effect to monocolor first
            if DEBUG: print('Set effect to: monocolor')
            self._write_verified(self.effect_file, 'monocolor')

            if rgb == "ESCOLOR":
                r, g, b = batoconf_color()
                out = f'{r} {g} {b}'
            else:
                r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
                out = f'{hex_to_dec(r)} {hex_to_dec(g)} {hex_to_dec(b)}'

            if DEBUG: print (f'Set color to: {out}')
            self._write_verified(self.color_file, out)

        except Exception as e:
            if DEBUG:
                print(f'Error setting Legion Go color: {e}')

    def get_color (self) -> str:
        try:
            with open(self.enabled_file, 'r') as f:
                if f.read().strip() == 'false':
                    return "000000"
        except:
            pass

        try:
            with open (self.color_file, 'r') as p:
                rgb = p.readline().strip()
                [ r, g, b ] = rgb.split(" ")
                out = f'{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}'
                return (out)
        except:
            return "000000"

    def set_color_dec (self, rgb):
        try:
            with open(self.enabled_file, 'w') as f:
                f.write('true')
        except Exception:
            pass

        try:
            if DEBUG: print('Set effect to: monocolor')
            with open (self.effect_file, 'w') as p: p.write('monocolor')
            if DEBUG: print (f'Set color to: {rgb}')
            with open (self.color_file, 'w') as p:
                p.write(rgb)
        except Exception as e:
            if DEBUG: print(f"Error setting dec color: {e}")


    def get_color_dec (self) -> str:
        try:
            with open(self.enabled_file, 'r') as f:
                if f.read().strip() == 'false':
                    return "0 0 0"
        except:
            pass

        try:
            with open (self.color_file, 'r') as p:
                return p.readline().strip()
        except:
            return "0 0 0"

    def rainbow_effect(self):
        try:
            with open(self.enabled_file, 'w') as f:
                f.write('true')
        except Exception:
            pass
        self.set_color("RAINBOW")

    def pulse_effect(self):
        try:
            with open(self.enabled_file, 'w') as f:
                f.write('true')
        except Exception:
            pass
        self.set_color("PULSE")

    def turn_off(self):
        if DEBUG: print('Turning off LED')
        try:
            with open(self.enabled_file, 'w') as f:
                f.write('false')
        except Exception as e:
            if DEBUG: print(f"Could not disable LED interface: {e}")
        self.set_brightness(0)

    def set_brightness (self, b):
        try:
            with open (self.brightness_file, 'w') as p:
                p.write(str(b))
        except Exception as e:
            if DEBUG: print(f"Could not set brightness: {e}")

    def set_brightness_conf (self):
        conf = batoconf("led.brightness")
        if conf is None:
            conf = 100 
        try:
            with open(self.max_brightness, 'r') as m:
                max_v = int(m.readline().strip())
            
            percentage = max(0, min(100, float(conf)))
            scaled_value = int((percentage / 100.0) * max_v)
            self.set_brightness(scaled_value)
        except:
            self.set_brightness(255)

    def get_brightness (self):
        try:
            with open (self.brightness_file, 'r') as p:
                b = p.readline().strip()
            with open (self.max_brightness, 'r') as m:
                x = m.readline().strip()
            return (b, x)
        except:
            return ("-1", "-1")

class legiongosled(legiongo_family_led):
    def __init__(self):
        super().__init__(prefix="go_s")

class legiongoled(legiongo_family_led):
    def __init__(self):
        super().__init__(prefix="go")

####################
# R36 Ultra
class r36ultraled():
    def __init__(self):
        self.modepath = '/sys/class/leds/keros::ambient/brightness'
        self.modemap = {
            "000000": 0,
            "FF0000": 1,
            "FFFF00": 2,
            "00FF00": 3,
            "00FFFF": 4,
            "0000FF": 5,
            "FF00FF": 6,
            "FFFFFF": 7,
        }

    def set_mode(self, mode: int) -> None:
        with open(self.modepath, "w") as f:
            f.write(str(mode))


    def set_color(self, rgb: str) -> None:
        # The R36 ultra has a preset number of modes, and the colours can't be adjusted.
        # These modes are:
        # 0. Off
        # 1. Red     (FF0000)
        # 2. Yellow  (FFFF00)
        # 3. Green   (00FF00)
        # 4. Cyan    (00FFFF)
        # 5. Blue    (0000FF)
        # 6. Magenta (FF00FF)
        # 7. White   (FFFFFF)
        # 8. Pulse - Alternates all the modes above fading in and out
        # 9. Rainbow - Circular rainbow effect
        #
        # Due to this, we can't set arbitrary RGB colours, but we can approximate which
        # is the closest one. Beats having nothing I guess.

        if rgb == "ESCOLOR":
            r, g, b = batoconf_color()
            rgb = f"{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}"
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "PULSE":
            self.pulse_effect()
            return
        elif rgb == "OFF":
            self.turn_off()
            return

        rounded_hex = ""

        try:
            for i in range(0, 6, 2):
                channel_val = hex_to_dec(rgb[i:i+2])

                if channel_val < 0x80:
                    rounded_hex += "00"
                else:
                    rounded_hex += "FF"

            if rounded_hex in self.modemap:
                self.set_mode(self.modemap[rounded_hex])
            else:
                print(f"Unable to translate color {rgb} to a suitable mode. Converted value: {rounded_hex}")
        except ValueError as e:
            print(f"Bad integer conversion: {e}")


    def get_color(self) -> str:
        try:
            with open (self.modepath, 'r') as f:
                mode = f.readline().strip()
            return list(self.modemap.keys())[list(self.modemap.values()).index(int(mode))]
        except:
            return "000000"

    def set_color_dec(self, rgb: str) -> None:
        hex = ""
        try:
            for color in rgb.split():
                hex += dec_to_hex(int(color))
        except ValueError as e:
            print(f"Bad integer conversion: {e}")
        self.set_color(hex)

    def get_color_dec(self) -> str:
        hex = self.get_color()
        dec = []

        try:
            for i in range(0, 6, 2):
                dec.append(str(hex_to_dec(hex[i:i+2])))

            return " ".join(dec)

        except ValueError as e:
            print(f"Bad integer conversion: {e}")

        return "0 0 0"

    def rainbow_effect(self) -> None:
        self.set_mode(9)

    def pulse_effect(self) -> None:
        self.set_mode(8)

    def turn_off(self) -> None:
        self.set_mode(0)

    def set_brightness (self, b: int) -> None:
        print("Brightness is not adjusteable")

    def set_brightness_conf (self) -> None:
        print("Brightness is not adjusteable")

    def get_brightness (self) -> tuple[str, str]:
        return ("-1", "-1")


####################
# Handhelds that use a direct RGB interface (easy peasy)
class rgbled(object):
    def __init__(self):
        self.bpath = None
        
        # Use glob to find newer joystick ring LEDs dynamically
        found_paths = glob.glob('/sys/class/leds/*:rgb:joystick_rings/')
        if found_paths:
            self.bpath = found_paths[0] # Take the first match
        else:
            # Fallback to the older multicolor path for other devices
            fallback_path = '/sys/class/leds/multicolor:chassis/'
            if os.path.exists(fallback_path):
                self.bpath = fallback_path

        if self.bpath is None:
            raise RuntimeError("Could not find a valid RGB LED sysfs path.")

        self.base            = self.bpath + 'multi_intensity'
        self.brightness      = self.bpath + 'brightness'
        self.max_brightness  = self.bpath + 'max_brightness'

    def set_color (self, rgb):
        if len(rgb) != 6 and rgb not in [ "PULSE", "RAINBOW", "OFF", "ESCOLOR" ]:
            print (f'Error Color {rgb} is invalid')
            return
        if rgb == "PULSE":
            self.pulse_effect()
            return
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "OFF":
            self.turn_off()
            return
        elif rgb == "ESCOLOR":
            r, g, b = batoconf_color()
            out = f'{r} {g} {b}'
        else:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
            out = f'{hex_to_dec(r)} {hex_to_dec(g)} {hex_to_dec(b)}'
        if (DEBUG):
            print (f'Set color to: {out}')
        with open (self.base, 'w') as p:
            p.write(out)

    def get_color (self) -> str:
        with open (self.base, 'r') as p:
            rgb = p.readline().strip()
            [ r, g, b ] = rgb.split(" ")
            out = f'{dec_to_hex(r)}{dec_to_hex(g)}{dec_to_hex(b)}'
            return (out)

    def set_color_dec (self, rgb):
        if (DEBUG):
            print (f'Set color to: {rgb}')
        with open (self.base, 'w') as p:
            p.write(rgb)

    def get_color_dec (self) -> str:
        with open (self.base, 'r') as p:
            rgb = p.readline().strip()
            [ r, g, b ] = rgb.split(" ")
            out = f'{r} {g} {b}'
            return (out)

    def rainbow_effect(self):
        prev = self.get_color()
        for i in range (0, EFFECT_STEP):
            o = getRainbowRGB(float (i/EFFECT_STEP))
            self.set_color(o)
            time.sleep(EFFECT_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def pulse_effect(self):
        prev = self.get_color()
        for i in range (0, EFFECT_STEP):
            o = getPulseRGB(i, EFFECT_STEP, prev)
            self.set_color(o)
            time.sleep(PULSE_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def turn_off(self):
        self.set_color("000000")

    def set_brightness (self, b):
        with open (self.brightness, 'w') as p:
            p.write(str(b))

    def set_brightness_conf (self):
        conf = batoconf("led.brightness")
        if conf is None:
            conf = 100
        try:
            with open(self.max_brightness, 'r') as m:
                max_v = int(m.readline().strip())
            
            percentage = max(0, min(100, float(conf)))
            scaled_value = int((percentage / 100.0) * max_v)
            self.set_brightness(scaled_value)
        except:
            self.set_brightness(255)

    def get_brightness (self):
        with open (self.brightness, 'r') as p:
            b = p.readline().strip()
        with open (self.max_brightness, 'r') as m:
            x = m.readline().strip()
        return (b, x)


####################
# Handhelds that use a PWM interface (trickier)
class pwmled(object):
    def __init__(self):
        c = glob.glob('/sys/class/pwm/pwmchip*')
        self.period = 100
        self.led = []
        for t in c:
            ret = self.pwmchip_init(t)
            if ret:
                self.led.append(ret)
        self.brightness     = -1
        self.max_brightness = -1

    def pwmchip_init (self, chip):
        self.base   = chip
        self.device = self.base + '/device/name'
        if not os.path.isdir(self.base):
            if (DEBUG):
                print ('PWM device driver not found: ' + self.base)
            return None
        try:
            with open (self.device) as f:
                m = f.readline().strip()
                if m != 'htr3212-pwm':
                    if (DEBUG):
                        print ('PWM device not a supported LED: ' + self.device)
                    return None
            with open (self.base + '/npwm') as f:
                npwm = int(f.readline().strip())
            if (npwm % 3) != 0:
                if (DEBUG):
                    print (f'Error: PWM is not a supported RGB LED: {npwm} pins')
                return None
            for i in range(npwm):
                p = self.base + f'/pwm{i}'
                if not os.path.isdir(p):
                    with open (self.base + '/export', 'w') as ex:
                        ex.write(str(i))
                with open (p + '/enable', 'w') as pe, \
                        open (p + '/period', 'w') as pp, \
                        open (p + '/duty_cycle', 'w') as pd:
                    pe.write('1')
                    pp.write(str(self.period))
                    # pd.write('0')
        except Exception as e:
            if (DEBUG):
                print('Error: PWM device is not a supported LED: {} ({})'.format(self.base, e))
            return None
        return (chip)

    def _get_factor(self):
        val = batoconf("led.brightness")
        if val is None: return 1.0
        try:
            return max(0, min(100, float(val))) / 100.0
        except: return 1.0

    def set_color (self, rgb):
        if len(rgb) != 6 and rgb not in [ "PULSE", "RAINBOW", "OFF", "ESCOLOR" ]:
            print (f'Error Color {rgb} is invalid')
            return
        if rgb == "PULSE":
            self.pulse_effect()
            return
        elif rgb == "RAINBOW":
            self.rainbow_effect()
            return
        elif rgb == "OFF":
            self.turn_off()
            return
        
        factor = self._get_factor()
        if rgb == "ESCOLOR":
            r_raw, g_raw, b_raw = batoconf_color()
        else:
            r_raw, g_raw, b_raw = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])

        r = str(int((int(r_raw)/255.0) * factor * self.period))
        g = str(int((int(g_raw)/255.0) * factor * self.period))
        b = str(int((int(b_raw)/255.0) * factor * self.period))

        if (DEBUG):
            print (f'Set color to: {r} {g} {b}')
        for l in self.led:
            for i in range (0, 12, 3):
                with open (l + f'/pwm{i}/duty_cycle', 'w') as p:
                    p.write(r)
            for i in range (1, 12, 3):
                with open (l + f'/pwm{i}/duty_cycle', 'w') as p:
                    p.write(g)
            for i in range (2, 12, 3):
                with open (l + f'/pwm{i}/duty_cycle', 'w') as p:
                    p.write(b)

    def get_color (self) -> str:
        if not self.led:
            return "000000"
        l = self.led[0]
        with open (l + f'/pwm0/duty_cycle', 'r') as p:
                r = p.readline().strip()
        with open (l + f'/pwm1/duty_cycle', 'r') as p:
                g = p.readline().strip()
        with open (l + f'/pwm2/duty_cycle', 'r') as p:
                b = p.readline().strip()
        out = f'{pwm_to_hex(r, self.period)}{pwm_to_hex(g, self.period)}{pwm_to_hex(b, self.period)}'
        return(out)

    def set_color_dec (self, rgb):
        int_list = [int(x) for x in rgb.split()]
        if len(int_list) != 3:
            print (f'Argument expects three ints for R G B, not {rgb}')
            return (1)
        
        factor = self._get_factor()
        r = str(int((int_list[0]/255.0) * factor * self.period))
        g = str(int((int_list[1]/255.0) * factor * self.period))
        b = str(int((int_list[2]/255.0) * factor * self.period))

        if (DEBUG):
            print (f'Set color to: {r} {g} {b}')
        for l in self.led:
            for i in range (0, 12, 3):
                with open (l + f'/pwm{i}/duty_cycle', 'w') as p:
                    p.write(r)
            for i in range (1, 12, 3):
                with open (l + f'/pwm{i}/duty_cycle', 'w') as p:
                    p.write(g)
            for i in range (2, 12, 3):
                with open (l + f'/pwm{i}/duty_cycle', 'w') as p:
                    p.write(b)

    def get_color_dec (self) -> str:
        l = self.led[0]
        with open (l + f'/pwm0/duty_cycle', 'r') as p:
                r = p.readline().strip()
        with open (l + f'/pwm1/duty_cycle', 'r') as p:
                g = p.readline().strip()
        with open (l + f'/pwm2/duty_cycle', 'r') as p:
                b = p.readline().strip()
        out = f'{pwm_to_dec(r, self.period)} {pwm_to_dec(g, self.period)} {pwm_to_dec(b, self.period)}'
        return(out)

    def rainbow_effect(self):
        prev = self.get_color()
        for i in range (0, EFFECT_STEP):
            o = getRainbowRGB(float (i/EFFECT_STEP))
            self.set_color(o)
            time.sleep(EFFECT_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def pulse_effect(self):
        prev = self.get_color()
        for i in range (0, EFFECT_STEP):
            o = getPulseRGB(i, EFFECT_STEP, prev)
            self.set_color(o)
            time.sleep(PULSE_DURATION/EFFECT_STEP)
        self.set_color(prev)

    def turn_off(self):
        self.set_color("000000")

    def set_brightness (self, b):
        self.set_color("ESCOLOR")

    def set_brightness_conf (self):
        self.set_color("ESCOLOR")

    def ret_brightness (self):
        return (batoconf("led.brightness") or "100", str(self.period))

####################
# Handhelds that use a direct RGB interface with each LED addressable
class rgbledaddr(object):
    def __init__(self):
        # Use glob to find all red, green, and blue channels for both left (l) and right (r)
        self.all_r = sorted(glob.glob('/sys/class/leds/[lr]:r?/brightness'))
        self.all_g = sorted(glob.glob('/sys/class/leds/[lr]:g?/brightness'))
        self.all_b = sorted(glob.glob('/sys/class/leds/[lr]:b?/brightness'))
        
        # Determine hardware max brightness (usually 255)
        self.max_val = self._get_hw_max()

    def _get_hw_max(self):
        test_paths = self.all_r + self.all_g + self.all_b
        if test_paths:
            try:
                max_path = test_paths[0].replace('brightness', 'max_brightness')
                with open(max_path, 'r') as f:
                    return int(f.readline().strip())
            except: pass
        return 255 

    def _get_factor(self):
        val = batoconf("led.brightness")
        if val is None: 
            return 1.0
        try:
            # Strictly treat as percentage (0 to 100)
            f_val = float(val)
            f_val = max(0, min(100, f_val)) # Clamp to 0-100 range
            return f_val / 100.0
        except:
            return 1.0

    def _write_scaled(self, r, g, b):
        factor = self._get_factor()
        
        # Math: (Color_Input / 255) * User_Brightness_Percent * Hardware_Max_Limit
        rs = str(int((r / 255.0) * factor * self.max_val))
        gs = str(int((g / 255.0) * factor * self.max_val))
        bs = str(int((b / 255.0) * factor * self.max_val))
        
        # Batch write to all color-specific sysfs paths
        for path in self.all_r:
            try:
                with open(path, 'w') as f: f.write(rs)
            except: pass
        for path in self.all_g:
            try:
                with open(path, 'w') as f: f.write(gs)
            except: pass
        for path in self.all_b:
            try:
                with open(path, 'w') as f: f.write(bs)
            except: pass

    def turn_off(self):
        self._write_scaled(0, 0, 0)

    def set_color(self, rgb):
        if rgb == "OFF":
            self.turn_off()
        elif rgb == "ESCOLOR":
            r, g, b = batoconf_color()
            self._write_scaled(int(r), int(g), int(b))
        elif rgb == "RAINBOW":
            self.rainbow_effect()
        elif rgb == "PULSE":
            self.pulse_effect()
        elif len(rgb) == 6:
            r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
            self._write_scaled(r, g, b)

    def set_color_dec(self, rgb_str):
        try:
            r, g, b = [int(x) for x in rgb_str.split()]
            self._write_scaled(r, g, b)
        except: pass

    def get_color(self):
        try:
            with open(self.all_r[0], 'r') as f: r = int(f.readline().strip())
            with open(self.all_g[0], 'r') as f: g = int(f.readline().strip())
            with open(self.all_b[0], 'r') as f: b = int(f.readline().strip())
            # Convert hardware-specific value back to standard 255-scale for the UI
            r_norm = int((r / self.max_val) * 255)
            g_norm = int((g / self.max_val) * 255)
            b_norm = int((b / self.max_val) * 255)
            return f"{dec_to_hex(r_norm)}{dec_to_hex(g_norm)}{dec_to_hex(b_norm)}"
        except: return "000000"

    def get_color_dec(self):
        try:
            with open(self.all_r[0], 'r') as f: r = f.readline().strip()
            with open(self.all_g[0], 'r') as f: g = f.readline().strip()
            with open(self.all_b[0], 'r') as f: b = f.readline().strip()
            return f"{r} {g} {b}"
        except: return "0 0 0"

    def rainbow_effect(self):
        for i in range(0, EFFECT_STEP):
            o_hex = getRainbowRGB(float(i/EFFECT_STEP))
            r, g, b = hex_to_dec(o_hex[0:2]), hex_to_dec(o_hex[2:4]), hex_to_dec(o_hex[4:6])
            self._write_scaled(r, g, b)
            time.sleep(EFFECT_DURATION/EFFECT_STEP)

    def pulse_effect(self):
        # Get the 'base' color from config to pulse against
        r_base, g_base, b_base = batoconf_color()
        for i in range(0, EFFECT_STEP):
            # Calculate pulse intensity
            if i < EFFECT_STEP/2:
                coeff = float(1 - 2*i/EFFECT_STEP)
            else:
                coeff = float((i - EFFECT_STEP/2) / (EFFECT_STEP/2))
            
            # Apply pulse coefficient AND brightness factor via _write_scaled
            self._write_scaled(int(int(r_base)*coeff), int(int(g_base)*coeff), int(int(b_base)*coeff))
            time.sleep(PULSE_DURATION/EFFECT_STEP)

    def set_brightness(self, b):
        self.set_color("ESCOLOR")

    def set_brightness_conf(self):
        self.set_color("ESCOLOR")

    def get_brightness(self):
        return (batoconf("led.brightness") or "100", str(self.max_val))

####################
# Unified class for Batocera handhelds
class led(object):
    def __new__(cls):
        m = batocera_model()
        if m == "pwm":
            return pwmled()
        elif m == "rgb":
            return rgbled()
        elif m == "rgbaddr":
            return rgbledaddr()
        elif m == "legiongos":
            return legiongosled()
        elif m == "legiongo":
            return legiongoled()
        elif m == "multiled":
            return multiled()
        elif m == "dual_multiled":
            return dual_multiled()
        elif m == "odin_mono":
            return odinmono()
        elif m == "cubexx":
            return cubexxled()
        elif m == "rg_vita_pro":
            return rgvitaproled()
        elif m == "r36ultra":
            return r36ultraled()
        else:
            print(m)

####################
# Helper functions and effects
def dec_to_hex(i):
    return f'{int(i):0>2X}'

def hex_to_dec(hx):
    return int('0x'+hx, 16)

def hex_to_pwm(hx, period):
    return int(float((int('0x'+hx, 16)/255)*period))

def pwm_to_hex(i, period):
    return f'{int(255*float(i)/period):0>2X}'

def dec_to_pwm(d, period):
    return int(float((int(d)/255)*period))

def pwm_to_dec(i, period):
    return f'{int(255*float(i)/period)}'

def getAngleDiff(a, b):
    return (a < b and a+360-b or a-b)

def getRainbowRGB(num):
    angle = num*360 # num = starting point between 0 and 1 (randomized)
    comp = []
    for i in range(0, 3):
        startAngle = ((i+1)*120)%360
        diffFromStart = getAngleDiff(angle, startAngle)
        if diffFromStart < 60:
            comp.append(int(diffFromStart/60*255))
        elif diffFromStart <= 180:
            comp.append(255)
        elif diffFromStart < 240:
            comp.append(int((240-diffFromStart)/60*255))
        else:
            comp.append(0)
    out = f'{comp[0]:0>2X}{comp[1]:0>2X}{comp[2]:0>2X}'
    return (out)

def getPulseRGB(num, step, rgb): # num = order from 0 to step
    r, g, b = hex_to_dec(rgb[0:2]), hex_to_dec(rgb[2:4]), hex_to_dec(rgb[4:6])
    if num < step/2:
        coeff = float(1-2*num/step)
    else:
        coeff = float((num-step/2)/(step/2))
    nr, ng, nb = int(coeff*float(r)), int(coeff*float(g)), int(coeff*float(b))
    out = f'{nr:0>2X}{ng:0>2X}{nb:0>2X}'
    return (out)

####################
# if invoked as a command line: respond with supported Model, or None
if __name__ == '__main__':
    print (batocera_model())
