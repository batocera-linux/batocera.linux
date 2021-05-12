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
    iniConfig.set("system", "shortanim", "false")

    # Fill audio section
    iniConfig.set("audio", "use_dsp", "false")

    # Fill display section
    if system.isOptSet("scaling"):
        iniConfig.set("display", "scale", system.config["scaling"])
    else:
        iniConfig.set("display", "scale", "scale") #4:3
    iniConfig.set("display", "ui_scale", "1")

    # Fill input section
    # first, clear
    for i in range(1,5):
        iniConfig.set("input", "controller_{}_guid".format(i), "")
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer <= 4:
            iniConfig.set("input", "controller_{}_guid".format(nplayer), pad.guid)
        nplayer = nplayer + 1

    # Fill network section
    iniConfig.set("network", "enabled", "false")
    iniConfig.set("network", "backend", "user")
    iniConfig.set("network", "local_addr", "0.0.0.0:9368")
    iniConfig.set("network", "remote_addr", "1.2.3.4:9368")

    # Fill misc section
    iniConfig.set("misc", "user_token", "")
