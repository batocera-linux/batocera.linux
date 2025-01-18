from __future__ import annotations

import logging
import os
import re
import shutil
import stat
import tarfile
import requests
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command, controllersConfig
from ...batoceraPaths import SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator
from ...utils import bezels as bezelsUtil

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

class LindberghGenerator(Generator):
    LINDBERGH_SAVES: Final = SAVES / "lindbergh"

    CONF_KEYS = {
        "WIDTH":                     True, "HEIGHT":                    True, "FULLSCREEN":                True, "INPUT_MODE":                True,
        "NO_SDL":                    True, "REGION":                    True, "FREEPLAY":                  True, "EMULATE_JVS":               True,
        "EMULATE_RIDEBOARD":         True, "EMULATE_DRIVEBOARD":        True, "EMULATE_MOTIONBOARD":       True, "JVS_PATH":                  True,
        "SERIAL_1_PATH":             True, "SERIAL_2_PATH":             True, "SRAM_PATH":                 True, "EEPROM_PATH":               True,
        "GPU_VENDOR":                True, "DEBUG_MSGS":                True, "BORDER_ENABLED":            True, "WHITE_BORDER_PERCENTAGE":   True,
        "BLACK_BORDER_PERCENTAGE":   True, "HUMMER_FLICKER_FIX":        True, "KEEP_ASPECT_RATIO":         True, "OUTRUN_LENS_GLARE_ENABLED": True,
        "SKIP_OUTRUN_CABINET_CHECK": True, "FPS_LIMITER_ENABLED":       True, "FPS_TARGET":                True, "LGJ_RENDER_WITH_MESA":      True,
        "PRIMEVAL_HUNT_MODE":        True, "MJ4_ENABLED_ALL_THE_TIME":  True, "LINDBERGH_COLOUR":          True, "TEST_KEY":                  True,
        "PLAYER_1_START_KEY":        True, "PLAYER_1_SERVICE_KEY":      True, "PLAYER_1_COIN_KEY":         True, "PLAYER_1_UP_KEY":           True,
        "PLAYER_1_DOWN_KEY":         True, "PLAYER_1_LEFT_KEY":         True, "PLAYER_1_RIGHT_KEY":        True, "PLAYER_1_BUTTON_1_KEY":     True,
        "PLAYER_1_BUTTON_2_KEY":     True, "PLAYER_1_BUTTON_3_KEY":     True, "PLAYER_1_BUTTON_4_KEY":     True, "TEST_BUTTON":               True,
        "PLAYER_1_BUTTON_START":     True, "PLAYER_1_BUTTON_SERVICE":   True, "PLAYER_1_BUTTON_UP":        True, "PLAYER_1_BUTTON_DOWN":      True,
        "PLAYER_1_BUTTON_LEFT":      True, "PLAYER_1_BUTTON_RIGHT":     True, "PLAYER_1_BUTTON_1":         True, "PLAYER_1_BUTTON_2":         True,
        "PLAYER_1_BUTTON_3":         True, "PLAYER_1_BUTTON_4":         True, "PLAYER_1_BUTTON_5":         True, "PLAYER_1_BUTTON_6":         True,
        "PLAYER_1_BUTTON_7":         True, "PLAYER_1_BUTTON_8":         True, "PLAYER_2_BUTTON_START":     True, "PLAYER_2_BUTTON_SERVICE":   True,
        "PLAYER_2_BUTTON_UP":        True, "PLAYER_2_BUTTON_DOWN":      True, "PLAYER_2_BUTTON_LEFT":      True, "PLAYER_2_BUTTON_RIGHT":     True,
        "PLAYER_2_BUTTON_1":         True, "PLAYER_2_BUTTON_2":         True, "PLAYER_2_BUTTON_3":         True, "PLAYER_2_BUTTON_4":         True,
        "PLAYER_2_BUTTON_5":         True, "PLAYER_2_BUTTON_6":         True, "PLAYER_2_BUTTON_7":         True, "PLAYER_2_BUTTON_8":         True,
        "ANALOGUE_1":                True, "ANALOGUE_2":                True, "ANALOGUE_3":                True, "ANALOGUE_4":                True,
        "ANALOGUE_DEADZONE_1":       True, "ANALOGUE_DEADZONE_2":       True, "ANALOGUE_DEADZONE_3":       True, "ANALOGUE_DEADZONE_4":       True,
        "ANALOGUE_DEADZONE_5":       True, "ANALOGUE_DEADZONE_6":       True, "ANALOGUE_DEADZONE_7":       True, "ANALOGUE_DEADZONE_8":       True
    }

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "lindbergh loader",
            #"keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "coin": "KEY_5" }
            "keys": { "exit": "KEY_T", "coin": "KEY_5" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        romDir = Path(rom).parent
        romName = Path(rom).name
        eslog.debug(f"ROM path: {romDir}")

        source_dir = Path("/usr/bin/lindbergh")

        ### target to romdir
        for file_name in ["lindbergh", "lindbergh.so"]:
            source_file = source_dir / file_name
            destination_file = romDir / file_name
            if not destination_file.exists() or source_file.stat().st_mtime > destination_file.stat().st_mtime:
                shutil.copy2(source_file, destination_file)
                eslog.debug(f"Updated {file_name}")

        ### Setup eeprom files as necessary
        self.setup_eeprom()

        ### conf file
        self.setup_config(source_dir, system, gameResolution, guns, playersControllers, romDir, romName)

        ### libraries
        self.setup_libraries(romDir, romName)

        # Change to the ROM path before launching
        os.chdir(romDir)

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

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9

    def loadConf(self, configFile):
        try:
            with configFile.open('r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            eslog.debug(f"Configuration file {configFile} not found.")
            lines = []
        
        conf = { "raw": lines, "keys": {}}

        # find keys and values
        pattern = re.compile(r"^\s*(#?)\s*([A-Z0-9_]+)\s(.*)$")

        # analyze lines
        n = 0
        for line in lines:
            matches = pattern.match(line)
            if matches:
                key = matches.group(2)

                if key in self.CONF_KEYS:
                    conf["keys"][key] = { "value":     matches.group(3).strip(),
                                          "commented": True if matches.group(1) == "#" else False,
                                          "line":      n,
                                          "modified":  False
                                         }
                else:
                    print(f"CONF: ignoring key /{key}/")
            else:
                strippedLine = line.rstrip();
                if strippedLine != "":
                    print(f"CONF: ignoring line {strippedLine}")
            n += 1
        return conf

    def setConf(self, conf, key, value):
        if key not in self.CONF_KEYS:
            raise Exception(f"unknown conf key {key}")
        conf["keys"][key]["value"]     = str(value)
        conf["keys"][key]["modified"]  = True
        conf["keys"][key]["commented"] = False

    def saveConf(self, conf, targetFile):
        # update with modified lines
        for key in conf["keys"]:
            if conf["keys"][key]["modified"]:
                nline = conf["keys"][key]["line"]
                line = key + " " + conf["keys"][key]["value"] + "\n"
                if conf["keys"][key]["commented"]:
                    line = "# " + line
                conf["raw"][nline] = line

        try:
            with targetFile.open('w') as file:
                file.writelines(conf["raw"])
            eslog.debug(f"Configuration file {targetFile} updated successfully.")
        except Exception as e:
            eslog.debug(f"Error updating configuration file: {e}")

    def buildConfFile(self, conf, system, gameResolution, guns, playersControllers, romName):
        self.setConf(conf, "WIDTH",                     gameResolution['width'])
        self.setConf(conf, "HEIGHT",                    gameResolution['height'])
        self.setConf(conf, "FULLSCREEN",                1)
        self.setConf(conf, "REGION",                    system.config["lindbergh_region"] if system.isOptSet("lindbergh_region") else "EX")
        self.setConf(conf, "FPS_TARGET",                system.config["lindbergh_fps"]    if system.isOptSet("lindbergh_fps")    else "60")
        self.setConf(conf, "FPS_LIMITER_ENABLED",       1 if system.isOptSet("lindbergh_limit")    and system.getOptBoolean("lindbergh_limit")            else 0)
        self.setConf(conf, "FREEPLAY",                  1 if system.isOptSet("lindbergh_freeplay") and system.getOptBoolean("lindbergh_freeplay")         else 0)
        self.setConf(conf, "KEEP_ASPECT_RATIO",         1 if system.isOptSet("lindbergh_aspect")   and system.getOptBoolean("lindbergh_aspect")           else 0)
        self.setConf(conf, "DEBUG_MSGS",                1 if system.isOptSet("lindbergh_debug")    and system.getOptBoolean("lindbergh_debug")            else 0)
        self.setConf(conf, "HUMMER_FLICKER_FIX",        1 if system.isOptSet("lindbergh_hummer")   and system.getOptBoolean("lindbergh_hummer")           else 0)
        self.setConf(conf, "OUTRUN_LENS_GLARE_ENABLED", 1 if system.isOptSet("lindbergh_lens")     and system.getOptBoolean("lindbergh_lens")             else 0)
        self.setConf(conf, "SKIP_OUTRUN_CABINET_CHECK", 1 if "outrun" in romName.lower() or "outr2sdx" in romName.lower() else 0)
        self.setConf(conf, "SRAM_PATH",   f"{self.LINDBERGH_SAVES}/sram.bin.{Path(romName).stem}")
        self.setConf(conf, "EEPROM_PATH", f"{self.LINDBERGH_SAVES}/eeprom.bin.{Path(romName).stem}")

        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
            need_guns_border = False
            for gun in guns:
                if guns[gun]["need_borders"]:
                    need_guns_border = True
            if need_guns_border:
                bordersSize = controllersConfig.gunsBordersSizeName(guns, system.config)
                bordersInnerSize, bordersOuterSize = bezelsUtil.gunBordersSize(bordersSize)
                self.setConf(conf, "WHITE_BORDER_PERCENTAGE", bordersInnerSize)
                self.setConf(conf, "BLACK_BORDER_PERCENTAGE", bordersOuterSize)
            self.setConf(conf, "BORDER_ENABLED", 1 if need_guns_border else 0)
        else:
            self.setConf(conf, "BORDER_ENABLED", 0)

        self.setup_controllers(conf, playersControllers)

    def setup_controllers(self, conf, playersControllers):
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

        self.setConf(conf, "INPUT_MODE", 0)

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

                        self.setConf(conf, key_pattern, f"{controller_name}_{input_value}")
                nplayer += 1

    def setup_eeprom(self):
        DOWNLOAD_PATH: Final = self.LINDBERGH_SAVES / "lindbergh-eeprom.tar.xz"
        DOWNLOADED_FLAG: Final = self.LINDBERGH_SAVES / "downloaded.txt"
        RAW_URL: Final = "https://raw.githubusercontent.com/batocera-linux/lindbergh-eeprom/main/lindbergh-eeprom.tar.xz"

        mkdir_if_not_exists(self.LINDBERGH_SAVES)
        if not DOWNLOADED_FLAG.exists():
            try:
                # Download the file
                self.download_file(RAW_URL, str(DOWNLOAD_PATH))
                # Extract the file
                self.extract_tar_xz(str(DOWNLOAD_PATH), self.LINDBERGH_SAVES)
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

    def setup_libraries(self, romDir, romName):
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

        # remove any legacy libsegaapi.so
        if Path(romDir, "libsegaapi.so").exists():
            Path(romDir, "libsegaapi.so").unlink()
            eslog.debug(f"Removed: {romDir}/libsegaapi.so")

    def setup_config(self, source_dir, system, gameResolution, guns, playersControllers, romDir, romName):
        LINDBERGH_CONFIG_FILE = Path("/userdata/system/configs/lindbergh/lindbergh.conf")
        mkdir_if_not_exists(LINDBERGH_CONFIG_FILE.parent)

        # get an initial version if no version is here
        source_file = source_dir / "lindbergh.conf"
        if not LINDBERGH_CONFIG_FILE.exists() or source_file.stat().st_mtime > LINDBERGH_CONFIG_FILE.stat().st_mtime:
            shutil.copy2(source_file, LINDBERGH_CONFIG_FILE)
            eslog.debug(f"Updated lindbergh.conf")

        # load and modify it if needed and save it
        conf = self.loadConf(LINDBERGH_CONFIG_FILE)
        self.buildConfFile(conf, system, gameResolution, guns, playersControllers, romName)
        self.saveConf(conf, LINDBERGH_CONFIG_FILE)

        # copy the config file in the rom dir, where it is used
        shutil.copy2(LINDBERGH_CONFIG_FILE, romDir / "lindbergh.conf")
