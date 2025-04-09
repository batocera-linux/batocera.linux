from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BIOS, CACHE, CONFIGS, SAVES, SCREENSHOTS, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import Controller, generate_sdl_game_controller_config
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
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": ["KEY_LEFTCTRL", "KEY_F5"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
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
        if rom.is_dir():
          # rom is a directory: must contains a <game name>.scummvm file
          romPath = rom
          romName = next(rom.glob("*.scummvm")).stem
        elif rom.stat().st_size < 3::
          # rom is a file less than 3 bytes: split in directory and file name
          romPath = rom.parent
          # Get rom name without extension
          romName = rom.stem
        else:
          # rom is a file containing the game ID inside, open and read game ID from ROM-file: split directory
          romName = Path(rom).read_text().rstrip('\n')
          romPath = rom.parent

        # pad number
        id = 0
        if pad := Controller.find_player_number(playersControllers, 1):
            id = pad.index

        commandArray = ["/usr/bin/scummvm", "-f"]

        # set the resolution
        window_width = str(gameResolution["width"])
        window_height = str(gameResolution["height"])
        commandArray.append(f"--window-size={window_width},{window_height}")

        ## user options

        # scale factor
        commandArray.append(f"--scale-factor={system.config.get('scumm_scale', '3')}")

        # sclaer mode
        commandArray.append(f"--scaler={system.config.get('scumm_scaler_mode', 'normal')}")

        #  stretch mode
        if stretch := system.config.get("scumm_stretch"):
            commandArray.append(f"--stretch-mode={stretch}")

        # renderer
        commandArray.append(f"--renderer={system.config.get('scumm_renderer', 'opengl')}")

        # language
        if language := system.config.get("scumm_language"):
            commandArray.extend(["-q", f"{language}"])

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
        if config.get("scumm_stretch") in ["fit_force_aspect", "pixel-perfect"]:
            return 4/3
        return 16/9
