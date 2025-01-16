from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...settings.unixSettings import UnixSettings
from ..Generator import Generator
from ..libretro import libretroControllers

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

_CONFIG_DIR: Final = CONFIGS / 'amiberry'
_CONFIG: Final = _CONFIG_DIR / 'conf' / 'amiberry.conf'
_RETROARCH_CUSTOM: Final = _CONFIG_DIR / 'conf' / 'retroarch' / 'overlay.cfg'
_RETROARCH_INPUTS_DIR: Final = _CONFIG_DIR / 'conf' / 'retroarch' / 'inputs'

class AmiberryGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "amiberry",
            "keys": { "exit": "KEY_F10" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(_RETROARCH_CUSTOM.parent)

        retroconfig = UnixSettings(_RETROARCH_CUSTOM, separator=' ')
        amiberryconf = UnixSettings(_CONFIG, separator=' ')
        amiberryconf.save('default_quit_key', 'F10')
        amiberryconf.save('saveimage_dir', '/userdata/saves/amiga/')
        amiberryconf.save('savestate_dir', '/userdata/saves/amiga/')
        amiberryconf.save('screenshot_dir', '/userdata/screenshots/')
        amiberryconf.save('rom_path', '/userdata/bios/amiga/')
        amiberryconf.save('whdboot_path', '/usr/share/amiberry/whdboot/')
        amiberryconf.save('logfile_path', '/userdata/system/logs/amiberry.log')
        amiberryconf.save('controllers_path', '/userdata/system/configs/amiberry/conf/retroarch/inputs/')
        amiberryconf.save('retroarch_config', _RETROARCH_CUSTOM)
        amiberryconf.save('default_vkbd_enabled', 'yes')
        amiberryconf.save('default_vkbd_hires', 'yes') # TODO: make an option in ES
        amiberryconf.save('default_vkbd_transparency', '60') # TODO: make an option in ES
        amiberryconf.save('default_vkbd_toggle', 'leftstick')
        amiberryconf.write()

        romType = self.getRomType(rom)
        eslog.debug("romType: "+romType)
        if romType != 'UNKNOWN' :
            commandArray: list[str | Path] = [ "/usr/bin/amiberry", "-G" ]
            if romType != 'WHDL' :
                commandArray.append("--model")
                commandArray.append(system.config['core'])

            if romType == 'WHDL' :
                commandArray.append("--autoload")
                commandArray.append(rom)
            elif romType == 'HDF' :
                commandArray.append("-s")
                commandArray.append("hardfile2=rw,DH0:"+rom+",32,1,2,512,0,,uae0")
                commandArray.append("-s")
                commandArray.append("uaehf0=hdf,rw,DH0:"+rom+",32,1,2,512,0,,uae0")
            elif romType == 'CD' :
                commandArray.append("--cdimage")
                commandArray.append(rom)
            elif romType == 'DISK':
                # floppies
                n = 0
                for img in self.floppiesFromRom(rom):
                    if n < 4:
                        commandArray.append("-" + str(n))
                        commandArray.append(img)
                    n += 1
                # floppy path
                commandArray.append("-s")
                # Use disk folder as floppy path
                romPathIndex = rom.rfind('/')
                commandArray.append("amiberry.floppy_path="+rom[0:romPathIndex])

            # controller
            libretroControllers.writeControllersConfig(retroconfig, system, playersControllers, True)
            retroconfig.write()

            mkdir_if_not_exists(_RETROARCH_INPUTS_DIR)

            nplayer = 1
            for playercontroller, pad in sorted(playersControllers.items()):
                replacements = {'_player' + str(nplayer) + '_':'_'}
                # amiberry remove / included in pads names like "USB Downlo01.80 PS3/USB Corded Gamepad"
                padfilename = pad.real_name.replace("/", "")
                playerInputFilename = _RETROARCH_INPUTS_DIR / f"{padfilename}.cfg"
                with _RETROARCH_CUSTOM.open() as infile, playerInputFilename.open('w') as outfile:
                    for line in infile:
                        for src, target in replacements.items():
                            newline = line.replace(src, target)
                            if not newline.isspace():
                                outfile.write(newline)
                if nplayer == 1: # 1 = joystick port
                    commandArray.append("-s")
                    commandArray.append("joyport1_friendlyname=" + padfilename)
                    if romType == 'CD' :
                        commandArray.append("-s")
                        commandArray.append("joyport1_mode=cd32joy")
                if nplayer == 2: # 0 = mouse for the player 2
                    commandArray.append("-s")
                    commandArray.append("joyport0_friendlyname=" + padfilename)
                nplayer += 1

            # fps
            if system.config['showFPS'] == 'true':
                commandArray.append("-s")
                commandArray.append("show_leds=true")

            # disable port 2 (otherwise, the joystick goes on it)
            commandArray.append("-s")
            commandArray.append("joyport2=")

            # remove interlace artifacts
            if system.isOptSet("amiberry_flickerfixer") and system.config['amiberry_flickerfixer'] == 'true':
                commandArray.append("-s")
                commandArray.append("gfx_flickerfixer=true")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_flickerfixer=false")

            # auto height
            if system.isOptSet("amiberry_auto_height") and system.config['amiberry_auto_height'] == 'true':
                commandArray.append("-s")
                commandArray.append("amiberry.gfx_auto_height=true")
            else:
                commandArray.append("-s")
                commandArray.append("amiberry.gfx_auto_height=false")

            # line mode
            if system.isOptSet("amiberry_linemode"):
                if system.config['amiberry_linemode'] == 'none':
                    commandArray.append("-s")
                    commandArray.append("gfx_linemode=none")
                elif system.config['amiberry_linemode'] == 'scanlines':
                    commandArray.append("-s")
                    commandArray.append("gfx_linemode=scanlines")
                elif system.config['amiberry_linemode'] == 'double':
                    commandArray.append("-s")
                    commandArray.append("gfx_linemode=double")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_linemode=double")

            # video resolution
            if system.isOptSet("amiberry_resolution"):
                if system.config['amiberry_resolution'] == 'lores':
                    commandArray.append("-s")
                    commandArray.append("gfx_resolution=lores")
                elif system.config['amiberry_resolution'] == 'superhires':
                    commandArray.append("-s")
                    commandArray.append("gfx_resolution=superhires")
                elif system.config['amiberry_resolution'] == 'hires':
                    commandArray.append("-s")
                    commandArray.append("gfx_resolution=hires")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_resolution=hires")

            # Scaling method
            if system.isOptSet("amiberry_scalingmethod"):
                if system.config['amiberry_scalingmethod'] == 'automatic':
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=false")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=-1")
                elif system.config['amiberry_scalingmethod'] == 'smooth':
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=true")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=1")
                elif system.config['amiberry_scalingmethod'] == 'pixelated':
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=true")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=0")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_lores_mode=false")
                commandArray.append("-s")
                commandArray.append("amiberry.scaling_method=-1")

            # display vertical centering
            commandArray.append("-s")
            commandArray.append("gfx_center_vertical=smart")

            # fix sound buffer and frequency
            commandArray.append("-s")
            commandArray.append("sound_max_buff=4096")
            commandArray.append("-s")
            commandArray.append("sound_frequency=48000")

            return Command.Command(array=commandArray,env={
                "AMIBERRY_DATA_DIR": "/usr/share/amiberry/",
                "AMIBERRY_HOME_DIR": "/userdata/system/configs/amiberry/",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)})
        # otherwise, unknown format
        return Command.Command(array=[])

    def floppiesFromRom(self, rom: str):
        rom_path = Path(rom)
        floppies: list[Path] = []
        indexDisk = rom_path.name.rfind("(Disk 1")

        # from one file (x1.zip), get the list of all existing files with the same extension + last char (as number) suffix
        # for example, "/path/toto0.zip" becomes ["/path/toto0.zip", "/path/toto1.zip", "/path/toto2.zip"]
        if rom_path.stem[-1:].isdigit():
            # path without the number
            fileprefix = rom_path.stem[:-1]

            # special case for 0 while numerotation can start at 1
            zero_file = rom_path.with_name(f"{fileprefix}0{rom_path.suffix}")
            if zero_file.is_file():
                floppies.append(zero_file)

            # adding all other files
            n = 1
            while (floppy := rom_path.with_name(f"{fileprefix}{n}{rom_path.suffix}")).is_file():
                floppies.append(floppy)
                n += 1
        # (Disk 1 of 2) format
        elif indexDisk != -1:
                # Several disks
                floppies.append(rom_path)
                prefix = rom_path.name[0:indexDisk+6]
                postfix = rom_path.name[indexDisk+7:]
                n = 2
                while (floppy := rom_path.with_name(f"{prefix}{n}{postfix}")).is_file():
                    floppies.append(floppy)
                    n += 1
        else:
           #Single ADF
           return [rom_path]

        return floppies

    def getRomType(self, filepath: str):
        extension = Path(filepath).suffix[1:].lower()

        if extension == "lha":
            return 'WHDL'
        elif extension == 'hdf' :
            return 'HDF'
        elif extension in ['iso','cue', 'chd'] :
            return 'CD'
        elif extension in ['adf','ipf']:
            return 'DISK'
        elif extension == "zip":
            # can be either whdl or adf
            with zipfile.ZipFile(filepath) as zip:
                for zipfilename in zip.namelist():
                    if zipfilename.find('/') == -1: # at the root
                        extension = Path(zipfilename).suffix[1:]
                        if extension == "info":
                            return 'WHDL'
                        elif extension == 'lha' :
                            eslog.warning("Amiberry doesn't support .lha inside a .zip")
                            return 'UNKNOWN'
                        elif extension == 'adf' :
                            return 'DISK'
            # no info or adf file found
            return 'UNKNOWN'

        return 'UNKNOWN'
