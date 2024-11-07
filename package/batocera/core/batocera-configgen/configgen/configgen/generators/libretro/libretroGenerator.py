from __future__ import annotations

import itertools
import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import (
    BATOCERA_SHADERS,
    BIOS,
    CONFIGS,
    HOME,
    OVERLAYS,
    ROMS,
    SAVES,
    USER_SHADERS,
    mkdir_if_not_exists,
)
from ...settings.unixSettings import UnixSettings
from ...utils import videoMode as videoMode
from ..Generator import Generator
from . import libretroConfig, libretroControllers, libretroRetroarchCustom
from .libretroPaths import (
    RETROARCH_BIN,
    RETROARCH_CONFIG,
    RETROARCH_CORES,
    RETROARCH_CUSTOM,
    RETROARCH_SHARE,
)

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

class LibretroGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        # f12 for coin : set in libretroMameConfig.py, others in libretroControllers.py
        return {
            "name": "retroarch",
            "keys": { "exit": ["KEY_LEFTSHIFT", "KEY_ESC"], "menu": ["KEY_LEFTSHIFT", "KEY_F1"], "pause": ["KEY_LEFTSHIFT", "KEY_F1"], "coin": "KEY_F12",
                      "save_state": ["KEY_LEFTSHIFT", "KEY_F3"], "restore_state": ["KEY_LEFTSHIFT", "KEY_F4"], "next_slot": ["KEY_LEFTSHIFT", "KEY_F6"], "previous_slot": ["KEY_LEFTSHIFT", "KEY_F5"]
                     }
        }

    # Main entry of the module
    # Configure retroarch and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        # Fix for the removed MESS/MAMEVirtual cores
        if system.config['core'] in [ 'mess', 'mamevirtual' ]:
            system.config['core'] = 'mame'

        # Get the graphics backend first
        gfxBackend = getGFXBackend(system)

        # Get the shader before writing the config, we may need to disable bezels based on the shader.
        renderConfig = system.renderconfig
        altDecoration = videoMode.getAltDecoration(system.name, rom_path, 'retroarch')
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
                shaderFilename = f"{gameShader}.slangp"
            else:
                shaderFilename = f"{gameShader}.glslp"
            eslog.debug(f"searching shader {shaderFilename}")
            if (USER_SHADERS / shaderFilename).exists():
                video_shader_dir = USER_SHADERS
                eslog.debug(f"shader {shaderFilename} found in {USER_SHADERS}")
            else:
                video_shader_dir = BATOCERA_SHADERS
            video_shader = video_shader_dir / shaderFilename
            # If the shader filename contains noBezel, activate Shader Bezel mode.
            if "noBezel" in video_shader.name:
                shaderBezel = True

        # Settings batocera default config file if no user defined one
        if not 'configfile' in system.config:
            # Using batocera config file
            system.config['configfile'] = str(RETROARCH_CUSTOM)
            # Create retroarchcustom.cfg if does not exists
            if not RETROARCH_CUSTOM.is_file():
                libretroRetroarchCustom.generateRetroarchCustom()
            #  Write controllers configuration files
            retroconfig = UnixSettings(RETROARCH_CUSTOM, separator=' ')

            if system.isOptSet('lightgun_map'):
                lightgun = system.getOptBoolean('lightgun_map')
            else:
                # Lightgun button mapping breaks lr-mame's inputs, disable if left on auto
                if system.config['core'] in [ 'mess', 'mamevirtual', 'same_cdi', 'mame078plus' ]:
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

            libretroConfig.writeLibretroConfig(self, retroconfig, system, playersControllers, metadata, guns, wheels, rom_path, bezel, shaderBezel, gameResolution, gfxBackend)
            retroconfig.write()

            # duplicate config to mapping files while ra now split in 2 parts
            remapconfigDir = RETROARCH_CONFIG / "config" / "remaps" / "common"
            mkdir_if_not_exists(remapconfigDir)
            shutil.copyfile(RETROARCH_CUSTOM, remapconfigDir / "common.rmp")

        # Retroarch core on the filesystem
        retroarchCore = RETROARCH_CORES / f"{system.config['core']}_libretro.so"

        # for each core, a file /usr/lib/<core>.info must exit, otherwise, info such as rewinding/netplay will not work
        # to do a global check : cd /usr/lib/libretro && for i in *.so; do INF=$(echo $i | sed -e s+/usr/lib/libretro+/usr/share/libretro/info+ -e s+\.so+.info+); test -e "$INF" || echo $i; done
        infoFile = RETROARCH_SHARE / "info" / f"{system.config['core']}_libretro.info"
        if not infoFile.exists():
            raise Exception(f"missing file {infoFile}")

        # The command to run
        dontAppendROM = False
        # For the NeoGeo CD (lr-fbneo) it is necessary to add the parameter: --subsystem neocd
        if system.name == 'neogeocd' and system.config['core'] == "fbneo":
            commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--subsystem", "neocd", "--config", system.config['configfile']]
        # Set up GB/GBC Link games to use 2 different ROMs if needed
        if system.name == 'gb2players' or system.name == 'gbc2players':
            GBMultiROM: list[Path] = []
            GBMultiFN: list[str] = []
            GBMultiSys: list[str] = []
            # If ROM file is a .gb2 text, retrieve the filenames
            if rom_path.suffix.lower() in ['.gb2', '.gbc2']:
                with rom_path.open() as fp:
                    for line in fp:
                        GBMultiText = line.strip()
                        if GBMultiText.lower().startswith("gb:"):
                            GBMultiROM.append(ROMS / "gb" / GBMultiText.split(":")[1])
                            GBMultiFN.append(GBMultiText.split(":")[1])
                            GBMultiSys.append("gb")
                        elif GBMultiText.lower().startswith("gbc:"):
                            GBMultiROM.append(ROMS / "gbc" / GBMultiText.split(":")[1])
                            GBMultiFN.append(GBMultiText.split(":")[1])
                            GBMultiSys.append("gbc")
                        else:
                            GBMultiROM.append(ROMS / system.name / GBMultiText)
                            GBMultiFN.append(GBMultiText.split(":")[1])
                            if system.name == "gb2players":
                                GBMultiSys.append("gb")
                            else:
                                GBMultiSys.append("gbc")
            else:
                # Otherwise fill in the list with the single game
                GBMultiROM.append(rom_path)
                GBMultiFN.append(rom_path.name)
                if system.name == "gb2players":
                    GBMultiSys.append("gb")
                else:
                    GBMultiSys.append("gbc")
            # If there are at least 2 games in the list, use the alternate command line
            if len(GBMultiROM) >= 2:
                commandArray = [RETROARCH_BIN, "-L", retroarchCore, GBMultiROM[0], "--subsystem", "gb_link_2p", GBMultiROM[1], "--config", system.config['configfile']]
                dontAppendROM = True
            else:
                commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]
            # Handling for the save copy
            if (system.isOptSet('sync_saves') and system.config["sync_saves"] == '1'):
                if len(GBMultiROM) >= 2:
                    GBMultiSave = [GBMultiROM[0].stem + ".srm", GBMultiROM[1].stem + ".srm"]
                else:
                    GBMultiSave = [GBMultiROM[0].stem + ".srm"]
                # Verifies all the save paths exist
                # Prevents copy errors if they don't
                mkdir_if_not_exists(SAVES / "gb")
                mkdir_if_not_exists(SAVES / "gbc")
                mkdir_if_not_exists(SAVES / "gb2players")
                mkdir_if_not_exists(SAVES / "gbc2players")
                # Copies the saves if they exist
                for x in range(len(GBMultiSave)):
                    saveFile = SAVES / GBMultiSys[x] / GBMultiSave[x]
                    newSaveFile = SAVES / system.name / GBMultiSave[x]
                    if saveFile.exists():
                        shutil.copy(saveFile, newSaveFile)
                # Generates a script to copy the saves back on exit
                # Starts by making sure script paths exist
                mkdir_if_not_exists(HOME / "scripts" / "gb2savesync")
                scriptFile = HOME / "scripts" / "gb2savesync" / "exitsync.sh"
                if scriptFile.exists():
                    scriptFile.unlink()
                GBMultiScript = scriptFile.open("w")
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
                GBMultiScript.write(f"       rm {scriptFile}\n")
                GBMultiScript.write("   ;;\n")
                GBMultiScript.write("esac\n")
                GBMultiScript.close()
                # Make it executable
                scriptFile.chmod(scriptFile.stat().st_mode | 0o111)
        # PURE zip games uses the same commandarray of all cores. .pc and .rom  uses owns
        elif system.name == 'dos':
            if (rom_path.suffix == '.dos' or rom_path.suffix == '.pc'):
                if (rom_path / f"{rom_path.stem}.bat").exists() and " " not in rom_path.stem:
                    exe = rom_path / f"{rom_path.stem}.bat"
                elif (rom_path / "dosbox.bat").exists() and not (rom_path / f"{rom_path.stem}.bat").exists():
                    exe = rom_path / "dosbox.bat"
                else:
                    exe = rom_path
                commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile'], exe]
                dontAppendROM = True
            else:
                commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]
        # Pico-8 multi-carts (might work only with official Lexaloffe engine right now)
        elif system.name == 'pico8':
            if (rom_path.suffix.lower() == ".m3u"):
                with rom_path.open("r") as fpin:
                    lines = fpin.readlines()
                rom_path = rom_path.absolute().parent / lines[0].strip()
            commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]
        # vitaquake2 - choose core based on directory
        elif system.name == 'vitaquake2':
            directory_parts = rom_path.parent.parts
            if "xatrix" in directory_parts:
                system.config['core'] = "vitaquake2-xatrix"
            elif "rogue" in directory_parts:
                system.config['core'] = "vitaquake2-rogue"
            elif "zaero" in directory_parts:
                system.config['core'] = "vitaquake2-zaero"
            # set the updated core name
            retroarchCore = RETROARCH_CORES / f"{system.config['core']}_libretro.so"
            commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]
        # doom3
        elif system.name == 'doom3':
            with rom_path.open('r') as file:
                first_line = file.readline().strip()
            # creating the new 'rom_path' variable by combining the directory path and the first line
            rom_path = rom_path.parent / first_line
            eslog.debug(f"New rom path: {rom_path}")
            # choose core based on new rom directory
            directory_parts = rom_path.parent.parts
            if "d3xp" in directory_parts:
                system.config['core'] = "boom3_xp"
            retroarchCore = RETROARCH_CORES / f"{system.config['core']}_libretro.so"
            commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]
        # super mario wars - verify assets from Content Downloader
        elif system.name == 'superbroswar':
            romdir = rom_path.absolute().parent
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
                    os.chdir(romdir / assetdir)
                os.chdir(romdir)
            except FileNotFoundError:
                eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
                raise

            commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]
        else:
            commandArray = [RETROARCH_BIN, "-L", retroarchCore, "--config", system.config['configfile']]

        configToAppend: list[Path] = []

        # Custom configs - per core
        customCfg = RETROARCH_CONFIG / f"{system.name}.cfg"
        if customCfg.is_file():
            configToAppend.append(customCfg)

        # Custom configs - per game
        customGameCfg = RETROARCH_CONFIG / system.name / f"{rom_path.name}.cfg"
        if customGameCfg.is_file():
            configToAppend.append(customGameCfg)

        # Overlay management
        overlayFile = OVERLAYS / system.name / f"{rom_path.name}.cfg"
        if overlayFile.is_file():
            configToAppend.append(overlayFile)

        # RetroArch 1.7.8 (Batocera 5.24) now requires the shaders to be passed as command line argument
        if 'shader' in renderConfig and gameShader != None:
            commandArray.extend(["--set-shader", video_shader])

        # Generate the append
        if configToAppend:
            commandArray.extend(["--appendconfig", "|".join(str(config) for config in configToAppend)])

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
            if "squashfs" in str(rom_path) and rom_path.is_dir():
                rom_path = next(itertools.chain(rom_path.glob('*.sfc'), rom_path.glob('*.smc')))
        elif system.name == 'msu-md':
            if "squashfs" in str(rom_path) and rom_path.is_dir():
                rom_path = next(rom_path.glob('*.md'))

        if system.name == 'scummvm':
            rom_path = rom_path.parent / rom_path.name
            if rom_path.stat().st_size == 0:
                # File is empty, run game directly
                rom_path = rom_path.with_suffix('')

        if system.name == 'reminiscence':
            with rom_path.open() as file:
                first_line = file.readline().strip()
            rom_path = rom_path.parent / first_line

        if system.name == 'openlara':
            with rom_path.open() as file:
                first_line = file.readline().strip()
            rom_path = rom_path.parent / first_line

        # Use command line instead of ROM file for MAME variants
        if system.config['core'] in [ 'mame', 'mess', 'mamevirtual', 'same_cdi' ]:
            dontAppendROM = True
            if system.config['core'] in [ 'mame', 'mess', 'mamevirtual' ]:
                corePath = 'lr-' + system.config['core']
            else:
                corePath = system.config['core']
            commandArray.append(f'/var/run/cmdfiles/{rom_path.stem}.cmd')

        if system.config['core'] == 'hatarib':
            biosdir = BIOS / "hatarib"
            if not biosdir.exists():
                biosdir.mkdir()
            targetlink = biosdir / "hdd"
            #retroarch can't use hdd files outside his system directory (/userdata/bios)
            if targetlink.exists():
                targetlink.unlink()
            if rom_path.suffix.lower() in ['.hd', '.gemdos']:
                #don't pass hd drive as parameter, it need to be added in configuration
                dontAppendROM = True
                targetlink.symlink_to(rom_path)

        if dontAppendROM == False:
            commandArray.append(rom_path)

        if system.isOptSet('state_slot') and system.isOptSet('state_filename') and system.config['state_filename'][-5:] != ".auto":
            # if the file ends by .auto, this is the auto loading, else it is the states
            # retroarch need the file be named with .entry at the end to load the state
            # a link would work, but on fat32, we need to copy
            commandArray.extend(["-e", system.config['state_slot']])

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":CONFIGS})

def getGFXBackend(system: Emulator) -> str:
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
