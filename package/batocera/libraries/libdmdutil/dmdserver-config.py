#!/usr/bin/env python3

import argparse
import configparser
import os

parser = argparse.ArgumentParser(prog="dmdserver-config")
parser.add_argument("--zedmd-matrix",               help="matrix color")
parser.add_argument("--zedmd-brightness", type=int, help="brightness")
parser.add_argument("--config", default="/userdata/system/configs/dmdserver/config.ini", help="config file")
args = parser.parse_args()

config = configparser.ConfigParser(interpolation=None)
# To prevent ConfigParser from converting to lower case
config.optionxform = str

if os.path.isfile(args.config):
    config.read(args.config)

if not config.has_section("DMDServer"):
    config.add_section("DMDServer")

if not config.has_section("ZeDMD"):
    config.add_section("ZeDMD")

## global
config.set("DMDServer", "AltColor", "1") # jsm174: AltColor should be 1 for everyone

### MATRIX ###
zedmd_before_rgborder   = None
zedmd_before_brightness = None
if config.has_option("ZeDMD", "RGBOrder"):
    zedmd_before_rgborder   = config.get("ZeDMD", "RGBOrder")
if config.has_option("ZeDMD", "Brightness"):
    zedmd_before_brightness = config.get("ZeDMD", "Brightness")

if args.zedmd_matrix is not None:
    if args.zedmd_matrix == "auto":
        config.remove_option("ZeDMD", "RGBOrder")
    elif args.zedmd_matrix == "rgb":
        config.set("ZeDMD",     "RGBOrder", "0")
    elif args.zedmd_matrix == "brg":
        config.set("ZeDMD",     "RGBOrder", "1")
    elif args.zedmd_matrix == "gbr":
        config.set("ZeDMD",     "RGBOrder", "2")
    elif args.zedmd_matrix == "rbg":
        config.set("ZeDMD",     "RGBOrder", "3")
    elif args.zedmd_matrix == "grb":
        config.set("ZeDMD",     "RGBOrder", "4")
    elif args.zedmd_matrix == "bgr":
        config.set("ZeDMD",     "RGBOrder", "5")

### Brightness ###
if args.zedmd_brightness is not None:
    if args.zedmd_brightness < 0:
        config.remove_option("ZeDMD", "Brightness")
    else:
        config.set("ZeDMD", "Brightness", str(args.zedmd_brightness))

### zedmd as a special flag to save config for the next reboot ###
# we do it only if something changes. this is not perfect, but i've no better way
zedmd_after_rgborder   = None
zedmd_after_brightness = None
if config.has_option("ZeDMD", "RGBOrder"):
    zedmd_after_rgborder   = config.get("ZeDMD", "RGBOrder")
if config.has_option("ZeDMD", "Brightness"):
    zedmd_after_brightness = config.get("ZeDMD", "Brightness")

if zedmd_before_rgborder != zedmd_after_rgborder or zedmd_before_brightness != zedmd_after_brightness:
    config.set("ZeDMD", "SaveSettings", "1")
else:
    config.set("ZeDMD", "SaveSettings", "0")

### save ###
if not os.path.exists(os.path.dirname(args.config)):
    os.makedirs(os.path.dirname(args.config))
with open(args.config, 'w') as configfile:
        config.write(configfile)
