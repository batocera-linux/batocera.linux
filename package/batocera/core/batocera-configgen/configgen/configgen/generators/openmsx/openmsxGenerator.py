#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
from distutils.dir_util import copy_tree

openMSX_Homedir = '/userdata/system/configs/openmsx'
openMSX_Config = '/usr/share/openmsx/'

class OpenmsxGenerator(Generator):

    def hasInternalMangoHUDCall(self):
        return True

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        share_dir = openMSX_Homedir + "/share"
        #settings_xml = share_dir + "/settings.xml"

        # Create Folder
        if not path.isdir(openMSX_Homedir):
            os.mkdir(openMSX_Homedir)

        # Copy File Needed
        if not os.path.exists(share_dir):
            os.mkdir(share_dir)
            copy_tree(openMSX_Config, share_dir)

        commandArray = ["/usr/bin/openmsx", "-cart", rom ]
        if system.isOptSet('hud') and system.config["hud"] != "":
               commandArray.insert(0, "mangohud")
        return Command.Command(array=commandArray)
