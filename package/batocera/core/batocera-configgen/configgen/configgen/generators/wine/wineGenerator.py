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
                nested_resolution = system.getOptString("gamescope_nested_resolution")
                if nested_resolution:
                    try:
                        nested_width, nested_height = nested_resolution.split("x")
                        gamescope_options.extend([
                            "-w", nested_width.strip(),
                            "-h", nested_height.strip()
                        ])
                    except Exception:
                        pass

                # Retrieve output resolution
                output_resolution = system.getOptString("gamescope_output_resolution")
                if output_resolution:
                    try:
                        output_width, output_height = output_resolution.split("x")
                        gamescope_options.extend([
                            "-W", output_width.strip(),
                            "-H", output_height.strip()
                        ])
                    except Exception:
                        pass

                # Retrieve refresh rate
                nested_refresh = system.getOptString("gamescope_nested_refresh")
                if nested_refresh:
                    gamescope_options.extend(["-r", str(nested_refresh)])

                # --- New: Framerate limit ---
                # Set a simple framerate limit as a divisor of the refresh rate.
                # Default is off (i.e. not used) unless explicitly set.
                framerate_limit = system.getOptString("gamescope_framerate_limit", "off").lower()
                if framerate_limit != "off":
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

                # HDR: only add if set to on/true/1
                hdr = system.getOptString("gamescope_hdr", "0").lower()
                if hdr in ["1", "on", "true"]:
                    gamescope_options.append("--hdr-enabled")

                    # Only process the following HDR options if HDR is enabled:

                    # SDR gamut wideness: add if not "off"
                    sdr_gamut = system.getOptString("gamescope_sdr_gamut_wideness", "off").lower()
                    if sdr_gamut != "off":
                        gamescope_options.extend(["--sdr-gamut-wideness", sdr_gamut])
                    
                    # HDR SDR content nits: add if not "off"
                    hdr_sdr_nits = system.getOptString("gamescope_hdr_sdr_content_nits", "off")
                    if hdr_sdr_nits.lower() != "off":
                        gamescope_options.extend(["--hdr-sdr-content-nits", hdr_sdr_nits])
                    
                    # HDR ITM enabled: add if set to on/true/1
                    hdr_itm_enabled = system.getOptString("gamescope_hdr_itm_enabled", "0").lower()
                    if hdr_itm_enabled in ["on", "1", "true"]:
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
                borderless = system.getOptString("gamescope_borderless").lower()
                if borderless in ["on", "1", "true"]:
                    gamescope_options.append("-b")
                else:
                    gamescope_options.append("-f")

                # Reshade effect.
                reshade_effect = system.getOptString("gamescope_reshade_effect")
                if reshade_effect:
                    gamescope_options.extend(["--reshade-effect", reshade_effect])

                # Prepend "gamescope" and its options to the base Wine command.
                commandArray = ["gamescope"] + gamescope_options + commandArray

            return Command.Command(array=commandArray, env=environment)

        raise Exception("invalid system " + system.name)

    def getMouseMode(self, config, rom):
        if "force_mouse" in config and config["force_mouse"] == "0":
            return False
        else:
            return True
