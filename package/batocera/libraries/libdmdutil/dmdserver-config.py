#!/usr/bin/env python3

import argparse
import configparser
import os

parser = argparse.ArgumentParser(prog="dmdserver-config")
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

### Brightness ###
if args.zedmd_brightness is not None:
    if args.zedmd_brightness < 0:
        config.remove_option("ZeDMD", "Brightness")
    else:
        config.set("ZeDMD", "Brightness", str(args.zedmd_brightness))

### save ###
if not os.path.exists(os.path.dirname(args.config)):
    os.makedirs(os.path.dirname(args.config))
with open(args.config, 'w') as configfile:
        config.write(configfile)
