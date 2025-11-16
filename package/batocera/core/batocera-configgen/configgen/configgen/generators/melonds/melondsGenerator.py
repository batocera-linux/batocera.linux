from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import toml

from ... import Command
from ...batoceraPaths import BIOS, CHEATS, CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import Controller
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
            with configFileName.open() as toml_file:
                config = toml.load(toml_file)
        else:
            config = {}

        # Define base configuration
        base_config: dict[str, Any] = {
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
                },
                "Window1": {
                    "Enabled": False,
                    "ScreenRotation": 0,
                    "ScreenSwap": False,
                    "ScreenLayout": 0,
                    "ScreenSizing": 5,
                    "IntegerScaling": 0
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
        if "melonds_renderer" in system.config:
            base_config["3D"]["Renderer"] = system.config.get_int("melonds_renderer")

        if vsync := system.config.get("melonds_vsync"):
            base_config["Screen"]["VSync"] = vsync
            base_config["Screen"]["VSyncInterval"] = 1

        # Cheater! Enable cheats if the option is set
        base_config["Instance0"]["EnableCheats"] = system.config.get("melonds_cheats", False)

        # Framerate
        base_config["LimitFPS"] = system.config.get("melonds_framerate", True)

        # Resolution
        if (resolution := system.config.get_int("melonds_resolution")) is not system.config.MISSING:
            base_config["3D"]["GL"]["ScaleFactor"] = resolution
            base_config["3D"]["GL"]["HiresCoordinates"] = resolution == 2

        # Polygons
        if polygons := system.config.get("melonds_polygons"):
            base_config["3D"]["GL"]["BetterPolygons"] = polygons

        # OSD
        base_config["Instance0"]["Window0"]["ShowOSD"] = system.config.get("melonds_osd", False)

        # Console
        base_config["Emu"]["ConsoleType"] = system.config.get_int("melonds_console", 0)
        
        # Check if dual screen mode is enabled
        is_dual_screen_enabled = system.config.get("melonds_dual_screen", False)

        if is_dual_screen_enabled:
            # Force specific settings for dual screen mode for optimal layout
            # Window0 (Top Screen)
            base_config["Instance0"]["Window0"]["ScreenRotation"] = 0
            base_config["Instance0"]["Window0"]["ScreenSwap"] = False
            base_config["Instance0"]["Window0"]["ScreenLayout"] = 0
            base_config["Instance0"]["Window0"]["ScreenSizing"] = 4
            
            # Window1 (Bottom Screen)
            base_config["Instance0"]["Window1"]["Enabled"] = True
            base_config["Instance0"]["Window1"]["ScreenRotation"] = 0
            base_config["Instance0"]["Window1"]["ScreenSwap"] = False
            base_config["Instance0"]["Window1"]["ScreenLayout"] = 0
            base_config["Instance0"]["Window1"]["ScreenSizing"] = 5
            
            # Sync IntegerScaling from Window0 to Window1
            window0_scaling = system.config.get("melonds_scaling", 0)
            base_config["Instance0"]["Window0"]["IntegerScaling"] = window0_scaling
            base_config["Instance0"]["Window1"]["IntegerScaling"] = window0_scaling
        else:
            # Apply standard user settings if dual screen is off
            base_config["Instance0"]["Window1"]["Enabled"] = False
            base_config["Instance0"]["Window0"]["ScreenRotation"] = system.config.get_int("melonds_rotation", 0)
            base_config["Instance0"]["Window0"]["ScreenSwap"] = system.config.get("melonds_screenswap", False)
            base_config["Instance0"]["Window0"]["ScreenLayout"] = system.config.get_int("melonds_layout", 0)
            base_config["Instance0"]["Window0"]["ScreenSizing"] = system.config.get_int("melonds_screensizing", 0)
            base_config["Instance0"]["Window0"]["IntegerScaling"] = system.config.get("melonds_scaling", 0)

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
        # Only use Player 1 controls
        if pad := Controller.find_player_number(playersControllers, 1):
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
        with configFileName.open("w") as toml_file:
            toml.dump(config, toml_file)

        commandArray = ["/usr/bin/melonDS", "-f", rom]
        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_DATA_HOME": SAVES
            }
        )
