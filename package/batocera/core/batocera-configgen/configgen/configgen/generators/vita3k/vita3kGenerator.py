from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Any, cast

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
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F12"], "menu": "KEY_ENTER", "pause": "KEY_ENTER" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Create save folder
        mkdir_if_not_exists(vitaSaves)

        # Move saves if necessary
        if (vitaConfig / 'ux0').is_dir():
            # Move all folders from vitaConfig to vitaSaves except "data", "lang", and "shaders-builtin"
            for item in vitaConfig.iterdir():
                if item.name not in ['data', 'lang', 'shaders-builtin'] and item.is_dir():
                    shutil.move(item, vitaSaves)

        # Create the config.yml file if it doesn't exist
        mkdir_if_not_exists(vitaConfig)

        vita3kymlconfig: dict[str, Any] | None = None
        indent: int | None = None
        block_seq_indent: int | None = None

        if vitaConfigFile.is_file():
            with vitaConfigFile.open('r') as stream:
                vita3kymlconfig, indent, block_seq_indent = cast('tuple[dict[str, Any] | None, int | None, int | None]', ruamel.yaml.util.load_yaml_guess_indent(stream))

        if vita3kymlconfig is None:
            vita3kymlconfig = {}

        if indent is None:
            indent = 2

        if block_seq_indent is None:
            block_seq_indent = 0

        # ensure the correct path is set
        vita3kymlconfig["pref-path"] = f"{vitaSaves!s}"

        # Set the renderer
        vita3kymlconfig["backend-renderer"] = system.config.get("vita3k_gfxbackend", "OpenGL")

        # Set the resolution multiplier
        vita3kymlconfig["resolution-multiplier"] = system.config.get_int("vita3k_resolution", 1)

        # Set FXAA
        vita3kymlconfig["enable-fxaa"] = system.config.get_bool("vita3k_fxaa", return_values=("true", "false"))

        # Set VSync
        vita3kymlconfig["v-sync"] = system.config.get_bool("vita3k_vsync", True, return_values=("true", "false"))

        # Set the anisotropic filtering
        vita3kymlconfig["anisotropic-filtering"] = system.config.get_int("vita3k_anisotropic", 1)

        # Set the linear filtering option
        vita3kymlconfig["enable-linear-filter"] = system.config.get_bool("vita3k_linear", return_values=("true", "false"))

        # Surface Sync
        vita3kymlconfig["disable-surface-sync"] = system.config.get_bool("vita3k_surface", True, return_values=("true", "false"))

        # Vita3k is fussy over its yml file
        # We try to match it as close as possible, but the 'vectors' cause yml formatting issues
        yaml = ruamel.yaml.YAML()
        yaml.explicit_start = True
        yaml.explicit_end = True
        yaml.indent(mapping=indent, sequence=indent, offset=block_seq_indent)

        with vitaConfigFile.open('w') as fp:
            yaml.dump(vita3kymlconfig, fp)

        # Simplify the rom name (strip the directory & extension)
        begin, end = rom.stem.find('['), rom.stem.rfind(']')
        smplromname = rom.stem[begin+1: end]
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
        return config.get("vita3k_show_pointer") != '0'

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
