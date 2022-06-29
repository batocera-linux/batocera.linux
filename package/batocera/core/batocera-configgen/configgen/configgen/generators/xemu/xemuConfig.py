#!/usr/bin/env python

import sys
import os
import io
import batoceraFiles
import settings
from Emulator import Emulator
import configparser

def writeIniFile(system, rom, playersControllers):
    iniConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    iniConfig.optionxform = str
    if os.path.exists(batoceraFiles.xemuConfig):
        try:
            with io.open(batoceraFiles.xemuConfig, 'r', encoding='utf_8_sig') as fp:
                iniConfig.readfp(fp)
        except:
            pass

    createXemuConfig(iniConfig, system, rom, playersControllers)
    # save the ini file
    if not os.path.exists(os.path.dirname(batoceraFiles.xemuConfig)):
        os.makedirs(os.path.dirname(batoceraFiles.xemuConfig))
    with open(batoceraFiles.xemuConfig, 'w') as configfile:
        iniConfig.write(configfile)

def createXemuConfig(iniConfig, system, rom, playersControllers):
    # Create INI sections
    if not iniConfig.has_section("system"):
        iniConfig.add_section("system")
    if not iniConfig.has_section("audio"):
        iniConfig.add_section("audio")
    if not iniConfig.has_section("display"):
        iniConfig.add_section("display")
    if not iniConfig.has_section("input"):
        iniConfig.add_section("input")
    if not iniConfig.has_section("network"):
        iniConfig.add_section("network")
    if not iniConfig.has_section("misc"):
        iniConfig.add_section("misc")

    # Fill system section
    iniConfig.set("system", "flash_path", "/userdata/bios/Complex_4627.bin")
    iniConfig.set("system", "bootrom_path", "/userdata/bios/mcpx_1.0.bin")
    iniConfig.set("system", "hdd_path", "/userdata/saves/xbox/xbox_hdd.qcow2")
    iniConfig.set("system", "eeprom_path", "/userdata/saves/xbox/xemu_eeprom.bin")
    iniConfig.set("system", "dvd_path", rom)
    iniConfig.set("system", "memory", "64")

    # Boot Animation Skip
    if system.isOptSet("xemu_bootanim"):
        iniConfig.set("system", "shortanim", system.config["xemu_bootanim"])
    else:
        iniConfig.set("system", "shortanim", "false")

    # Fill audio section
    iniConfig.set("audio", "use_dsp", "false")

    # Fill display section
    if system.isOptSet("scaling"):
        iniConfig.set("display", "scale", system.config["scaling"])
    else:
        iniConfig.set("display", "scale", "scale") #4:3

    if system.isOptSet("render"):
        iniConfig.set("display", "render_scale", system.config["render"])
    else:
        iniConfig.set("display", "render_scale", "1") #render scale by default
        iniConfig.set("display", "ui_scale", "1")

    # Fill input section
    # first, clear
    for i in range(1,5):
        iniConfig.set("input", f"controller_{i}_guid", "")
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer <= 4:
            iniConfig.set("input", f"controller_{nplayer}_guid", pad.guid)
        nplayer = nplayer + 1

    # Determine the current default network connection
    currentDefaultNetwork = defaultNetworkInterface()

    if currentDefaultNetwork:
        # Fill network section
        iniConfig.set("network", "enabled", "true")
        iniConfig.set("network", "backend", "pcap")
        iniConfig.set("network", "local_addr", "0.0.0.0:9368")
        iniConfig.set("network", "remote_addr", "1.2.3.4:9368")
        iniConfig.set("network", "pcap_iface", currentDefaultNetwork)
    else:
        iniConfig.set("network", "enabled", "false")
        iniConfig.set("network", "backend", "user")
        iniConfig.set("network", "local_addr", "0.0.0.0:9368")
        iniConfig.set("network", "remote_addr", "1.2.3.4:9368")

    # Fill misc section
    iniConfig.set("misc", "user_token", "")

def defaultNetworkInterface():
    # This function returns the name of the first interface that routes to the "default" destination. If there is no such interface, return None instead.

    n = 0
    # Open the route network information.
    with open("/proc/net/route") as f:
        for line in f:
            n += 1
            # Check to make sure we are skipping over the first line (as it is just the header).
            if n > 1:
                words = line.split("\t")
                # If the "Destination" of the route is the default "00000000":
                if words[1] == "00000000":
                    # Return the name of that "Iface" and immediately exit this function:
                    return words[0]
    # Otherwise, this loop repeats for all the remaining routes. If none are found, return None.
    return None