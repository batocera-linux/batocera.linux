from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BIOS, CACHE, CONFIGS, SAVES, SCREENSHOTS, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

scummConfigDir: Final = CONFIGS / "scummvm"
scummConfigFile: Final = scummConfigDir / "scummvm.ini"
scummExtra: Final = BIOS / "scummvm" / "extra"

class ScummVMGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "scummvm",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        # crete /userdata/bios/scummvm/extra folder if it doesn't exist
        mkdir_if_not_exists(scummExtra)

        # create / modify scummvm config file as needed
        scummConfig = CaseSensitiveConfigParser()
        if scummConfigFile.exists():
            scummConfig.read(scummConfigFile)

        if not scummConfig.has_section("scummvm"):
            scummConfig.add_section("scummvm")
        # set gui_browser_native to false
        scummConfig.set("scummvm", "gui_browser_native", "false")

        # save the ini file
        with ensure_parents_and_open(scummConfigFile, 'w') as configfile:
            scummConfig.write(configfile)

        # Find rom path
        if rom_path.is_dir():
          # rom is a directory: must contains a <game name>.scummvm file
          romPath = rom_path
          romName = next(rom_path.glob("*.scummvm")).stem
        else:
          # rom is a file: split in directory and file name
          romPath = rom_path.parent
          # Get rom name without extension
          romName = rom_path.stem

        # pad number
        nplayer = 1
        id = 0
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                id=pad.index
            nplayer += 1

        commandArray = ["/usr/bin/scummvm", "-f"]

        # set the resolution
        window_width = str(gameResolution["width"])
        window_height = str(gameResolution["height"])
        commandArray.append(f"--window-size={window_width},{window_height}")

        ## user options

        # scale factor
        if system.isOptSet("scumm_scale"):
            commandArray.append(f"--scale-factor={system.config['scumm_scale']}")
        else:
            commandArray.append("--scale-factor=3")

        # sclaer mode
        if system.isOptSet("scumm_scaler_mode"):
            commandArray.append(f"--scaler={system.config['scumm_scaler_mode']}")
        else:
            commandArray.append("--scaler=normal")

        #  stretch mode
        if system.isOptSet("scumm_stretch"):
            commandArray.append(f"--stretch-mode={system.config['scumm_stretch']}")
        else:
            commandArray.append("--stretch-mode=center")

        # renderer
        if system.isOptSet("scumm_renderer"):
            commandArray.append(f"--renderer={system.config['scumm_renderer']}")
        else:
            commandArray.append("--renderer=opengl")

        # language
        if system.isOptSet("scumm_language"):
            commandArray.extend(["-q", f"{system.config['scumm_language']}"])

        # logging
        commandArray.append("--logfile=/userdata/system/logs/scummvm.log")

        commandArray.extend(
            [f"--joystick={id}",
            f"--screenshotspath={SCREENSHOTS}",
            f"--extrapath={scummExtra}",
            f"--path={romPath}",
            f"{romName}"]
        )

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":CONFIGS,
                "XDG_DATA_HOME":SAVES,
                "XDG_CACHE_HOME":CACHE,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if ("scumm_stretch" in config and config["scumm_stretch"] == "fit_force_aspect") or ("scumm_stretch" in config and config["scumm_stretch"] == "pixel-perfect"):
            return 4/3
        return 16/9
