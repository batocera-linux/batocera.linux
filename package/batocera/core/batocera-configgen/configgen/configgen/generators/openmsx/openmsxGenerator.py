#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from distutils.dir_util import copy_tree
import xml.etree.ElementTree as ET
import shutil
import xml.dom.minidom as minidom
import re
import zipfile
from utils.logger import get_logger

eslog = get_logger(__name__)

openMSX_Homedir = '/userdata/system/configs/openmsx'
openMSX_Config = '/usr/share/openmsx/'

class OpenmsxGenerator(Generator):

    def hasInternalMangoHUDCall(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        share_dir = openMSX_Homedir + "/share"
        source_settings = openMSX_Config + "/settings.xml" 
        settings_xml = share_dir + "/settings.xml"
        settings_tcl = share_dir + "/script.tcl"

        # create folder if needed
        if not os.path.isdir(openMSX_Homedir):
            os.mkdir(openMSX_Homedir)
        
        # screenshot folder
        if not os.path.isdir("/userdata/screenshots/openmsx"):
            os.mkdir("/userdata/screenshots/openmsx")

        # copy files if needed
        if not os.path.exists(share_dir):
            os.mkdir(share_dir)
            copy_tree(openMSX_Config, share_dir)
        
        # always use our settings.xml file as a base
        shutil.copy2(source_settings, share_dir)

        # Adjust settings.xml as needed
        tree = ET.parse(settings_xml)
        root = tree.getroot()
        
        settings_elem = root.find("settings")
        if system.isOptSet("openmsx_loading"):
            fullspeed_elem = ET.Element("setting", {"id": "fullspeedwhenloading"})
            fullspeed_elem.text = system.config["openmsx_loading"]
        else:
            fullspeed_elem = ET.Element("setting", {"id": "fullspeedwhenloading"})
            fullspeed_elem.text = "true"
        
        settings_elem.append(fullspeed_elem)
        
        # Create the bindings element
        bindings_elem = ET.Element("bindings")
        new_bind = ET.Element("bind", {"key": "keyb F6"})
        new_bind.text = "cycle videosource"
        bindings_elem.append(new_bind)
        
        # Add the bindings element to the root element
        root.append(bindings_elem)
        
        # Write the updated xml to the file
        with open(settings_xml, "w") as f:
            f.write("<!DOCTYPE settings SYSTEM 'settings.dtd'>\n")
            # purdify the XML
            xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            formatted_xml = "\n".join([line for line in xml_string.split("\n") if line.strip()])
            f.write(formatted_xml)
              
        # setup the blank tcl file
        with open(settings_tcl, "w") as file:
            file.write("")
        
        # set the tcl file options - we can add other options later
        with open(settings_tcl, "a") as file:
            file.write("filepool add -path /userdata/bios/Machines -types system_rom -position 1\n")
            file.write("filepool add -path /userdata/bios/openmsx -types system_rom -position 2\n")
            # get the rom name (no extension) for the savestate name
            save_name = os.path.basename(rom)
            save_name = os.path.splitext(save_name)[0]
            # simplify the rom name, remove content between brackets () & []
            save_name = re.sub(r"\([^)]*\)", "", save_name)
            save_name = re.sub(r"\[[^]]*\]", "", save_name)
            file.write("\n")
            file.write("# -= Save state =-\n")
            file.write('savestate "{}"\n'.format(save_name))
            # set the screenshot
            file.write("\n")
            file.write("# -= Screenshots =-\n")
            file.write('bind F5 {screenshot [utils::get_next_numbered_filename /userdata/screenshots/openmsx "[guess_title] " ".png"]}\n')
            # setup the controller
            file.write("\n")
            file.write("# -= Controller config =-\n")
            nplayer = 1
            for playercontroller, pad in sorted(playersControllers.items()):
                if nplayer <= 2:
                    if nplayer == 1:
                        file.write("plug joyporta joystick1\n")
                    if nplayer == 2:
                        file.write("plug joyportb joystick2\n")
                    for x in pad.inputs:
                        input = pad.inputs[x]
                        if input.name == "y":
                            file.write('bind "joy{} button{} down" "keymatrixdown 6 0x40"\n'.format(nplayer, input.id))
                        if input.name == "x":
                            file.write('bind "joy{} button{} down" "keymatrixdown 6 0x80"\n'.format(nplayer, input.id))
                        if input.name == "pagedown":
                            file.write('bind "joy{} button{} up" "set fastforward off"\n'.format(nplayer, input.id))
                            file.write('bind "joy{} button{} down" "set fastforward on"\n'.format(nplayer, input.id))
                        if input.name == "select":
                            file.write('bind "joy{} button{} down" "toggle pause"\n'.format(nplayer, input.id))
                        if input.name == "start":
                            file.write('bind "joy{} button{} down" "main_menu_toggle"\n'.format(nplayer, input.id))
                        if input.name == "l3":
                            file.write('bind "joy{} button{} down" "toggle_osd_keyboard"\n'.format(nplayer, input.id))
                        if input.name == "r3":
                            file.write('bind "joy{} button{} down" "toggle console"\n'.format(nplayer, input.id))
                nplayer += 1
        
        # now run the rom with the appropriate flags
        file_extension = os.path.splitext(rom)[1].lower()
        commandArray = ["/usr/bin/openmsx", "-cart", rom, "-script", settings_tcl]

        # set the best machine based on the system
        if system.name in ["msx1", "msx2"]:
            commandArray[1:1] = ["-machine", "Boosted_MSX2_EN"]

        if system.name == "msx2+":
            commandArray[1:1] = ["-machine", "Boosted_MSX2+_JP"]

        if system.name == "msxturbor":
            commandArray[1:1] = ["-machine", "Boosted_MSXturboR_with_IDE"]

        if system.name == "colecovision":
            commandArray[1:1] = ["-machine", "ColecoVision_SGM"]
        
        if system.name == "spectravideo":
            commandArray[1:1] = ["-machine", "Spectravideo_SVI-328"]
        
        if system.isOptSet("hud") and system.config["hud"] != "":
            commandArray.insert(0, "mangohud")
        
        # setup the media types
        if file_extension == ".zip":
            with zipfile.ZipFile(rom, "r") as zip_file:
                for zip_info in zip_file.infolist():
                    file_extension = os.path.splitext(zip_info.filename)[1]
                    # usually zip files only contain 1 file however break loop if file extension found
                    if file_extension in [".cas", ".dsk", ".ogv"]:
                        eslog.debug(f"Zip file contains: {file_extension}")
                        break
        
        if file_extension == ".ogv":
            eslog.debug("File is a laserdisc")
            for i in range(len(commandArray)):
                if commandArray[i] == "-machine":
                    commandArray[i+1] = "Pioneer_PX-7"
                elif commandArray[i] == "-cart":
                    commandArray[i] = "-laserdisc"
        
        if file_extension == ".cas":
            eslog.debug("File is a cassette")
            for i in range(len(commandArray)):
                if commandArray[i] == "-cart":
                    commandArray[i] = "-cassetteplayer"
        
        if file_extension == ".dsk":
            eslog.debug("File is a disk")
            disk_type = "-diska"
            if system.isOptSet("openmsx_disk") and system.config["openmsx_disk"] == "hda":
                disk_type = "-hda"
            for i in range(len(commandArray)):
                if commandArray[i] == "-cart":
                    commandArray[i] = disk_type
        
        # handle our own file format for stacked roms / disks
        if file_extension == ".openmsx":
            # read the contents of the file and extract the rom paths
            with open(rom, "r") as file:
                lines = file.readlines()
                rom1 = ""
                rom1 = lines[0].strip()
                rom2 = ""
                rom2 = lines[1].strip()
            # get the directory path of the .openmsx file
            openmsx_dir = os.path.dirname(rom)
            # prepend the directory path to the .rom/.dsk file paths
            rom1 = os.path.join(openmsx_dir, rom1)
            rom2 = os.path.join(openmsx_dir, rom2)
            # get the first lines extension
            extension = rom1.split(".")[-1].lower()
            # now start ammending the array
            if extension == "rom":
                cart_index = commandArray.index("-cart")
                commandArray[cart_index] = "-carta"
                commandArray[cart_index +1] = rom1
            elif extension == "dsk":
                cart_index = commandArray.index("-cart")
                commandArray[cart_index] = "-diska"
                commandArray[cart_index +1] = rom1
            if extension == "rom" or extension == "dsk":
                rom2_index = cart_index + 2
                commandArray.insert(rom2_index, "-cartb" if extension == "rom" else "-diskb")
                commandArray.insert(rom2_index + 1, rom2)

        return Command.Command(
            array=commandArray,
            env={"XDG_DATA_HOME": share_dir}
        )
