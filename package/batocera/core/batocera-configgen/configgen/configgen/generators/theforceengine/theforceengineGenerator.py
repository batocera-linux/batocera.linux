from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

forceConfigDir = CONFIGS / "theforceengine"
forceModsDir = forceConfigDir / "Mods"
forcePatchFile = "v3.zip" # current patch version
forceModFile = forceModsDir / forcePatchFile
forceConfigFile = forceConfigDir / "settings.ini"

class TheForceEngineGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "theforceengine",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "save_state": [ "KEY_LEFTALT", "KEY_F5" ], "restore_state": [ "KEY_LEFTALT", "KEY_F9" ] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Check if the directories exist, if not create them
        mkdir_if_not_exists(forceConfigDir)
        mkdir_if_not_exists(forceModsDir)

        mod_name = None
        # use the patch file if available
        if forceModFile.exists():
            mod_name = forcePatchFile

        # Open the .tfe rom file for user mods
        with rom.open() as file:
            # Read the first line and store it as 'first_line'
            first_line = file.readline().strip()
            # use the first_line as mod if the file isn't empty
            if first_line:
                mod_name = first_line

        ## Configure
        forceConfig = CaseSensitiveConfigParser()
        if forceConfigFile.exists():
            forceConfig.read(forceConfigFile)

        # Windows
        if not forceConfig.has_section("Window"):
            forceConfig.add_section("Window")
        forceConfig.set("Window", "width", format(gameResolution["width"]))
        forceConfig.set("Window", "height", format(gameResolution["height"]))
        # always fullscreen
        forceConfig.set("Window", "fullscreen", "true")

        # Graphics
        if not forceConfig.has_section("Graphics"):
            forceConfig.add_section("Graphics")

        res_height = system.config.get_int("force_render_res", gameResolution["height"])
        res_width = int(res_height) * 4/3
        res_width_int = int(res_width)
        forceConfig.set("Graphics", "gameWidth", f"{res_width_int if res_width == res_width_int else res_width}")
        forceConfig.set("Graphics", "gameHeight", f"{res_height}")

        forceConfig.set("Graphics", "widescreen", system.config.get_bool("force_widescreen", return_values=("true", "false")))
        forceConfig.set("Graphics", "vsync", system.config.get_bool("force_vsync", True, return_values=("true", "false")))
        forceConfig.set("Graphics", "frameRateLimit", system.config.get("force_rate", "60"))
        forceConfig.set("Graphics", "renderer", system.config.get("force_api", "1"))
        forceConfig.set("Graphics", "colorMode", system.config.get("force_colour", "0"))
        forceConfig.set("Graphics", "useBilinear", system.config.get_bool("force_bilinear", return_values=("true", "false")))
        forceConfig.set("Graphics", "useMipmapping", system.config.get_bool("force_mipmapping", return_values=("true", "false")))
        forceConfig.set("Graphics", "reticleEnable", system.config.get_bool("force_crosshair", return_values=("true", "false")))
        forceConfig.set("Graphics", "bloomEnabled", system.config.get_bool("force_postfx", return_values=("true", "false")))

        # Hud
        if not forceConfig.has_section("Hud"):
            forceConfig.add_section("Hud")
        forceConfig.set("Hud", "hudScale", '"Proportional"')
        forceConfig.set("Hud", "hudPos", '"Edge"')
        forceConfig.set("Hud", "scale", "1.000")

        # Enhancements
        if not forceConfig.has_section("Enhancements"):
            forceConfig.add_section("Enhancements")

        force_hd = system.config.get_bool("force_hd", return_values=("1", "0"))
        forceConfig.set("Enhancements", "hdTextures", force_hd)
        forceConfig.set("Enhancements", "hdSprites", force_hd)
        forceConfig.set("Enhancements", "hdHud", force_hd)

        if force_hd == "1":
            # force true colour for HD textures
            forceConfig.set("Graphics", "colorMode", "2")

        # Sound
        if not forceConfig.has_section("Sound"):
            forceConfig.add_section("Sound")

        forceConfig.set("Sound", "disableSoundInMenus", system.config.get_bool("force_menu_sound", return_values=("true", "false")))
        forceConfig.set("Sound", "use16Channels", system.config.get_bool("force_digital_audio", return_values=("true", "false")))

        # System
        if not forceConfig.has_section("System"):
            forceConfig.add_section("System")

        # A11y
        if not forceConfig.has_section("A11y"):
            forceConfig.add_section("A11y")

        # Game
        if not forceConfig.has_section("Game"):
            forceConfig.add_section("Game")
        # currently Dark Forces only - to do
        forceConfig.set("Game", "game", "Dark Forces")

        # Dark_Forces
        if not forceConfig.has_section("Dark_Forces"):
            forceConfig.add_section("Dark_Forces")
        # currently use this directory
        forceConfig.set("Dark_Forces", "sourcePath", '"/userdata/roms/theforceengine/Star Wars - Dark Forces/"')

        forceConfig.set("Dark_Forces", "disableFightMusic", system.config.get_bool("force_fight_music", return_values=("true", "false")))
        forceConfig.set("Dark_Forces", "enableAutoaim", system.config.get_bool("force_auto_aim", True, return_values=("true", "false")))
        forceConfig.set("Dark_Forces", "showSecretFoundMsg", system.config.get_bool("force_secret_msg", True, return_values=("true", "false")))
        forceConfig.set("Dark_Forces", "autorun", system.config.get_bool("force_auto_run", return_values=("true", "false")))
        forceConfig.set("Dark_Forces", "bobaFettFacePlayer", system.config.get_bool("force_boba", return_values=("true", "false")))
        forceConfig.set("Dark_Forces", "smoothVUEs", system.config.get_bool("force_smooth_vues", return_values=("true", "false")))

        # Outlaws
        if not forceConfig.has_section("Outlaws"):
            forceConfig.add_section("Outlaws")
        forceConfig.set("Outlaws", "sourcePath", '""')

        # CVar
        if not forceConfig.has_section("CVar"):
            forceConfig.add_section("CVar")

        ## Update the configuration file
        with ensure_parents_and_open(forceConfigFile, 'w') as configfile:
            forceConfig.write(configfile)

        ## Setup the command
        commandArray = ["theforceengine"]

        ## Accomodate Mods, skip cutscenes etc
        if (skip_cutscenes := system.config.get("force_skip_cutscenes")) == "initial":
            commandArray.extend(["-c0"])
        elif skip_cutscenes == "skip":
            commandArray.extend(["-c"])
        # Add mod zip file if necessary
        if mod_name is not None:
            commandArray.extend([f"-u{mod_name}"])

        # Run - only Dark Forces currently
        commandArray.extend(["-gDARK"])

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "TFE_DATA_HOME": forceConfigDir
            }
        )

    # Show mouse for menu actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get("force_widescreen") == "1":
            return 16/9
        return 4/3
