#!/usr/bin/env python
import sys
import Command
import batoceraFiles
from . import libretroConfig
from . import libretroRetroarchCustom
from . import libretroControllers
from generators.Generator import Generator
import os
import stat
import subprocess
from settings.unixSettings import UnixSettings
from utils.logger import get_logger
import utils.videoMode as videoMode
import shutil
import glob

eslog = get_logger(__name__)

class LibretroGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    # Main entry of the module
    # Configure retroarch and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Fix for the removed MESS/MAMEVirtual cores
        if system.config['core'] in [ 'mess', 'mamevirtual' ]:
            system.config['core'] = 'mame'

        # Get the graphics backend first
        gfxBackend = getGFXBackend(system)

        # Get the shader before writing the config, we may need to disable bezels based on the shader.
        renderConfig = system.renderconfig
        altDecoration = videoMode.getAltDecoration(system.name, rom, 'retroarch')
        gameShader = None
        shaderBezel = False
        if altDecoration == "0":
            if 'shader' in renderConfig:
                gameShader = renderConfig['shader']
        else:
            if ('shader-' + str(altDecoration)) in renderConfig:
                gameShader = renderConfig['shader-' + str(altDecoration)]
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
            # If the shader filename contains noBezel, activate Shader Bezel mode.
            if "noBezel" in video_shader:
                shaderBezel = True

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
                if system.config['core'] in [ 'mess', 'mamevirtual', 'same_cdi', 'mame078plus', 'mame0139' ]:
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

            libretroConfig.writeLibretroConfig(self, retroconfig, system, playersControllers, metadata, guns, wheels, rom, bezel, shaderBezel, gameResolution, gfxBackend)
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
            romDOSName, romExtension = os.path.splitext(romName)
            if (romExtension == '.dos' or romExtension == '.pc'):
                if os.path.exists(os.path.join(rom, romDOSName + ".bat")) and not " " in romDOSName:
                    exe = os.path.join(rom, romDOSName + ".bat")
                elif os.path.exists(os.path.join(rom, "dosbox.bat")) and not os.path.exists(os.path.join(rom, romDOSName + ".bat")):
                    exe = os.path.join(rom, "dosbox.bat")
                else:
                    exe = rom
                commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile'], exe]
                dontAppendROM = True
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
        # vitaquake2 - choose core based on directory
        elif system.name == 'vitaquake2':
            directory_path = os.path.dirname(rom)
            if "xatrix" in directory_path:
                system.config['core'] = "vitaquake2-xatrix"
            elif "rogue" in directory_path:
                system.config['core'] = "vitaquake2-rogue"
            elif "zaero" in directory_path:
                system.config['core'] = "vitaquake2-zaero"
            # set the updated core name
            retroarchCore = batoceraFiles.retroarchCores + system.config['core'] + "_libretro.so"
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
        # boom3
        elif system.name == 'boom3':
            with open(rom, 'r') as file:
                first_line = file.readline().strip()
            # extracting the directory path from the original 'rom' variable
            directory_path = '/'.join(rom.split('/')[:-1])
            # creating the new 'rom' variable by combining the directory path and the first line
            rom = f"{directory_path}/{first_line}"
            # choose core based on new rom directory
            directory_path = os.path.dirname(rom)
            if "d3xp" in directory_path:
                system.config['core'] = "boom3_xp"
            retroarchCore = batoceraFiles.retroarchCores + system.config['core'] + "_libretro.so"
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
        # super mario wars - verify assets from Content Downloader
        elif system.name == 'superbroswar':
            romdir = os.path.dirname(os.path.abspath(rom))
            assetdirs = [
                "music/world/Standard", "music/game/Standard/Special", "music/game/Standard/Menu", "filters", "worlds/KingdomHigh",
                "worlds/MrIsland", "worlds/Sky World", "worlds/Smb3", "worlds/Simple", "worlds/screenshots", "worlds/Flurry World",
                "worlds/MixedRiver", "worlds/Contest", "gfx/skins", "gfx/packs/Retro/fonts", "gfx/packs/Retro/modeobjects",
                "gfx/packs/Retro/eyecandy", "gfx/packs/Retro/awards", "gfx/packs/Retro/powerups", "gfx/packs/Retro/menu",
                "gfx/packs/Classic/projectiles", "gfx/packs/Classic/fonts", "gfx/packs/Classic/modeobjects", "gfx/packs/Classic/world",
                "gfx/packs/Classic/world/thumbnail", "gfx/packs/Classic/world/preview", "gfx/packs/Classic/modeskins",
                "gfx/packs/Classic/hazards", "gfx/packs/Classic/blocks", "gfx/packs/Classic/backgrounds", "gfx/packs/Classic/tilesets/SMB2",
                "gfx/packs/Classic/tilesets/Expanded", "gfx/packs/Classic/tilesets/SMB1", "gfx/packs/Classic/tilesets/Classic",
                "gfx/packs/Classic/tilesets/SMB3", "gfx/packs/Classic/tilesets/SuperMarioWorld", "gfx/packs/Classic/tilesets/YoshisIsland",
                "gfx/packs/Classic/eyecandy", "gfx/packs/Classic/awards", "gfx/packs/Classic/powerups", "gfx/packs/Classic/menu",
                "gfx/leveleditor", "gfx/docs", "sfx/packs/Classic", "sfx/announcer/Mario",
                "maps/tour", "maps/cache", "maps/screenshots", "maps/special", "tours",
            ]
            try:
                for assetdir in assetdirs:
                    os.chdir(f"{romdir}/{assetdir}")
                os.chdir(romdir)
            except FileNotFoundError:
                eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
                raise

            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]
        else:
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-L", retroarchCore, "--config", system.config['configfile']]

        configToAppend = []

        # Custom configs - per core
        customCfg = f"{batoceraFiles.retroarchRoot}/{system.name}.cfg"
        if os.path.isfile(customCfg):
            configToAppend.append(customCfg)

        # Custom configs - per game
        customGameCfg = f"{batoceraFiles.retroarchRoot}/{system.name}/{romName}.cfg"
        if os.path.isfile(customGameCfg):
            configToAppend.append(customGameCfg)

        # Overlay management
        overlayFile = f"{batoceraFiles.OVERLAYS}/{system.name}/{romName}.cfg"
        if os.path.isfile(overlayFile):
            configToAppend.append(overlayFile)

        # RetroArch 1.7.8 (Batocera 5.24) now requires the shaders to be passed as command line argument
        if 'shader' in renderConfig and gameShader != None:
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
            if 'netplay.server.session' in system.config:
                commandArray.extend(["--mitm-session", system.config['netplay.server.session']])
            if 'netplay.nickname' in system.config:
                commandArray.extend(["--nick", system.config['netplay.nickname']])

        # Verbose logs
        commandArray.extend(['--verbose'])

        if system.name == 'snes-msu1' or system.name == 'satellaview':
            if "squashfs" in rom:
                romsInDir = glob.glob(glob.escape(rom) + '/*.sfc') + glob.glob(glob.escape(rom) + '/*.smc')
                rom = romsInDir[0]

        if system.name == 'scummvm':
            rom = os.path.dirname(rom) + '/' + romName
            if os.stat(rom).st_size == 0:
                # File is empty, run game directly
                rom = rom[0:-8]
        
        if system.name == 'reminiscence':
            with open(rom, 'r') as file:
                first_line = file.readline().strip()
            directory_path = '/'.join(rom.split('/')[:-1])
            rom = f"{directory_path}/{first_line}"

        if system.name == 'openlara':
            with open(rom, 'r') as file:
                first_line = file.readline().strip()
            directory_path = '/'.join(rom.split('/')[:-1])
            rom = f"{directory_path}/{first_line}"

        # Use command line instead of ROM file for MAME variants
        if system.config['core'] in [ 'mame', 'mess', 'mamevirtual', 'same_cdi' ]:
            dontAppendROM = True
            if system.config['core'] in [ 'mame', 'mess', 'mamevirtual' ]:
                corePath = 'lr-' + system.config['core']
            else:
                corePath = system.config['core']
            commandArray.append(f'/var/run/cmdfiles/{os.path.splitext(os.path.basename(rom))[0]}.cmd')

        if dontAppendROM == False:
            commandArray.append(rom)

        if system.isOptSet('state_slot') and system.isOptSet('state_filename') and system.config['state_filename'][-5:] != ".auto":
            # if the file ends by .auto, this is the auto loading, else it is the states
            # retroarch need the file be named with .entry at the end to load the state
            # a link would work, but on fat32, we need to copy
            commandArray.extend(["-e", system.config['state_slot']])

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF})

def getGFXBackend(system):
        # Start with the selected option
        # Pick glcore or gl based on drivers if not selected
        if system.isOptSet("gfxbackend"):
            backend = system.config["gfxbackend"]
            setManually = True
        else:
            setManually = False
            # glvendor check first, to avoid a 2nd testing on intel boards
            if videoMode.getGLVendor() in ["nvidia", "amd"] and videoMode.getGLVersion() >= 3.1:
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
