#!/usr/bin/env python

import sys
import os
import io
import batoceraFiles
import settings
from Emulator import Emulator
import configparser

def writeIniFile(system, rom, playersControllers):
    tomlConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    tomlConfig.optionxform = str
    if os.path.exists(batoceraFiles.xemuConfig):
        try:
            with io.open(batoceraFiles.xemuConfig, 'r', encoding='utf_8_sig') as fp:
                tomlConfig.readfp(fp)
        except:
            pass

    createXemuConfig(tomlConfig, system, rom, playersControllers)
    # save the ini file
    if not os.path.exists(os.path.dirname(batoceraFiles.xemuConfig)):
        os.makedirs(os.path.dirname(batoceraFiles.xemuConfig))
    with open(batoceraFiles.xemuConfig, 'w') as configfile:
        tomlConfig.write(configfile)

def createXemuConfig(tomlConfig, system, rom, playersControllers):
    # Create INI sections
    if not tomlConfig.has_section("general"):
        tomlConfig.add_section("general")
    if not tomlConfig.has_section("general.updates"):
        tomlConfig.add_section("general.updates")
    if not tomlConfig.has_section("sys"):
        tomlConfig.add_section("sys")
    if not tomlConfig.has_section("sys.files"):
        tomlConfig.add_section("sys.files")
    if not tomlConfig.has_section("audio"):
        tomlConfig.add_section("audio")
    if not tomlConfig.has_section("display.window"):
        tomlConfig.add_section("display.window")
    if not tomlConfig.has_section("display.ui"):
        tomlConfig.add_section("display.ui")
    if not tomlConfig.has_section("input"):
        tomlConfig.add_section("input")
    if not tomlConfig.has_section("net"):
        tomlConfig.add_section("net")
    if not tomlConfig.has_section("misc"):
        tomlConfig.add_section("misc")

    # Fill system section
    tomlConfig.set("sys", "mem_limit", "'64'")
    tomlConfig.set("sys.files", "flashrom_path", "'/userdata/bios/Complex_4627.bin'")
    tomlConfig.set("sys.files", "bootrom_path", "'/userdata/bios/mcpx_1.0.bin'")
    tomlConfig.set("sys.files", "hdd_path", "'/userdata/saves/xbox/xbox_hdd.qcow2'")
    tomlConfig.set("sys.files", "eeprom_path", "'/userdata/saves/xbox/xemu_eeprom.bin'")
    tomlConfig.set("sys.files", "dvd_path", rom)

    # Boot Animation Skip
    if system.isOptSet("xemu_bootanim"):
        tomlConfig.set("sys.files", "shortanim", system.config["xemu_bootanim"])
    else:
        tomlConfig.set("sys.files", "shortanim", "false")

    # Fill audio section
    tomlConfig.set("audio", "use_dsp", "false")

    # Fill display section
    if system.isOptSet("scaling"):
        tomlConfig.set("display.window", "scale", system.config["scaling"])
    else:
        tomlConfig.set("display.window", "scale", "scale") #4:3

    if system.isOptSet("render"):
        tomlConfig.set("display.window", "render_scale", system.config["render"])
    else:
        tomlConfig.set("display.window", "render_scale", "1") #render scale by default
        tomlConfig.set("display.window", "ui_scale", "1")

    # Fill input section
    # first, clear
    for i in range(1,5):
        tomlConfig.set("input", "controller_{}_guid".format(i), "")
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer <= 4:
            tomlConfig.set("input", "controller_{}_guid".format(nplayer), pad.guid)
        nplayer = nplayer + 1

    # Fill network section
    tomlConfig.set("net", "enabled", "false")
    tomlConfig.set("net", "backend", "user")
    tomlConfig.set("net", "local_addr", "0.0.0.0:9368")
    tomlConfig.set("net", "remote_addr", "1.2.3.4:9368")

    # Fill misc section
    tomlConfig.set("misc", "user_token", "")

    # Set screenshot folder
    tomlConfig.set("general", "show_welcome", "false")
    tomlConfig.set("general", "screenshot_dir", "'/userdata/screenshots'")

    # Disable check update
    tomlConfig.set("general.updates", "check", "false")
