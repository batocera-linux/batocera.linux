import os
import shutil
import json

from ... import batoceraFiles
from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class Sonic3AIRGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        config_file = "/usr/bin/sonic3-air/config.json"
        oxygen_file = "/usr/bin/sonic3-air/oxygenproject.json"
        s2_config_folder = batoceraFiles.CONF + "/Sonic3AIR"
        config_dest_file = s2_config_folder + "/config.json"
        oxygen_dest_file = s2_config_folder + "/oxygenproject.json"
        saves_folder = "/userdata/saves/sonic3-air"
        settings_file = s2_config_folder + "/settings.json"

        ## Configuration

        # copy configuration json files so we can manipulate them
        if not os.path.exists(config_dest_file):
            if not os.path.exists(s2_config_folder):
                os.makedirs(s2_config_folder)
            shutil.copy(config_file, config_dest_file)
        if not os.path.exists(oxygen_dest_file):
            if not os.path.exists(s2_config_folder):
                os.makedirs(s2_config_folder)
            shutil.copy(oxygen_file, oxygen_dest_file)

        # saves dir
        if not os.path.exists(saves_folder):
                os.makedirs(saves_folder)

        # read the json file
        # can't use `import json` as the file is not compliant
        with open(config_dest_file, 'r') as file:
            json_text = file.read()
        # update the "SaveStatesDir"
        json_text = json_text.replace('"SaveStatesDir":  "saves/states"', '"SaveStatesDir":  "/userdata/saves/sonic3-air"')

        # extract the current resolution value
        current_resolution = json_text.split('"WindowSize": "')[1].split('"')[0]
        # replace the resolution with new values
        new_resolution = str(gameResolution["width"]) + " x " + str(gameResolution["height"])
        json_text = json_text.replace(f'"WindowSize": "{current_resolution}"', f'"WindowSize": "{new_resolution}"')

        with open(config_dest_file, 'w') as file:
            file.write(json_text)

        # settings json - compliant
        # ensure fullscreen
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as file:
                settings_data = json.load(file)
                settings_data["Fullscreen"] = 1
        else:
            settings_data = {"Fullscreen": 1}

        with open(settings_file, 'w') as file:
            json.dump(settings_data, file, indent=4)

        # now run
        commandArray = ["/usr/bin/sonic3-air/sonic3air_linux"]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME":batoceraFiles.CONF,
                "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
