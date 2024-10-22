from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ... import Command
import toml
from ...batoceraPaths import BIOS, CHEATS, CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_MELONDS_SAVES: Final = SAVES / "nds"
_MELONDS_ROMS: Final = ROMS / "nds"
_MELONDS_CHEATS: Final = CHEATS / "melonDS"
_MELONDS_CONFIG: Final = CONFIGS / "melonDS"

class MelonDSGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "melonds",
            "keys": {"exit": ["KEY_LEFTALT", "KEY_F4"]}
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Verify paths
        mkdir_if_not_exists(_MELONDS_SAVES)
        mkdir_if_not_exists(_MELONDS_CHEATS)
        mkdir_if_not_exists(_MELONDS_CONFIG)

        # Config file path
        configFileName = _MELONDS_CONFIG / "melonDS.toml"
        
        # Load existing config if file exists
        if configFileName.exists():
            with open(configFileName, "r") as toml_file:
                config = toml.load(toml_file)
        else:
            config = {}

        # Define base configuration
        base_config = {
            "MouseHide": False,
            "LastBIOSFolder": str(BIOS),
            "PauseLostFocus": False,
            "LastROMFolder": str(_MELONDS_ROMS),
            "SavestatePath": str(_MELONDS_SAVES),
            "CheatFilePath": str(_MELONDS_CHEATS),
            "SaveFilePath": str(_MELONDS_SAVES),
            "MouseHideSeconds": 5,
            "DS": {
                "FirmwarePath": str(BIOS / "firmware.bin"),
                "BIOS7Path": str(BIOS / "bios7.bin"),
                "BIOS9Path": str(BIOS / "bios9.bin")
            },
            "DLDI": {
                "FolderPath": str(_MELONDS_SAVES),
                "ImagePath": "dldi.bin",
                "Enable": True
            },
            "DSi": {
                "FullBIOSBoot": False,
                "FirmwarePath": str(BIOS / "dsi_firmware.bin"),
                "BIOS9Path": str(BIOS / "bios9.bin"),
                "BIOS7Path": str(BIOS / "bios7.bin"),
                "NANDPath": str(BIOS / "dsi_nand.bin"),
                "SD": {
                    "FolderPath": str(_MELONDS_SAVES),
                    "ImagePath": "dsisd.bin",
                    "Enable": True
                }
            },
            "Emu": {
                "DirectBoot": True,
                "ExternalBIOSEnable": True
            },
            "Instance0": {
                "Joystick": {},
                "Window0": {
                    "ScreenRotation": 0,
                    "ScreenSwap": False,
                    "ScreenLayout": 0,
                    "ScreenSizing": 0,
                    "IntegerScaling": 0,
                    "ShowOSD": False
                }
            },
            "3D": {
                "Renderer": 1,
                "GL": {
                    "ScaleFactor": 5,
                    "BetterPolygons": False
                }
            },
            "Screen": {
                "VSync": False
            }
        }

        ## User selected options

        # Override Renderer if system option is set
        if system.isOptSet("melonds_renderer"):
            base_config["3D"]["Renderer"] = int(system.config["melonds_renderer"])
        
        if system.isOptSet("melonds_vsync"):
            base_config["Screen"]["VSync"] = system.config["melonds_vsync"]
            base_config["Screen"]["VSyncInterval"] = 1
        
        # Cheater! Enable cheats if the option is set
        if system.isOptSet("melonds_cheats"):
            base_config["Instance0"]["EnableCheats"] = system.config["melonds_cheats"]
        else:
            base_config["Instance0"]["EnableCheats"] = False
        
        # Framerate
        if system.isOptSet("melonds_framerate"):
            base_config["LimitFPS"] = system.config["melonds_framerate"]
        else:
            base_config["LimitFPS"] = True
        
        # Resolution
        if system.isOptSet("melonds_resolution"):
            base_config["3D"]["GL"]["ScaleFactor"] = int(system.config["melonds_resolution"])
            if system.config["melonds_resolution"] == "2":
                base_config["3D"]["GL"]["HiresCoordinates"] = True
            else:
                base_config["3D"]["GL"]["HiresCoordinates"] = False
        
        # Polygons
        if system.isOptSet("melonds_polygons"):
            base_config["3D"]["GL"]["BetterPolygons"] = system.config["melonds_polygons"]
        
        # Rotation
        if system.isOptSet("melonds_rotation"):
            base_config["Instance0"]["Window0"]["ScreenRotation"] = int(system.config["melonds_rotation"])
        else:
            base_config["Instance0"]["Window0"]["ScreenRotation"] = 0

        # Screen Swap
        if system.isOptSet("melonds_screenswap"):
            base_config["Instance0"]["Window0"]["ScreenSwap"] = system.config["melonds_screenswap"]
        else:
            base_config["Instance0"]["Window0"]["ScreenSwap"] = False

        # Screen Layout
        if system.isOptSet("melonds_layout"):
            base_config["Instance0"]["Window0"]["ScreenLayout"] = int(system.config["melonds_layout"])
        else:
            base_config["Instance0"]["Window0"]["ScreenLayout"] = 0
        
        # Screen Sizing
        if system.isOptSet("melonds_screensizing"):
            base_config["Instance0"]["Window0"]["ScreenSizing"] = int(system.config["melonds_screensizing"])
        else:
            base_config["Instance0"]["Window0"]["ScreenSizing"] = 0
        
        # Integer Scaling
        if system.isOptSet("melonds_scaling"):
            base_config["Instance0"]["Window0"]["IntegerScaling"] = system.config["melonds_scaling"]
        else:
            base_config["Instance0"]["Window0"]["IntegerScaling"] = 0
        
        # OSD
        if system.isOptSet("melonds_osd"):
            base_config["Instance0"]["Window0"]["ShowOSD"] = system.config["melonds_osd"]
        else:
            base_config["Instance0"]["Window0"]["ShowOSD"] = False
        
        # Console
        if system.isOptSet("melonds_console"):
            base_config["Emu"]["ConsoleType"] = int(system.config["melonds_console"])
        else:
            base_config["Emu"]["ConsoleType"] = 0

        # Map controllers
        melonDSMapping = {
            "a":        "A",
            "b":        "B",
            "select":   "Select",
            "start":    "Start",
            "right":    "Right",
            "left":     "Left",
            "up":       "Up",
            "down":     "Down",
            "pagedown": "R",
            "pageup":   "L",
            "x":        "X",
            "y":        "Y"
        }
        
        val = -1
        for controller, pad in sorted(playersControllers.items()):
            # Only use Player 1 controls
            if pad.player_number != 1:
                continue
            for index in pad.inputs:
                input = pad.inputs[index]
                if input.name not in melonDSMapping:
                    continue
                option = melonDSMapping[input.name]
                # Workaround - SDL numbers?
                val = input.id
                if val == "0":
                    if option == "Up":
                        val = 257
                    elif option == "Down":
                        val = 260
                    elif option == "Left":
                        val = 264
                    elif option == "Right":
                        val = 258
                base_config["Instance0"]["Joystick"][option] = int(val)

        # Update base_config with any existing values
        config.update(base_config)

        # Write updated configuration back to the file
        with open(configFileName, "w") as toml_file:
            toml.dump(config, toml_file)

        commandArray = ["/usr/bin/melonDS", "-f", rom]
        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_DATA_HOME": SAVES,
                "QT_QPA_PLATFORM": "xcb"
            }
        )
