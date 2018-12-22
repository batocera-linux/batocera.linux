import os
from os import path
import Command
import recalboxFiles
import shutil
from generators.Generator import Generator
import os.path
import zipfile
from settings.unixSettings import UnixSettings
from generators.libretro import libretroControllers
from os.path import dirname

class AmiberryGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        retroconfig = UnixSettings(recalboxFiles.amiberryRetroarchCustom, separator=' ')
        if not os.path.exists(dirname(recalboxFiles.amiberryRetroarchCustom)):
            os.makedirs(dirname(recalboxFiles.amiberryRetroarchCustom))

        romIsWhd = self.isWhdFile(rom)
        commandArray = [ recalboxFiles.recalboxBins[system.config['emulator']], "-G" ]
        if not romIsWhd:
	    commandArray.append("-core=" + system.config['core'])

        # floppies
        n = 0
        for img in self.floppiesFromRom(rom):
            if n < 4:
                commandArray.append("-" + str(n))
                commandArray.append(img)
            n += 1

        # floppy path
        if romIsWhd:
            commandArray.append("-autowhdload="+rom)
        else:
	    commandArray.append("-s")
	    commandArray.append("pandora.floppy_path=/recalbox/share/roms/amiga/" + system.config['core'])

        # controller
        libretroControllers.writeControllersConfig(retroconfig, system, playersControllers)

        if not os.path.exists(recalboxFiles.amiberryRetroarchInputsDir):
            os.makedirs(recalboxFiles.amiberryRetroarchInputsDir)
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            replacements = {'_player' + str(nplayer) + '_':'_'}
            playerInputFilename = recalboxFiles.amiberryRetroarchInputsDir + "/" + pad.realName + ".cfg"
            with open(recalboxFiles.amiberryRetroarchCustom) as infile, open(playerInputFilename, 'w') as outfile:
	        for line in infile:
                    for src, target in replacements.iteritems():
		        newline = line.replace(src, target)
		        if not newline.isspace():
		            outfile.write(newline)
            nplayer += 1

        # fps
	if system.config['showFPS'] == 'true':
            commandArray.append("-s")
            commandArray.append("show_leds=true")
        
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

    def isWhdFile(self, filepath):
        # whd have zip extention
        extension = os.path.splitext(filepath)[1][1:]

        # valid extensions are lha and zip
        if extension == "lha":
            return True

        if extension != "zip":
            return False
        # whd have a file .info on top of the archive
        with zipfile.ZipFile(filepath) as zip:
            for zipfilename in zip.namelist():
                if zipfilename.find('/') == -1: # at the root
                    extension = os.path.splitext(zipfilename)[1][1:]
                    if extension == "info":
                        return True
        # no info file found
        return False
