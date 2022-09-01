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
    if not iniConfig.has_section("general"):
        iniConfig.add_section("general")
    if not iniConfig.has_section("sys.files"):
        iniConfig.add_section("sys.files")
    if not iniConfig.has_section("audio"):
        iniConfig.add_section("audio")
    if not iniConfig.has_section("display.quality"):
        iniConfig.add_section("display.quality")
    if not iniConfig.has_section("display.ui"):
        iniConfig.add_section("display.ui")
    if not iniConfig.has_section("input"):
        iniConfig.add_section("input")
    if not iniConfig.has_section("net"):
        iniConfig.add_section("net")
    if not iniConfig.has_section("misc"):
        iniConfig.add_section("misc")

    # Boot Animation Skip
    if system.isOptSet("xemu_bootanim"):
        iniConfig.set("general", "skip_boot_anim", system.config["xemu_bootanim"])
    else:
        iniConfig.set("general", "skip_boot_anim", "false")

    # Disable welcome screen on first launch
    iniConfig.set("general", "show_welcome", "false")

    # Fill system section
    iniConfig.set("sys.files", "flashrom_path", '"/userdata/bios/Complex_4627.bin"')
    iniConfig.set("sys.files", "bootrom_path", '"/userdata/bios/mcpx_1.0.bin"')
    iniConfig.set("sys.files", "hdd_path", '"/userdata/saves/xbox/xbox_hdd.qcow2"')
    iniConfig.set("sys.files", "eeprom_path", '"/userdata/saves/xbox/xemu_eeprom.bin"')
    iniConfig.set("sys.files", "dvd_path", '"' + rom + '"')

    # Audio quality
    if system.isOptSet("use_dsp"):
        iniConfig.set("audio", "use_dsp", system.config["use_dsp"])
    else:
        iniConfig.set("audio", "use_dsp", "false")

    # Rendering resolution
    if system.isOptSet("render"):
        iniConfig.set("display.quality", "surface_scale", system.config["render"])
    else:
        iniConfig.set("display.quality", "surface_scale", "1") #render scale by default

    # Aspect ratio
    if system.isOptSet("scaling"):
        iniConfig.set("display.ui", "fit", '"' + system.config["scaling"] + '"')
    else:
        iniConfig.set("display.ui", "fit", '"scale"') #4:3

    # Fill input section
    # first, clear
    for i in range(1,5):
        iniConfig.remove_option("input", f"controller_{i}_guid")
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer <= 4:
            iniConfig.set("input", f"controller_{nplayer}_guid", '"' + pad.guid + '"')
        nplayer = nplayer + 1

    # Determine the current default network connection
    #currentDefaultNetwork = defaultNetworkInterface()

    #if currentDefaultNetwork:
        ## Fill network section
        #iniConfig.set("network", "enabled", "true")
        #iniConfig.set("network", "backend", "pcap")
        #iniConfig.set("network", "local_addr", "0.0.0.0:9368")
        #iniConfig.set("network", "remote_addr", "1.2.3.4:9368")
        #iniConfig.set("network", "pcap_iface", currentDefaultNetwork)
    #else:
        #iniConfig.set("network", "enabled", "false")
        #iniConfig.set("network", "backend", "user")
        #iniConfig.set("network", "local_addr", "0.0.0.0:9368")
        #iniConfig.set("network", "remote_addr", "1.2.3.4:9368")

    # Fill misc section
    #iniConfig.set("misc", "user_token", "")

#def defaultNetworkInterface():
    ## This function returns the name of the first interface that routes to the "default" destination. If there is no such interface, return None instead.

    #n = 0
    ## Open the route network information.
    #with open("/proc/net/route") as f:
        #for line in f:
            #n += 1
            ## Check to make sure we are skipping over the first line (as it is just the header).
            #if n > 1:
                #words = line.split("\t")
                ## If the "Destination" of the route is the default "00000000":
                #if words[1] == "00000000":
                    ## Return the name of that "Iface" and immediately exit this function:
                    #return words[0]
    ## Otherwise, this loop repeats for all the remaining routes. If none are found, return None.
    #return None
