from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import ruamel.yaml
import ruamel.yaml.util

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

vitaConfig = CONFIGS / 'vita3k'
vitaSaves = SAVES / 'psvita'
vitaConfigFile = vitaConfig / 'config.yml'

class Vita3kGenerator(Generator):


    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vita3k",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ENTER", "pause": "KEY_ENTER" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Create save folder
        mkdir_if_not_exists(vitaSaves)

        # Move saves if necessary
        if (vitaConfig / 'ux0').is_dir():
            # Move all folders from vitaConfig to vitaSaves except "data", "lang", and "shaders-builtin"
            for item in vitaConfig.iterdir():
                if item.name not in ['data', 'lang', 'shaders-builtin']:
                    if item.is_dir():
                        shutil.move(item, vitaSaves)

        # Create the config.yml file if it doesn't exist
        mkdir_if_not_exists(vitaConfig)

        vita3kymlconfig = None
        indent = None
        block_seq_indent = None

        if vitaConfigFile.is_file():
            with vitaConfigFile.open('r') as stream:
                vita3kymlconfig, indent, block_seq_indent = ruamel.yaml.util.load_yaml_guess_indent(stream)

        if vita3kymlconfig is None:
            vita3kymlconfig = {}

        if indent is None:
            indent = 2

        if block_seq_indent is None:
            block_seq_indent = 0

        # ensure the correct path is set
        vita3kymlconfig["pref-path"] = f"{vitaSaves!s}"

        # Set the renderer
        if system.isOptSet("vita3k_gfxbackend"):
            vita3kymlconfig["backend-renderer"] = system.config["vita3k_gfxbackend"]
        else:
            vita3kymlconfig["backend-renderer"] = "OpenGL"
        # Set the resolution multiplier
        if system.isOptSet("vita3k_resolution"):
            vita3kymlconfig["resolution-multiplier"] = int(system.config["vita3k_resolution"])
        else:
            vita3kymlconfig["resolution-multiplier"] = 1
        # Set FXAA
        if system.isOptSet("vita3k_fxaa") and system.getOptBoolean("vita3k_surface") == True:
            vita3kymlconfig["enable-fxaa"] = "true"
        else:
            vita3kymlconfig["enable-fxaa"] = "false"
        # Set VSync
        if system.isOptSet("vita3k_vsync") and system.getOptBoolean("vita3k_surface") == False:
            vita3kymlconfig["v-sync"] = "false"
        else:
            vita3kymlconfig["v-sync"] = "true"
        # Set the anisotropic filtering
        if system.isOptSet("vita3k_anisotropic"):
            vita3kymlconfig["anisotropic-filtering"] = int(system.config["vita3k_anisotropic"])
        else:
            vita3kymlconfig["anisotropic-filtering"] = 1
        # Set the linear filtering option
        if system.isOptSet("vita3k_linear") and system.getOptBoolean("vita3k_surface") == True:
            vita3kymlconfig["enable-linear-filter"] = "true"
        else:
            vita3kymlconfig["enable-linear-filter"] = "false"
        # Surface Sync
        if system.isOptSet("vita3k_surface") and system.getOptBoolean("vita3k_surface") == False:
            vita3kymlconfig["disable-surface-sync"] = "false"
        else:
            vita3kymlconfig["disable-surface-sync"] = "true"

        # Vita3k is fussy over its yml file
        # We try to match it as close as possible, but the 'vectors' cause yml formatting issues
        yaml = ruamel.yaml.YAML()
        yaml.explicit_start = True
        yaml.explicit_end = True
        yaml.indent(mapping=indent, sequence=indent, offset=block_seq_indent)

        with vitaConfigFile.open('w') as fp:
            yaml.dump(vita3kymlconfig, fp)

        # Simplify the rom name (strip the directory & extension)
        begin, end = rom.find('['), rom.rfind(']')
        smplromname = rom[begin+1: end]
        # because of the yml formatting, we don't allow Vita3k to modify it
        # using the -w & -f options prevents Vita3k from re-writing & prompting the user in GUI
        # we want to avoid that so roms load straight away
        if (vitaSaves / 'ux0' / 'app' / smplromname).is_dir():
            commandArray = ["/usr/bin/vita3k/Vita3K", "-F", "-w", "-f", "-c", vitaConfigFile, "-r", smplromname]
        else:
            # Game not installed yet, let's open the menu
            commandArray = ["/usr/bin/vita3k/Vita3K", "-F", "-w", "-f", "-c", vitaConfigFile, rom]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_DATA_HOME": SAVES,
                "XDG_CACHE_HOME": CACHE
            }
        )

    # Show mouse for touchscreen actions
    def getMouseMode(self, config, rom):
        if "vita3k_show_pointer" in config and config["vita3k_show_pointer"] == "0":
             return False
        else:
             return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
