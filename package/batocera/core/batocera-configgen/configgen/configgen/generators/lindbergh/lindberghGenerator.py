from __future__ import annotations

import logging
import os
import re
import shutil
import stat
import tarfile
import lzma
import requests
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command, controllersConfig
from ...batoceraPaths import SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

_LINDBERGH_SAVES: Final = SAVES / "lindbergh"
DOWNLOADED_FLAG: Final = _LINDBERGH_SAVES / "downloaded.txt"
RAW_URL: Final = "https://raw.githubusercontent.com/batocera-linux/lindbergh-eeprom/main/lindbergh-eeprom.tar.xz"
DOWNLOAD_PATH: Final = _LINDBERGH_SAVES / "lindbergh-eeprom.tar.xz"

class LindberghGenerator(Generator):

    @staticmethod
    def download_file(url, destination):
        eslog.debug("Downloading the file...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(destination, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            eslog.debug(f"File downloaded to {destination}")
        else:
            raise Exception(f"Failed to download file. Status code: {response.status_code}")
            eslog.debug("Do you have internet!?")
    
    @staticmethod
    def extract_tar_xz(file_path, extract_to):
        eslog.debug("Extracting the file...")
        with tarfile.open(file_path, "r:xz") as tar:
            for member in tar.getmembers():
                file_path_to_extract = os.path.join(extract_to, member.name)
                if not os.path.exists(file_path_to_extract):
                    tar.extract(member, path=extract_to)
                else:
                    eslog.debug(f"Skipping {member.name}, file already exists.")
        eslog.debug(f"Files extracted to {extract_to}")

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "lindbergh-loader",
            "keys": {
                "Exit emulator": ["KEY_T"],
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Define mappings as tuples to preserve order
        lindberghCtrl = {
            "a":              ("BUTTON_2", "BTN_EAST"),
            "b":              ("BUTTON_1", "BTN_SOUTH"),
            "x":              ("BUTTON_4", "BTN_NORTH"),
            "y":              ("BUTTON_3", "BTN_WEST"),
            "start":          ("BUTTON_START", "BTN_START"),
            #"select":         ("BUTTON_SERVICE", "BTN_SELECT"),
            "up":             ("BUTTON_UP", "ABS_HAT0Y_MIN"),
            "down":           ("BUTTON_DOWN", "ABS_HAT0Y_MAX"),
            "left":           ("BUTTON_LEFT", "ABS_HAT0X_MIN"),
            "right":          ("BUTTON_RIGHT", "ABS_HAT0X_MAX"),
            "joystick1up":    ("ANALOGUE_2", "ABS_Y"),
            "joystick1left":  ("ANALOGUE_1", "ABS_X"),
            "pageup":         ("BUTTON_5", "BTN_TL"),
            "pagedown":       ("BUTTON_6", "BTN_TR"),
            "l2":             ("BUTTON_7", "BTN_TL2"),
            "r2":             ("BUTTON_8", "BTN_TR2")
        }

        romDir = Path(rom).parent
        romName = Path(rom).name
        eslog.debug(f"ROM path: {romDir}")
        _LINDBERGH_CONFIG_FILE = romDir / "lindbergh.conf"

        # Copy essential files into romDir if they're newer
        source_dir = Path("/usr/bin/lindbergh")
        files_to_copy = ["lindbergh", "lindbergh.so", "lindbergh.conf"]

        for file_name in files_to_copy:
            source_file = source_dir / file_name
            destination_file = romDir / file_name
            shutil.copy2(source_file, destination_file)
            eslog.debug(f"Updated {file_name}")
        
        # Setup eeprom files as necessary
        mkdir_if_not_exists(_LINDBERGH_SAVES)
        if not DOWNLOADED_FLAG.exists():
            try:
                # Download the file
                self.download_file(RAW_URL, str(DOWNLOAD_PATH))
                # Extract the file
                self.extract_tar_xz(str(DOWNLOAD_PATH), _LINDBERGH_SAVES)
                # Create the downloaded.txt flag file so we don't download again
                DOWNLOADED_FLAG.write_text("Download and extraction successful.\n")
                eslog.debug(f"Created flag file: {DOWNLOADED_FLAG}")

            except Exception as e:
                eslog.debug(f"An error occurred: {e}")
            finally:
                # Cleanup the downloaded .tar.xz file
                if DOWNLOAD_PATH.exists():
                    DOWNLOAD_PATH.unlink()
                    eslog.debug(f"Temporary file {DOWNLOAD_PATH} deleted.")

        # Read the configuration file
        with _LINDBERGH_CONFIG_FILE.open('r') as file:
            lines = file.readlines()

        modified_lines = []

        # Update WIDTH, HEIGHT, FULLSCREEN settings
        for line in lines:
            if line.strip().startswith("# WIDTH") or line.strip().startswith("WIDTH"):
                modified_lines.append(f"WIDTH {gameResolution['width']}\n")
            elif line.strip().startswith("# HEIGHT") or line.strip().startswith("HEIGHT"):
                modified_lines.append(f"HEIGHT {gameResolution['height']}\n")
            elif line.strip().startswith("# FULLSCREEN") or line.strip().startswith("FULLSCREEN"):
                modified_lines.append("FULLSCREEN 1\n")
            else:
                modified_lines.append(line)
                
        ## ES options ##

        # Handle freeplay option
        freeplay_value = "1" if system.isOptSet("lindbergh_freeplay") and system.getOptBoolean("lindbergh_freeplay") else "0"
        freeplay_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# FREEPLAY", "FREEPLAY")):
                modified_lines[i] = f"FREEPLAY {freeplay_value}\n"
                freeplay_replaced = True
                break

        if not freeplay_replaced:
            modified_lines.append(f"FREEPLAY {freeplay_value}\n")
        
        # Handle region option
        region_value = system.config["lindbergh_region"] if system.isOptSet("lindbergh_region") else "EX"
        region_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# REGION", "REGION")):
                modified_lines[i] = f"REGION {region_value}\n"
                region_replaced = True
                break

        if not region_replaced:
            modified_lines.append(f"REGION {region_value}\n")
        
        # Handle border option(s)
        border_value = "1" if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0 else "0"
        border_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# BORDER_ENABLED", "BORDER_ENABLED")):
                modified_lines[i] = f"BORDER_ENABLED {border_value}\n"
                border_replaced = True
                break

        if not border_replaced:
            modified_lines.append(f"BORDER_ENABLED {border_value}\n")
        
        if border_value == "1":
            for gun in guns:
                if guns[gun]["need_borders"]:
                    thickness_replaced = False
                    border_thickness = "1"
                    bordersSize = controllersConfig.gunsBordersSizeName(guns, system.config)
                    if bordersSize == "thin":
                        border_thickness = "1"
                    elif bordersSize == "medium":
                        border_thickness = "2"
                    else:
                        border_thickness = "3"
                    
                    for i, line in enumerate(modified_lines):
                        if line.strip().startswith(("# WHITE_BORDER_PERCENTAGE", "WHITE_BORDER_PERCENTAGE")):
                            modified_lines[i] = f"WHITE_BORDER_PERCENTAGE {border_thickness}\n"
                            thickness_replaced = True
                            break
                        
                    if not thickness_replaced:
                        modified_lines.append(f"WHITE_BORDER_PERCENTAGE {border_thickness}\n")
        
        # Handle the aspect ratio option
        aspect_value = "1" if system.isOptSet("lindbergh_aspect") and system.getOptBoolean("lindbergh_aspect") else "0"
        aspect_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# KEEP_ASPECT_RATIO", "KEEP_ASPECT_RATIO")):
                modified_lines[i] = f"KEEP_ASPECT_RATIO {aspect_value}\n"
                aspect_replaced = True
                break

        if not aspect_replaced:
            modified_lines.append(f"KEEP_ASPECT_RATIO {aspect_value}\n")
        
        # FPS limit option
        limit_value = "1" if system.isOptSet("lindbergh_limit") and system.getOptBoolean("lindbergh_limit") else "0"
        limit_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# FPS_LIMITER_ENABLED", "FPS_LIMITER_ENABLED")):
                modified_lines[i] = f"FPS_LIMITER_ENABLED {limit_value}\n"
                limit_replaced = True
                break

        if not limit_replaced:
            modified_lines.append(f"FPS_LIMITER_ENABLED {limit_value}\n")

        # FPS value option
        fps_value = system.config["lindbergh_fps"] if system.isOptSet("lindbergh_fps") else "60"
        fps_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# FPS_TARGET", "FPS_TARGET")):
                modified_lines[i] = f"FPS_TARGET {fps_value}\n"
                fps_replaced = True
                break

        if not fps_replaced:
            modified_lines.append(f"FPS_TARGET {fps_value}\n")

        # Debug logging option
        debug_value = "1" if system.isOptSet("lindbergh_debug") and system.getOptBoolean("lindbergh_debug") else "0"
        debug_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# DEBUG_MSGS", "DEBUG_MSGS")):
                modified_lines[i] = f"DEBUG_MSGS {debug_value}\n"
                debug_replaced = True
                break

        if not debug_replaced:
            modified_lines.append(f"DEBUG_MSGS {debug_value}\n")
        
        # Hummer flicker fix
        hummer_value = "1" if system.isOptSet("lindbergh_hummer") and system.getOptBoolean("lindbergh_hummer") else "0"
        hummer_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# HUMMER_FLICKER_FIX", "HUMMER_FLICKER_FIX")):
                modified_lines[i] = f"HUMMER_FLICKER_FIX {hummer_value}\n"
                hummer_replaced = True
                break

        if not hummer_replaced:
            modified_lines.append(f"HUMMER_FLICKER_FIX {hummer_value}\n")
        
        # Outrun lens glare
        lens_value = "1" if system.isOptSet("lindbergh_lens") and system.getOptBoolean("lindbergh_lens") else "0"
        lens_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# OUTRUN_LENS_GLARE_ENABLED", "OUTRUN_LENS_GLARE_ENABLED")):
                modified_lines[i] = f"OUTRUN_LENS_GLARE_ENABLED {lens_value}\n"
                lens_replaced = True
                break

        if not lens_replaced:
            modified_lines.append(f"OUTRUN_LENS_GLARE_ENABLED {lens_value}\n")
        
        # Not an ES option but to set automatically if the rom is OutRun
        outrun_value = "1" if "outrun" in romName.lower() or "outr2sdx" in romName.lower() else "0"
        outrun_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# SKIP_OUTRUN_CABINET_CHECK", "SKIP_OUTRUN_CABINET_CHECK")):
                modified_lines[i] = f"SKIP_OUTRUN_CABINET_CHECK {outrun_value}\n"
                outrun_replaced = True
                break

        if not outrun_replaced:
            modified_lines.append(f"SKIP_OUTRUN_CABINET_CHECK {outrun_value}\n")
        
        # eeprom.bin & sram.bin saves
        sram_replaced = False
        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# SRAM_PATH", "SRAM_PATH")):
                modified_lines[i] = f"SRAM_PATH {_LINDBERGH_SAVES}/sram.bin.{Path(romName).stem}\n"
                sram_replaced = True
                break

        if not sram_replaced:
            modified_lines.append(f"SRAM_PATH {_LINDBERGH_SAVES}/sram.bin.{Path(romName).stem}\n")
        
        eeprom_replaced = False
        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# EEPROM_PATH", "EEPROM_PATH")):
                modified_lines[i] = f"EEPROM_PATH {_LINDBERGH_SAVES}/eeprom.bin.{Path(romName).stem}\n"
                eeprom_replaced = True
                break

        if not eeprom_replaced:
            modified_lines.append(f"EEPROM_PATH {_LINDBERGH_SAVES}/eeprom.bin.{Path(romName).stem}\n")

        ## Controllers
        input_type = 1 # SDL controls only

        # Handle gun games by name until they're tagged accordingly
        if any(keyword in romName.lower() for keyword in ["spicy", "ghost", "gsevo", "jungle", "letsgoju", "hunt", "primevah", "rambo", "dead", "hotd"]):
            # Replace or append controller evdev configuration
            input_type = 0 # All controller modes
            nplayer = 1
            for playercontroller, pad in sorted(playersControllers.items()):
                # Handle two players / controllers only
                if nplayer <= 2:
                    controller_name = pad.real_name.upper().replace(" ", "_").replace("-", "_")
                    for input_name in pad.inputs:
                        if input_name in lindberghCtrl:
                            button_name, input_value = lindberghCtrl[input_name]

                            # Handle special case for joystick1up and joystick1left
                            if input_name in {"joystick1up", "joystick1left"}:
                                key_pattern = button_name
                            else:
                                key_pattern = f"PLAYER_{nplayer}_{button_name}"

                            line_pattern = re.compile(rf"^(#\s*)?{key_pattern}\s")

                            # Check if the line exists
                            replaced = False
                            for i, line in enumerate(modified_lines):
                                if line_pattern.match(line):
                                    modified_line = f"{key_pattern} {controller_name}_{input_value}\n"
                                    eslog.debug(f"Configured: {key_pattern} {controller_name}_{input_value}")
                                    modified_lines[i] = modified_line
                                    replaced = True
                                    break

                            if not replaced:
                                modified_line = f"{key_pattern} {controller_name}_{input_value}\n"
                                eslog.debug(f"Appended: {key_pattern} {controller_name}_{input_value}")
                                modified_lines.append(modified_line)
                    nplayer += 1
        
        input_replaced = False

        for i, line in enumerate(modified_lines):
            if line.strip().startswith(("# INPUT_MODE", "INPUT_MODE")):
                modified_lines[i] = f"INPUT_MODE {input_type}\n"
                input_replaced = True
                break
        
        if not input_replaced:
            modified_lines.append(f"INPUT_MODE {input_type}\n")
        
        # Write back the modified configuration
        with _LINDBERGH_CONFIG_FILE.open('w') as file:
            file.writelines(modified_lines)
        
        # Setup some library quirks for GPU support (NVIDIA?)
        source = Path("/lib32/libkswapapi.so")
        if source.exists():
            destination = Path(romDir) / "libGLcore.so.1"
            if not destination.exists():
                shutil.copy2(source, destination)
                eslog.debug(f"Copied: {destination} from {source}")
        
        # -= Game specific library versions =-
        if any(keyword in romName.lower() for keyword in ("harley", "hdkotr", "spicy", "rambo", "hotdex", "dead ex")):
            destCg = Path(romDir) / "libCg.so"
            destCgGL = Path(romDir) / "libCgGL.so"
            if not destCg.exists():
                shutil.copy2("/lib32/extralibs/libCg.so.harley", destCg)
                eslog.debug(f"Copied: {destCg}")
            if not destCgGL.exists():
                shutil.copy2("/lib32/extralibs/libCgGL.so.other", destCgGL)
                eslog.debug(f"Copied: {destCgGL}")
        
        if "stage 4" in romName.lower() or "initiad4" in romName.lower():
            destination = Path(romDir) / "libCgGL.so"
            if not destination.exists():
                shutil.copy2("/lib32/extralibs/libCgGL.so.other", destination)
                eslog.debug(f"Copied: {destination}")

        if "tennis" in romName.lower():
            destCg = Path(romDir) / "libCg.so"
            destCgGL = Path(romDir) / "libCgGL.so"
            if not destCg.exists():
                shutil.copy2("/lib32/extralibs/libCg.so.tennis", destCg)
                eslog.debug(f"Copied: {destCg}")
            if not destCgGL.exists():
                shutil.copy2("/lib32/extralibs/libCgGL.so.tennis", destCgGL)
                eslog.debug(f"Copied: {destCgGL}")
        
        # Change to the ROM path before launching
        os.chdir(romDir)

        # remove any legacy libsegaapi.so
        if Path(romDir, "libsegaapi.so").exists():
            Path(romDir, "libsegaapi.so").unlink()
            eslog.debug(f"Removed: {romDir}/libsegaapi.so")

        # Check for known executable files and make them executable if needed
        # Details in the Lindbergh.c file
        executable_files = [
            "main.exe", "ramboM.elf", "vt3_Lindbergh", "hummer_Master.elf",
            "drive.elf", "chopperM.elf", "vsg", "Jennifer", "dsr", "abc",
            "hod4M.elf", "lgj_final", "vt3", "id4.elf", "id5.elf",
            "lgjsp_app", "gsevo", "vf5", "apacheM.elf", "hodexRI.elf", "a.elf"
        ]

        for exe_file in executable_files:
            file_path = romDir / exe_file
            if file_path.exists():
                # Check if file is executable
                if not os.access(file_path, os.X_OK):
                    # Add executable permission (equivalent to chmod +x)
                    current_permissions = file_path.stat().st_mode
                    executable_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                    file_path.chmod(executable_permissions)
                    eslog.debug(f"Made {exe_file} executable")

        # Run command
        if system.isOptSet("lindbergh_test") and system.getOptBoolean("lindbergh_test"):
            commandArray: list[str | Path] = [str(romDir / "lindbergh"), "-t"]
        else:
            commandArray: list[str | Path] = [str(romDir / "lindbergh")]

        return Command.Command(
            array=commandArray,
            env={
                # Libraries
                "LD_LIBRARY_PATH": "/lib32:/lib32/extralibs:/lib:/usr/lib:" + str(romDir),
                # Graphics
                "GST_PLUGIN_SYSTEM_PATH_1_0": "/lib32/gstreamer-1.0:/usr/lib/gstreamer-1.0",
                "GST_REGISTRY_1_0": "/userdata/system/.cache/gstreamer-1.0/registry..bin:/userdata/system/.cache/gstreamer-1.0/registry.x86_64.bin",
                "LIBGL_DRIVERS_PATH": "/lib32/dri:/usr/lib/dri",
                # Audio
                "SPA_PLUGIN_DIR": "/lib32/spa-0.2:/usr/lib/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/lib32/pipewire-0.3:/usr/lib/pipewire-0.3",
                # Controller(s)
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
