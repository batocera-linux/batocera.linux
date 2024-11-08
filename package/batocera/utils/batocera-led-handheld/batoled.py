#!/usr/bin/env python3
"""
PWM + RGB unified LED driver 
Written for Batocera - @lbrpdx
"""
import os
import time
import glob

DEBUG = 0            # set to 1 for debugging
EFFECT_STEP = 60     # how many colors in the effect
EFFECT_DURATION = 2  # how many seconds
PULSE_DURATION  = 1  # how many seconds
BATOCONFFILE = '/userdata/system/batocera.conf'
DEFAULT_ES_COLOR = '255 0 165'

####################
# Is your handheld supported by this library?
def batocera_model():
    l = '/sys/class/leds/multicolor:chassis/multi_intensity' 
    if os.path.exists(l):
        return("rgb")
    c = glob.glob('/sys/class/pwm/pwmchip*/device/name')
    for t in c:
        with open (t) as f:
            m = f.readline().strip()
            if m == 'htr3212-pwm':
                return("pwm")
    return("Unsupported")


####################
# Get a value from batocera.conf
def batoconf(key):
    with open(BATOCONFFILE) as f:
        for line in f:
            if not line.startswith(key+"="):
                continue
            rest = line.split("=", 1)[1]
            nocomment = rest.split("#", 1)[0].strip()
            return(nocomment) # First one is enough
    return None


####################
# Handhelds that use a direct RGB interface (easy peasy)
class rgbled(object):
    def __init__(self):
        self.bpath           = '/sys/class/leds/multicolor:chassis/'
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
            rgb = batoconf("led.colour")
            if rgb == None:
                out = DEFAULT_ES_COLOR
            else:
                [ r, g, b ] = rgb.split(" ")
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
        b = batoconf("led.brightness")
        if b == None:
            b = 128
        self.set_brightness(b)

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
            rgb = batoconf("led.colour")
            if rgb == None:
                rgb = DEFAULT_ES_COLOR
            [ r, g, b ] = rgb.split(" ")
            r, g, b = str(dec_to_pwm(r, self.period)), str(dec_to_pwm(g, self.period)), str(dec_to_pwm(b, self.period))
        else:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
            r, g, b = str(hex_to_pwm(r, self.period)), str(hex_to_pwm(g, self.period)), str(hex_to_pwm(b, self.period))
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
        int_list = [int(x) for x in string.split(rgb)]
        if len(int_list) != 3:
            print (f'Argument expects three ints for R G B, not {rgb}')
            return (1)
        for n in int_list:
           if n < 0:
              n = 0
           if n > 255:
              n = 255
        r, g, b = str(dec_to_pwm(int_list[0], self.period)), str(dec_to_pwm(int_list[1], self.period)), str(dec_to_pwm(int_list[2], self.period))
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
        return          # unable to set it at the moment

    def set_brightness_conf (self):
        return

    def ret_brightness (self):
        return (-1, -1) # current brightness, max_brightness

####################
# Unified class for Batocera handhelds
class led(object):
    def __new__(cls):
        m = batocera_model()
        if m == "pwm":
            return pwmled()
        elif m == "rgb":
            return rgbled()
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
