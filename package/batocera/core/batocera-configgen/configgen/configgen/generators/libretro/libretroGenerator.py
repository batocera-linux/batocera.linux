#!/usr/bin/env python
import Command
import libretroControllers
import recalboxFiles
import libretroConfig
import shutil
from generators.Generator import Generator
import os.path
from settings.unixSettings import UnixSettings

class LibretroGenerator(Generator):

    # Main entry of the module
    # Configure retroarch and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Settings recalbox default config file if no user defined one
        if not 'configfile' in system.config:
            # Using recalbox config file
            system.config['configfile'] = recalboxFiles.retroarchCustom
            # Create retroarchcustom.cfg if does not exists
            if not os.path.isfile(recalboxFiles.retroarchCustom):
                shutil.copyfile(recalboxFiles.retroarchCustomOrigin, recalboxFiles.retroarchCustom)
            #  Write controllers configuration files
            retroconfig = UnixSettings(recalboxFiles.retroarchCustom, separator=' ')
            libretroControllers.writeControllersConfig(retroconfig, system, playersControllers)
            # Write configuration to retroarchcustom.cfg
            if 'bezel' not in system.config or system.config['bezel'] == '':
                bezel = None
            else:
                bezel = system.config['bezel']
            libretroConfig.writeLibretroConfig(retroconfig, system, playersControllers, rom, bezel, gameResolution)

        # Retroarch core on the filesystem
        retroarchCore = recalboxFiles.retroarchCores + system.config['core'] + recalboxFiles.libretroExt
        romName = os.path.basename(rom)

        # the command to run
        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
        configToAppend = []
        
        # Custom configs - per core
        customCfg = "{}/{}.cfg".format(recalboxFiles.retroarchRoot, system.name)
        if os.path.isfile(customCfg):
            configToAppend.append(customCfg)
        
        # Custom configs - per game
        customGameCfg = "{}/{}/{}.cfg".format(recalboxFiles.retroarchRoot, system.name, romName)
        if os.path.isfile(customGameCfg):
            configToAppend.append(customGameCfg)
        
        # Overlay management
        overlayFile = "{}/{}/{}.cfg".format(recalboxFiles.OVERLAYS, system.name, romName)
        if os.path.isfile(overlayFile):
            configToAppend.append(overlayFile)
        
        # Generate the append
        if configToAppend:
            commandArray.extend(["--appendconfig", "|".join(configToAppend)])
            
         # Netplay mode
        if 'netplaymode' in system.config:
            if system.config['netplaymode'] == 'host':
                commandArray.append("--host")
            elif system.config['netplaymode'] == 'client':
                commandArray.extend(["--connect", system.config['netplay.server.address']])

        commandArray.append(rom)
        return Command.Command(array=commandArray)
