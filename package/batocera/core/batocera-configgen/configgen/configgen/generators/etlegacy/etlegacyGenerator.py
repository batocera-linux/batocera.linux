import os
import shutil

from ... import Command
from ... import controllersConfig
from ... import batoceraFiles
from ..Generator import Generator

class ETLegacyGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        etLegacyDir = "/userdata/roms/etlegacy/legacy"
        etLegacyFile = "/legacy_2.82-dirty.pk3"
        etLegacySource = "/usr/share/etlegacy" + etLegacyFile
        etLegacyDest = etLegacyDir + etLegacyFile

        ## Configuration

        # Config file path
        config_dir = batoceraFiles.CONF + "/etlegacy/legacy"
        config_file_path = config_dir + "/etconfig.cfg"

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # Define the options to add or modify
        options_to_set = {
            "seta r_mode": "-1",
            "seta r_fullscreen": "1",
            "seta r_allowResize": "0",
            "seta r_centerWindow": "1",
            "seta r_customheight": f'"{gameResolution["height"]}"',
            "seta r_customwidth": f'"{gameResolution["width"]}"'
        }

        # Set language
        if system.isOptSet("etlegacy_language"):
            options_to_set["seta cl_lang"] = system.config["etlegacy_language"]
            options_to_set["seta ui_cl_lang"] = system.config["etlegacy_language"]
        else:
            options_to_set["seta cl_lang"] = "en"
            options_to_set["seta ui_cl_lang"] = "en"

        # Check if the file exists
        if os.path.isfile(config_file_path):
            with open(config_file_path, 'r') as config_file:
                lines = config_file.readlines()

            # Loop through the options and update the lines
            for key, value in options_to_set.items():
                option_exists = any(key in line for line in lines)
                if not option_exists:
                    lines.append(f"{key} \"{value}\"\n")
                else:
                    for i, line in enumerate(lines):
                        if key in line:
                            lines[i] = f"{key} \"{value}\"\n"

            # Write the modified content back to the file
            with open(config_file_path, 'w') as config_file:
                config_file.writelines(lines)
        else:
            # File doesn't exist, create it and add the options
            with open(config_file_path, 'w') as config_file:
                for key, value in options_to_set.items():
                    config_file.write(f"{key} \"{value}\"\n")

        # copy mod files needed
        if not os.path.exists(etLegacyDir):
            os.makedirs(etLegacyDir)

        # copy latest mod file to the rom directory
        if not os.path.exists(etLegacyDest):
            shutil.copy(etLegacySource, etLegacyDest)
        else:
            source_version = os.path.getmtime(etLegacySource)
            destination_version = os.path.getmtime(etLegacyDest)
            if source_version > destination_version:
                shutil.copy(etLegacySource, etLegacyDest)

        commandArray = ["etl"]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
