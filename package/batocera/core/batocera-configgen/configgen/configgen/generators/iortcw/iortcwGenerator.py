#!/usr/bin/env python
import os
import controllersConfig
from generators.Generator import Generator
from Command import Command

class IORTCWGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        # Config file path
        config_file_path = "/userdata/roms/iortcw/main/wolfconfig.cfg"

        # Define the options to add or modify
        options_to_set = {
            "seta r_mode": "-1",
            "seta r_noborder": "1",
            "seta r_fullscreen": "1",
            "seta r_allowResize": "0",
            "seta r_centerWindow": "1",
            "seta r_inGameVideo": "1",
            "seta r_customheight": f'"{gameResolution["height"]}"',
            "seta r_customwidth": f'"{gameResolution["width"]}"',
            "seta in_joystick": "1",
            "seta in_joystickUseAnalog": "1",
            "bind PAD0_A": '"+moveup"',
            "bind PAD0_X": '"+movedown"',
            "bind PAD0_Y": '"+button2"',
            "bind PAD0_LEFTSHOULDER": 'weapnext',
            "bind PAD0_RIGHTSHOULDER": 'weapprev',
            "bind PAD0_LEFTSTICK_LEFT": '+moveleft',
            "bind PAD0_LEFTSTICK_RIGHT": '+moveright',
            "bind PAD0_LEFTSTICK_UP": '+forward',
            "bind PAD0_LEFTSTICK_DOWN": '+back',
            "bind PAD0_RIGHTSTICK_LEFT": '+left',
            "bind PAD0_RIGHTSTICK_RIGHT": '+right',
            "bind PAD0_RIGHTSTICK_UP": '+lookup',
            "bind PAD0_RIGHTSTICK_DOWN": '+lookdown',
            "bind PAD0_LEFTTRIGGER": '+speed',
            "bind PAD0_RIGHTTRIGGER": '+attack'
        }
        # TODO - seta cl_renderer "opengl1" & seta cl_language "0" etc

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
                
        # Single Player for now
        commandArray = ["/usr/bin/iortcw/iowolfsp"]

        # iortcw looks for roms in home + /iortcw
        return Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": "/userdata/roms",
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
