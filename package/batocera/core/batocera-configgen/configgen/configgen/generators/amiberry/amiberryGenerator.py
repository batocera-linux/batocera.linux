import Command
from generators.Generator import Generator
import recalboxFiles
import os
from os import path

class AmiberryGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = [ recalboxFiles.recalboxBins[system.config['emulator']], "-G", "-core=" + system.config['core'] ]

        # floppies
        n = 0
        for img in self.floppiesFromRom(rom):
            if n < 4:
                commandArray.append("-" + str(n))
                commandArray.append(img)
            n += 1

        # floppy path
        commandArray.append("-s")
        commandArray.append("pandora.floppy_path=/recalbox/share/roms/amiga/" + system.config['core'])

        # controller
        n = 1
        for controller in playersControllers:
            if n == 1:
                commandArray.append("-s")
                commandArray.append("joyport1=joy" + playersControllers[controller].dev[-1:]) # not perfect
                commandArray.append("-s")
                commandArray.append("joyportname1=JOY" + playersControllers[controller].dev[-1:]) # not perfect

                # hotkey
                if "start" in playersControllers[controller].inputs and playersControllers[controller].inputs["hotkey"].type == 'button':
                    commandArray.append("-s")
                    commandArray.append("button_for_hotkey=" + playersControllers[controller].inputs["hotkey"].id)

                # menu
                if "start" in playersControllers[controller].inputs and playersControllers[controller].inputs["start"].type == 'button':
                    commandArray.append("-s")
                    commandArray.append("button_for_menu=" + playersControllers[controller].inputs["b"].id)

                # quit
                if "hotkey" in playersControllers[controller].inputs and playersControllers[controller].inputs["hotkey"].type == 'button':
                    commandArray.append("-s")
                    commandArray.append("button_for_quit=" + playersControllers[controller].inputs["start"].id)

            n = n+1

        # fps
	if system.config['showFPS'] == 'true':
            commandArray.append("-s")
            commandArray.append("show_leds=true")
        
        if 'args' in system.config and system.config['args'] is not None:
            commandArray.extend(system.config['args'])
        os.chdir("/usr/share/amiberry")
        return Command.Command(array=commandArray)

    # from one file (x1.zip), get the list of all existing files with the same extension + last char (as number) suffix
    # for example, "/path/toto0.zip" becomes ["/path/toto0.zip", "/path/toto1.zip", "/path/toto2.zip"]
    def floppiesFromRom(self, rom):
        floppies = []

        # split path and extension
        filepath, fileext = path.splitext(rom)

        # if the last char is not a digit, only 1 file
        if not filepath[-1:].isdigit():
            floppies.append(rom)
            return floppies

        # path without the number
        fileprefix=filepath[:-1]

        # special case for 0 while numerotation can start at 1
        n = 0
        if path.isfile(fileprefix + str(n) + fileext):
            floppies.append(fileprefix + str(n) + fileext)

        # adding all other files
        n = 1
        while path.isfile(fileprefix + str(n) + fileext):
            floppies.append(fileprefix + str(n) + fileext)
            n += 1

        return floppies
