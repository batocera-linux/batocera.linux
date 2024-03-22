#!/usr/bin/env python3

import argparse
import configparser
import os

parser = argparse.ArgumentParser(prog="dmdserver-config")
parser.add_argument("--matrix",               help="matrix color")
parser.add_argument("--brightness", type=int, help="matrix color")
parser.add_argument("--config", default="/userdata/system/configs/dmdserver/config.ini", help="config file")
args = parser.parse_args()

config = configparser.ConfigParser(interpolation=None)
# To prevent ConfigParser from converting to lower case
config.optionxform = str

if os.path.isfile(args.config):
    config.read(args.config)

if not config.has_section("Pixelcade"):
    config.add_section("Pixelcade")

if not config.has_section("ZeDMD"):
    config.add_section("ZeDMD")
    
### MATRIX ###
if args.matrix is not None:
    if args.matrix == "auto":
        config.remove_option("Pixelcade", "Matrix")
        config.remove_option("ZeDMD",     "RGBOrder")
    elif args.matrix == "rgb":
        config.set("Pixelcade", "Matrix",   "0")
        config.set("ZeDMD",     "RGBOrder", "0") # to be fixed, maybe SaveSettings should be applied
    elif args.matrix == "rbg":
        config.set("Pixelcade", "Matrix",   "1")
        config.set("ZeDMD",     "RGBOrder", "1") # to be fixed, maybe SaveSettings should be applied

### Brightness ###
if args.brightness is not None:
    if args.brightness == -1:
        config.remove_option("ZeDMD", "Brightness")
    else:
        config.set("ZeDMD", "Brightness", str(int(args.brightness/6.66))) # zedmd brightness is from 0 to 15

### save ###
with open(args.config, 'w') as configfile:
        config.write(configfile)
