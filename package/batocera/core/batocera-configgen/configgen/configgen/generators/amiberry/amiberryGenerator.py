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

_logger = logging.getLogger(__name__)

_CONFIG_DIR: Final = CONFIGS / 'amiberry'
_CONFIG: Final = _CONFIG_DIR / 'conf' / 'amiberry.conf'
_RETROARCH_CUSTOM: Final = _CONFIG_DIR / 'conf' / 'retroarch' / 'overlay.cfg'
_RETROARCH_INPUTS_DIR: Final = _CONFIG_DIR / 'conf' / 'retroarch' / 'inputs'

class AmiberryGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "amiberry",
            "keys": {
                "exit": "KEY_F9",
                "menu": "KEY_F8"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(_RETROARCH_CUSTOM.parent)

        retroconfig = UnixSettings(_RETROARCH_CUSTOM, separator=' ')
        amiberryconf = UnixSettings(_CONFIG, separator=' ')
        amiberryconf.save('default_quit_key', 'F9')
        amiberryconf.save('default_open_gui_key', 'F8')
        amiberryconf.save('saveimage_dir', '/userdata/saves/amiga/')
        amiberryconf.save('savestate_dir', '/userdata/saves/amiga/')
        amiberryconf.save('screenshot_dir', '/userdata/screenshots/')
        amiberryconf.save('nvram_dir', '/userdata/saves/amiga/nvram/')
        amiberryconf.save('rom_path', '/userdata/bios/amiga/')
        amiberryconf.save('whdboot_path', '/userdata/system/configs/amiberry/whdboot/')
        amiberryconf.save('logfile_path', '/userdata/system/logs/amiberry.log')
        amiberryconf.save('controllers_path', '/userdata/system/configs/amiberry/conf/retroarch/inputs/')
        amiberryconf.save('retroarch_config', _RETROARCH_CUSTOM)
        amiberryconf.save('default_vkbd_enabled', system.config.get_bool('amiberry_virtual_keyboard', return_values=(1, 0)))
        amiberryconf.save('default_vkbd_hires', system.config.get_bool("amiberry_hires_keyboard", return_values=(1, 0)))
        amiberryconf.save("default_vkbd_transparency", system.config.get('amiberry_vkbd_transparency', '60'))
        amiberryconf.save("default_vkbd_language", system.config.get('amiberry_vkbd_language', 'US'))
        amiberryconf.save('default_vkbd_toggle', 'leftstick')
        amiberryconf.save('default_fullscreen_mode', '2')
        amiberryconf.save('write_logfile', 'yes')
        amiberryconf.write()

        romType = self.getRomType(rom)
        _logger.debug("romType: %s", romType)
        if romType != 'UNKNOWN' :
            commandArray: list[str | Path] = [ "/usr/bin/amiberry" ]
            if romType != 'WHDL' :
                commandArray.append("--model")
                commandArray.append(system.config.core)
            if romType == 'WHDL' :
                commandArray.append("--autoload")
                commandArray.append(rom)
            elif romType == 'HDF' :
                commandArray.append("-s")
                commandArray.append(f"hardfile2=rw,DH0:{rom},32,1,2,512,0,,uae0")
                commandArray.append("-s")
                commandArray.append(f"uaehf0=hdf,rw,DH0:{rom},32,1,2,512,0,,uae0")
            elif romType == 'UAE' :
                commandArray.append("-f")
                commandArray.append(rom)
            elif romType == 'CD' :
                commandArray.append("--cdimage")
                commandArray.append(rom)
            elif romType == 'DISK':
                # floppies
                for n, img in enumerate(self.floppiesFromRom(rom)[:4]):
                    commandArray.append(f"-{n}")
                    commandArray.append(img)
                # floppy path
                commandArray.append("-s")
                # Use disk folder as floppy path
                commandArray.append(f"amiberry.floppy_path={rom.parent}")

            # controller
            libretroControllers.writeControllersConfig(retroconfig, system, playersControllers, True)
            retroconfig.write()

            mkdir_if_not_exists(_RETROARCH_INPUTS_DIR)

            for pad in playersControllers:
                replacements = {f'_player{pad.player_number}_':'_'}
                # amiberry remove / included in pads names like "USB Downlo01.80 PS3/USB Corded Gamepad"
                padfilename = pad.real_name.replace("/", "")
                playerInputFilename = _RETROARCH_INPUTS_DIR / f"{padfilename}.cfg"
                with _RETROARCH_CUSTOM.open() as infile, playerInputFilename.open('w') as outfile:
                    for line in infile:
                        for src, target in replacements.items():
                            newline = line.replace(src, target)
                            if not newline.isspace():
                                outfile.write(newline)
                if pad.player_number == 1: # 1 = joystick port
                    commandArray.append("-s")
                    commandArray.append(f"joyport1_friendlyname={padfilename}")
                    if romType == 'CD' :
                        commandArray.append("-s")
                        commandArray.append("joyport1_mode=cd32joy")
                if pad.player_number == 2: # 0 = mouse for the player 2
                    commandArray.append("-s")
                    commandArray.append(f"joyport0_friendlyname={padfilename}")

            # fps
            if system.config.show_fps:
                commandArray.append("-s")
                commandArray.append("show_leds=true")

            # disable port 2 (otherwise, the joystick goes on it)
            commandArray.append("-s")
            commandArray.append("joyport2=")

            # remove interlace artifacts
            commandArray.append("-s")
            commandArray.append(f'gfx_flickerfixer={system.config.get_bool("amiberry_flickerfixer", return_values=("true", "false"))}')

            # auto height
            commandArray.append("-s")
            commandArray.append(f'amiberry.gfx_auto_height={system.config.get_bool("amiberry_auto_height", return_values=("true", "false"))}')

            # line mode
            commandArray.append("-s")
            commandArray.append(f"gfx_linemode={system.config.get('amiberry_linemode', 'double')}")

            # video resolution
            commandArray.append("-s")
            commandArray.append(f"gfx_resolution={system.config.get('amiberry_resolution', 'hires')}")

            # Scaling method
            match system.config.get("amiberry_scalingmethod"):
                case "smooth":
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=true")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=1")
                case "pixelated":
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=true")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=0")
                case _:
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

            # Disable GUI at launch
            if not commandArray or commandArray[-1] != "-G":
                commandArray.append("-G")

            return Command.Command(array=commandArray,env={
                 "AMIBERRY_DATA_DIR": "/usr/share/amiberry/data/",
                 "AMIBERRY_HOME_DIR": "/userdata/system/configs/amiberry",
                 "AMIBERRY_CONFIG_DIR": "/userdata/system/configs/amiberry/conf/",
                 "AMIBERRY_PLUGINS_DIR": "/userdata/system/configs/amiberry/plugins/",
                 "XDG_DATA_HOME": "/userdata/system/configs/",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)})
        # otherwise, unknown format
        return Command.Command(array=[])

    def floppiesFromRom(self, rom: Path):
        floppies: list[Path] = []
        indexDisk = rom.name.rfind("(Disk 1")

        # from one file (x1.zip), get the list of all existing files with the same extension + last char (as number) suffix
        # for example, "/path/toto0.zip" becomes ["/path/toto0.zip", "/path/toto1.zip", "/path/toto2.zip"]
        if rom.stem[-1:].isdigit():
            # path without the number
            fileprefix = rom.stem[:-1]

            # special case for 0 while numerotation can start at 1
            zero_file = rom.with_name(f"{fileprefix}0{rom.suffix}")
            if zero_file.is_file():
                floppies.append(zero_file)

            # adding all other files
            n = 1
            while (floppy := rom.with_name(f"{fileprefix}{n}{rom.suffix}")).is_file():
                floppies.append(floppy)
                n += 1
        # (Disk 1 of 2) format
        elif indexDisk != -1:
                # Several disks
                floppies.append(rom)
                prefix = rom.name[0:indexDisk+6]
                postfix = rom.name[indexDisk+7:]
                n = 2
                while (floppy := rom.with_name(f"{prefix}{n}{postfix}")).is_file():
                    floppies.append(floppy)
                    n += 1
        else:
           #Single ADF
           return [rom]

        return floppies

    def getRomType(self, filepath: Path):
        extension = filepath.suffix[1:].lower()

        if extension == "lha":
            return 'WHDL'
        if extension == 'hdf' :
            return 'HDF'
        if extension == 'uae' :
            return 'UAE'
        if extension in ['iso','cue', 'chd'] :
            return 'CD'
        if extension in ['adf','ipf']:
            return 'DISK'
        if extension == "zip":
            # can be either whdl or adf
            with zipfile.ZipFile(filepath) as zip:
                for zipfilename in zip.namelist():
                    if zipfilename.find('/') == -1: # at the root
                        extension = Path(zipfilename).suffix[1:]
                        if extension == "info":
                            return 'WHDL'
                        if extension == 'lha' :
                            _logger.warning("Amiberry doesn't support .lha inside a .zip")
                            return 'UNKNOWN'
                        if extension in ['adf','ipf'] :
                            return 'DISK'
            # no info or adf file found
            return 'UNKNOWN'

        return 'UNKNOWN'
