from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class WineGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "wine",
            "keys": { "exit": "/usr/bin/batocera-wine windows stop" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "windows", "install", rom]
            return Command.Command(array=commandArray)
        elif system.name == "windows":
            commandArray = ["batocera-wine", "windows", "play", rom]

            environment: dict[str, str | Path] = {}
            #system.language
            try:
                language = subprocess.check_output("batocera-settings-get system.language", shell=True, text=True).strip()
            except subprocess.CalledProcessError:
                language = 'en_US'
            if language:
                environment.update({
                    "LANG": language + ".UTF-8",
                    "LC_ALL": language + ".UTF-8"
                    }
                )
            # sdl controller option - default is on
            if not system.isOptSet("sdl_config") or system.getOptBoolean("sdl_config"):
                environment.update(
                    {
                        "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                        "SDL_JOYSTICK_HIDAPI": "0"
                    }
                )
            # ensure nvidia driver used for vulkan
            if Path('/var/tmp/nvidia.prime').exists():
                variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
                for variable_name in variables_to_remove:
                    if variable_name in os.environ:
                        del os.environ[variable_name]

                environment.update(
                    {
                        'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/nvidia_icd.i686.json',
                    }
                )

            # --- GameScope Support using system options ---
            if system.config.get_bool("gamescope"):
                gamescope_options = []

                # Retrieve nested resolution
                nested_resolution = system.config.get_str("gamescope_nested_resolution", "1920x1080")
                nested_width, _, nested_height = nested_resolution.partition("x")
                gamescope_options.extend([
                "-w", nested_width.strip(),
                "-h", nested_height.strip()
                ])

                # Retrieve output resolution
                output_resolution = system.config.get_str("gamescope_output_resolution", "1920x1080")
                output_width, _, output_height = output_resolution.partition("x")
                gamescope_options.extend([
                "-W", output_width.strip(),
                "-H", output_height.strip()
                ])

                # Retrieve refresh rate
                gamescope_options.extend(["-r", system.config.get_str("gamescope_nested_refresh", "60")])

                # Set a simple framerate limit as a divisor of the refresh rate.
                # Default is off (i.e. not used) unless explicitly set.
                if framerate_limit := system.config.get_str("gamescope_framerate_limit"):
                gamescope_options.extend(["--framerate-limit", framerate_limit])

                # Upscaler type
                scaler = system.getOptString("gamescope_scaler")
                if scaler:
                    gamescope_options.extend(["-S", scaler])

                # Upscaler filter
                filt = system.getOptString("gamescope_filter")
                if filt:
                    gamescope_options.extend(["-F", filt])

                # Upscaler sharpness: only add if not set to "auto"
                sharpness = system.getOptString("gamescope_sharpness")
                if sharpness and sharpness != "auto":
                    gamescope_options.extend(["--sharpness", sharpness])

                # HDR
                if system.config.get_bool("gamescope_hdr"):

                    # Only process the following HDR options if HDR is enabled:

                    # SDR gamut wideness: add if not "off"
                    sdr_gamut = system.getOptString("gamescope_sdr_gamut_wideness", "off").lower()
                    if sdr_gamut != "off":
                        gamescope_options.extend(["--sdr-gamut-wideness", sdr_gamut])
                    
                    # HDR SDR content nits: add if not "off"
                    hdr_sdr_nits = system.getOptString("gamescope_hdr_sdr_content_nits", "off")
                    if hdr_sdr_nits.lower() != "off":
                        gamescope_options.extend(["--hdr-sdr-content-nits", hdr_sdr_nits])
                    
                    # HDR ITM enabled: 
                    if system.config.get_bool("gamescope_hdr_itm_enabled", False):
                        gamescope_options.append("--hdr-itm-enabled")

                    # HDR ITM SDR nits: add if not "off"
                    hdr_itm_sdr_nits = system.getOptString("gamescope_hdr_itm_sdr_nits", "off")
                    if hdr_itm_sdr_nits.lower() != "off":
                        gamescope_options.extend(["--hdr-itm-sdr-nits", hdr_itm_sdr_nits])
                    
                    # HDR ITM target nits: add if not "off"
                    hdr_itm_target = system.getOptString("gamescope_hdr_itm_target_nits", "off")
                    if hdr_itm_target.lower() != "off":
                        gamescope_options.extend(["--hdr-itm-target-nits", hdr_itm_target])

                # Use borderless if explicitly enabled; otherwise, default to fullscreen.
                gamescope_options.append(system.config.get_bool("gamescope_borderless", return_values=("-b", "-f")))

                # Reshade effect.
                reshade_effect = system.getOptString("gamescope_reshade_effect")
                if reshade_effect:
                    gamescope_options.extend(["--reshade-effect", reshade_effect])

                # Prepend "gamescope" and its options to the base Wine command.
                commandArray = ["gamescope", *gamescope_options, *commandArray]

            return Command.Command(array=commandArray, env=environment)

        raise Exception("invalid system " + system.name)

    def getMouseMode(self, config, rom):
        if "force_mouse" in config and config["force_mouse"] == "0":
            return False
        else:
            return True
