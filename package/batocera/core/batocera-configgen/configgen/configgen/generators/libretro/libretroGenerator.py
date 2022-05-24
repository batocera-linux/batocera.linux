#!/usr/bin/env python
import sys
import Command
import batoceraFiles
from . import libretroConfig
from . import libretroRetroarchCustom
from . import libretroControllers
import shutil
from generators.Generator import Generator
import os
import stat
import subprocess
from settings.unixSettings import UnixSettings
from utils.logger import get_logger
import utils.videoMode as videoMode
import shutil

eslog = get_logger(__name__)

class LibretroGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    # Main entry of the module
    # Configure retroarch and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Settings batocera default config file if no user defined one
        if not 'configfile' in system.config:
            # Using batocera config file
            system.config['configfile'] = batoceraFiles.retroarchCustom
            # Create retroarchcustom.cfg if does not exists
            if not os.path.isfile(batoceraFiles.retroarchCustom):
                libretroRetroarchCustom.generateRetroarchCustom()
            #  Write controllers configuration files
            retroconfig = UnixSettings(batoceraFiles.retroarchCustom, separator=' ')

            if system.isOptSet('lightgun_map'):
                lightgun = system.getOptBoolean('lightgun_map')
            else:
                # Lightgun button mapping breaks lr-mame's inputs, disable if left on auto
                if system.config['core'] in [ 'mame', 'mess', 'mamevirtual' ]:
                    lightgun = False
                else:
                    lightgun = True
            libretroControllers.writeControllersConfig(retroconfig, system, playersControllers, lightgun)
            # force pathes
            libretroRetroarchCustom.generateRetroarchCustomPathes(retroconfig)
            # Write configuration to retroarchcustom.cfg
            if 'bezel' not in system.config or system.config['bezel'] == '':
                bezel = None
            else:
                bezel = system.config['bezel']
            # some systems (ie gw) won't bezels
            if system.isOptSet('forceNoBezel') and system.getOptBoolean('forceNoBezel'):
                bezel = None

            # Get the graphics backend prior to writing the config
            gfxBackend = getGFXBackend(system)

            libretroConfig.writeLibretroConfig(retroconfig, system, playersControllers, rom, bezel, gameResolution, gfxBackend)
            retroconfig.write()

            # duplicate config to mapping files while ra now split in 2 parts
            remapconfigDir = batoceraFiles.retroarchRoot + "/config/remaps/common"
            if not os.path.exists(remapconfigDir):
                os.makedirs(remapconfigDir)
            shutil.copyfile(batoceraFiles.retroarchCustom, remapconfigDir + "/common.rmp")

        # Retroarch core on the filesystem
        retroarchCore = batoceraFiles.retroarchCores + system.config['core'] + "_libretro.so"

        # for each core, a file /usr/lib/<core>.info must exit, otherwise, info such as rewinding/netplay will not work
        # to do a global check : cd /usr/lib/libretro && for i in *.so; do INF=$(echo $i | sed -e s+/usr/lib/libretro+/usr/share/libretro/info+ -e s+\.so+.info+); test -e "$INF" || echo $i; done
        infoFile = "/usr/share/libretro/info/"  + system.config['core'] + "_libretro.info"
        if not os.path.exists(infoFile):
            raise Exception("missing file " + infoFile)

        romName = os.path.basename(rom)


        # The command to run
        dontAppendROM = False
        # For the NeoGeo CD (lr-fbneo) it is necessary to add the parameter: --subsystem neocd
        if system.name == 'neogeocd' and system.config['core'] == "fbneo":
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--subsystem", "neocd", "--config", system.config['configfile']]
        # Set up GB/GBC Link games to use 2 different ROMs if needed
        if system.name == 'gb2players' or system.name == 'gbc2players':
            GBMultiROM = list()
            GBMultiFN = list()
            GBMultiSys = list()
            romGBName, romExtension = os.path.splitext(romName)
            # If ROM file is a .gb2 text, retrieve the filenames
            if romExtension.lower() in ['.gb2', '.gbc2']:
                with open(rom) as fp:
                    for line in fp:
                        GBMultiText = line.strip()
                        if GBMultiText.lower().startswith("gb:"):
                            GBMultiROM.append("/userdata/roms/gb/" + GBMultiText.split(":")[1])
                            GBMultiFN.append(GBMultiText.split(":")[1])
                            GBMultiSys.append("gb")
                        elif GBMultiText.lower().startswith("gbc:"):
                            GBMultiROM.append("/userdata/roms/gbc/" + GBMultiText.split(":")[1])
                            GBMultiFN.append(GBMultiText.split(":")[1])
                            GBMultiSys.append("gbc")
                        else:
                            GBMultiROM.append("/userdata/roms/" + system.name + "/" + GBMultiText)
                            GBMultiFN.append(GBMultiText.split(":")[1])
                            if system.name == "gb2players":
                                GBMultiSys.append("gb")
                            else:
                                GBMultiSys.append("gbc")
            else:
                # Otherwise fill in the list with the single game
                GBMultiROM.append(rom)
                GBMultiFN.append(romName)
                if system.name == "gb2players":
                    GBMultiSys.append("gb")
                else:
                    GBMultiSys.append("gbc")
            # If there are at least 2 games in the list, use the alternate command line
            if len(GBMultiROM) >= 2:
                commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, GBMultiROM[0], "--subsystem", "gb_link_2p", GBMultiROM[1], "--config", system.config['configfile']]
                dontAppendROM = True
            else:
                commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
            # Handling for the save copy
            if (system.isOptSet('sync_saves') and system.config["sync_saves"] == '1'):
                if len(GBMultiROM) >= 2:
                    GBMultiSave = [os.path.splitext(GBMultiFN[0])[0] + ".srm", os.path.splitext(GBMultiFN[1])[0] + ".srm"]
                else:
                    GBMultiSave = [os.path.splitext(GBMultiFN[0])[0] + ".srm"]
                # Verifies all the save paths exist
                # Prevents copy errors if they don't
                if not os.path.exists("/userdata/saves/gb"):
                    os.mkdir("/userdata/saves/gb")
                if not os.path.exists("/userdata/saves/gbc"):
                    os.mkdir("/userdata/saves/gbc")
                if not os.path.exists("/userdata/saves/gb2players"):
                    os.mkdir("/userdata/saves/gb2players")
                if not os.path.exists("/userdata/saves/gbc2players"):
                    os.mkdir("/userdata/saves/gbc2players")
                # Copies the saves if they exist
                for x in range(len(GBMultiSave)):
                    saveFile = "/userdata/saves/" + GBMultiSys[x] + "/" + GBMultiSave[x]
                    newSaveFile = "/userdata/saves/" + system.name + "/" + GBMultiSave[x]
                    if os.path.exists(saveFile):
                        shutil.copy(saveFile, newSaveFile)
                # Generates a script to copy the saves back on exit
                # Starts by making sure script paths exist
                if not os.path.exists("/userdata/system/scripts/"):
                    os.mkdir("/userdata/system/scripts")
                if not os.path.exists("/userdata/system/scripts/gb2savesync/"):
                    os.mkdir("/userdata/system/scripts/gb2savesync")
                scriptFile = "/userdata/system/scripts/gb2savesync/exitsync.sh"
                if os.path.exists(scriptFile):
                    os.remove(scriptFile)
                GBMultiScript = open(scriptFile, "w")
                GBMultiScript.write("#!/bin/bash\n")
                GBMultiScript.write("#This script is created by the Game Boy link cable system to sync save files.\n")
                GBMultiScript.write("#\n")
                GBMultiScript.write("\n")
                GBMultiScript.write("case $1 in\n")
                GBMultiScript.write("   gameStop)\n")
                # The only event is gameStop, checks to make sure it was called by the right system
                GBMultiScript.write("       if [ $2 = 'gb2players' ] || [ $2 = 'gbc2players' ]\n")
                GBMultiScript.write("       then\n")
                for x in range(len(GBMultiSave)):
                    saveFile = "/userdata/saves/" + GBMultiSys[x] + "/" + GBMultiSave[x]
                    newSaveFile = "/userdata/saves/" + system.name + "/" + GBMultiSave[x]
                    GBMultiScript.write('           cp "' + newSaveFile + '" "' + saveFile + '"\n')
                GBMultiScript.write("       fi\n")
                # Deletes itself after running
                GBMultiScript.write("       rm " + scriptFile + "\n")
                GBMultiScript.write("   ;;\n")
                GBMultiScript.write("esac\n")
                GBMultiScript.close()
                # Make it executable
                fileStat = os.stat(scriptFile)
                os.chmod(scriptFile, fileStat.st_mode | 0o111)
        # PURE zip games uses the same commandarray of all cores. .pc and .rom  uses owns
        elif system.name == 'dos':
            romDOSName = os.path.splitext(romName)[0]
            romDOSName, romExtension = os.path.splitext(romName)
            if romExtension == '.dos' or romExtension == '.pc':
                commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile'], os.path.join(rom, romDOSName + ".bat")]
            else:
                commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
        # Pico-8 multi-carts (might work only with official Lexaloffe engine right now)
        elif system.name == 'pico8':
            romext = os.path.splitext(romName)[1]
            if (romext.lower() == ".m3u"):
                with open (rom, "r") as fpin:
                    lines = fpin.readlines()
                rom = os.path.dirname(os.path.abspath(rom)) + '/' + lines[0].strip()
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
        else:
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]


        configToAppend = []


        # Custom configs - per core
        customCfg = "{}/{}.cfg".format(batoceraFiles.retroarchRoot, system.name)
        if os.path.isfile(customCfg):
            configToAppend.append(customCfg)

        # Custom configs - per game
        customGameCfg = "{}/{}/{}.cfg".format(batoceraFiles.retroarchRoot, system.name, romName)
        if os.path.isfile(customGameCfg):
            configToAppend.append(customGameCfg)

        # Overlay management
        overlayFile = "{}/{}/{}.cfg".format(batoceraFiles.OVERLAYS, system.name, romName)
        if os.path.isfile(overlayFile):
            configToAppend.append(overlayFile)

        # RetroArch 1.7.8 (Batocera 5.24) now requires the shaders to be passed as command line argument
        renderConfig = system.renderconfig
        gameSpecial = videoMode.getGameSpecial(system.name, rom, True)
        gameShader = None
        if gameSpecial == "0":
            if 'shader' in renderConfig:
                gameShader = renderConfig['shader']
        else:
            if ('shader-' + str(gameSpecial)) in renderConfig:
                gameShader = renderConfig['shader-' + str(gameSpecial)]
            else:
                gameShader = renderConfig['shader']
        if 'shader' in renderConfig and gameShader != None:
            if (gfxBackend == 'glcore' or gfxBackend == 'vulkan') or (system.config['core'] in libretroConfig.coreForceSlangShaders):
                shaderFilename = gameShader + ".slangp"
            else:
                shaderFilename = gameShader + ".glslp"
            eslog.debug("searching shader {}".format(shaderFilename))
            if os.path.exists("/userdata/shaders/" + shaderFilename):
                video_shader_dir = "/userdata/shaders"
                eslog.debug("shader {} found in /userdata/shaders".format(shaderFilename))
            else:
                video_shader_dir = "/usr/share/batocera/shaders"
            video_shader = video_shader_dir + "/" + shaderFilename
            commandArray.extend(["--set-shader", video_shader])

        # Generate the append
        if configToAppend:
            commandArray.extend(["--appendconfig", "|".join(configToAppend)])

        # Netplay mode
        if 'netplay.mode' in system.config:
            if system.config['netplay.mode'] == 'host':
                commandArray.append("--host")
            elif system.config['netplay.mode'] == 'client' or system.config['netplay.mode'] == 'spectator':
                commandArray.extend(["--connect", system.config['netplay.server.ip']])
            if 'netplay.server.port' in system.config:
                commandArray.extend(["--port", system.config['netplay.server.port']])
            if 'netplay.nickname' in system.config:
                commandArray.extend(["--nick", system.config['netplay.nickname']])

        # Verbose logs
        commandArray.extend(['--verbose'])

        # Extension used by hypseus .daphne but lr-daphne starts with .zip
        if system.name == 'daphne':
            romName = os.path.splitext(os.path.basename(rom))[0]
            rom = batoceraFiles.daphneDatadir + '/roms/' + romName +'.zip'

        if system.name == 'scummvm':
            rom = os.path.dirname(rom) + '/' + romName[0:-8]
        
        # Use command line instead of ROM file for MAME variants
        if system.config['core'] in [ 'mame', 'mess', 'mamevirtual' ]:
            dontAppendROM = True
            commandArray.append("/var/run/lr-mame.cmd")

        if dontAppendROM == False:
            commandArray.append(rom)
            
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF})

def getGFXBackend(system):
        # Start with the selected option
        # Pick glcore or gl based on drivers if not selected
        if system.isOptSet("gfxbackend"):
            backend = system.config["gfxbackend"]
            setManually = True
        else:
            setManually = False
            if videoMode.getGLVersion() >= 3.1 and videoMode.getGLVendor() in ["nvidia", "amd"]:
                backend = "glcore"
            else:
                backend = "gl"

        # Retroarch has flipped between using opengl or gl, correct the setting here if needed.
        if backend == "opengl":
            backend = "gl"

        # Don't change based on core if manually selected.
        if not setManually:
            # If set to glcore or gl, override setting for certain cores that require one or the other
            core = system.config['core']
            if backend == "gl" and core in [ 'kronos', 'citra', 'mupen64plus-next', 'melonds', 'beetle-psx-hw' ]:
                backend = "glcore"
            if backend == "glcore" and core in [ 'parallel_n64', 'yabasanshiro', 'openlara', 'boom3' ]:
                backend = "gl"

        return backend
