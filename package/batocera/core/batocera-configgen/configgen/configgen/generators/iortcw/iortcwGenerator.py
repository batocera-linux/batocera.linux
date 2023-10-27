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
            "bind PAD0_Y": '"+useitem"',
            "bind PAD0_B": '"+activate"',
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
        
        ## ES options
        # Graphics API
        if system.isOptSet("iortcw_api"):
            options_to_set["seta cl_renderer"] = system.config["iortcw_api"]
        else:
            options_to_set["seta cl_renderer"] = "opengl1"
        # VSync
        if system.isOptSet("iortcw_vsync") and system.getOptBoolean("iortcw_vsync"):
            options_to_set["seta r_swapInterval"] = "1"
        else:
            options_to_set["seta r_swapInterval"] = "0"
        # Frame rate
        if system.isOptSet("iortcw_fps"):
            options_to_set["seta com_maxfps"] = system.config["iortcw_fps"]
        else:
            options_to_set["seta com_maxfps"] = "60"
        # Anisotropic filtering
        if system.isOptSet("iortcw_filtering"):
            options_to_set["seta r_ext_texture_filter_anisotropic"] = "1"
            options_to_set["seta r_ext_max_anisotropy"] = system.config["iortcw_filtering"]
        else:
            options_to_set["seta r_ext_texture_filter_anisotropic"] = "0"
            options_to_set["seta r_ext_max_anisotropy"] = "2"
        # Anti-aliasing
        if system.isOptSet("iortcw_aa"):
            options_to_set["seta r_ext_multisample"] = system.config["iortcw_aa"]
            options_to_set["seta r_ext_framebuffer_multisample"] = system.config["iortcw_aa"]
        else:
            options_to_set["seta r_ext_multisample"] = "0"
            options_to_set["seta r_ext_framebuffer_multisample"] = "0"

        # Skip intro video
        if system.isOptSet("iortcw_skip_video") and system.getOptBoolean("iortcw_skip_video"):
            options_to_set["seta com_introplayed"] = "1"
        else:
            options_to_set["seta com_introplayed"] = "0"
        
        # Set language
        if system.isOptSet("iortcw_language"):
            options_to_set["seta cl_language"] = system.config["iortcw_language"]
        else:
            options_to_set["seta cl_language"] = "0"
        
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

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
