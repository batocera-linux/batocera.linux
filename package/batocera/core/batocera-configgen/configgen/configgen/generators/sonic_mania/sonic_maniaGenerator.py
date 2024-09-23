import os
import shutil
import configparser

from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class SonicManiaGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        source_file = '/usr/bin/sonic-mania'
        rom_directory = '/userdata/roms/sonic-mania'
        destination_file = rom_directory + '/sonic-mania'
        if not os.path.exists(destination_file):
            shutil.copy(source_file, destination_file)

        ## Configuration

        # VSync
        if system.isOptSet('smania_vsync'):
            selected_vsync = system.config['smania_vsync']
        else:
            selected_vsync = 'y'
        # Triple Buffering
        if system.isOptSet('smania_buffering'):
            selected_buffering = system.config['smania_buffering']
        else:
            selected_buffering = 'n'
        # Language
        if system.isOptSet('smania_language'):
            selected_language = system.config['smania_language']
        else:
            selected_language = '0'

        ## Create the Settings.ini file
        config = configparser.ConfigParser()
        config.optionxform = str
        # Game
        config['Game'] = {
            'devMenu': 'y',
            'faceButtonFlip': 'n',
            'enableControllerDebugging': 'n',
            'disableFocusPause': 'n',
            'region': '-1',
            'language': selected_language
        }
        # Video
        config['Video'] = {
            'windowed': 'n',
            'border': 'n',
            'exclusiveFS': 'y',
            'vsync': selected_vsync,
            'tripleBuffering': selected_buffering,
            'winWidth': '848',
            'winHeight': '480',
            'refreshRate': '60',
            'shaderSupport': 'y',
            'screenShader': '1',
            'maxPixWidth': '0'
        }
        # Audio
        config['Audio'] = {
            'streamsEnabled': 'y',
            'streamVolume': '1.000000',
            'sfxVolume': '1.000000'
        }
        # Save the ini file
        with open( rom_directory + '/Settings.ini', 'w') as configfile:
            config.write(configfile)

        # Now run
        os.chdir(rom_directory)
        commandArray = [destination_file]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
