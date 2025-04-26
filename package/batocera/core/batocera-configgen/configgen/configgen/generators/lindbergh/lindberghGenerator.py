#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
from __future__ import annotations

import logging
import os
import re
import shutil
import socket
import stat
import subprocess
import tarfile
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, ClassVar, Final, Literal

from evdev import ecodes

from ... import Command
from ...batoceraPaths import SAVES, mkdir_if_not_exists
from ...controller import Controller, Controllers, generate_sdl_game_controller_config
from ...exceptions import BatoceraException, InvalidConfiguration
from ...utils import bezels as bezelsUtil, hotkeygen
from ...utils.download import download
from ..Generator import Generator

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...gun import Guns
    from ...types import DeviceInfoMapping, HotkeysContext, Resolution

_logger = logging.getLogger(__name__)

class LindberghGenerator(Generator):
    LINDBERGH_SAVES: Final = SAVES / "lindbergh"

    CONF_KEYS: ClassVar = {
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
        "ANALOGUE_5":                True, "ANALOGUE_6":                True, "ANALOGUE_7":                True, "ANALOGUE_8":                True,
        "ANALOGUE_1+":               True, "ANALOGUE_2+":               True, "ANALOGUE_3+":               True, "ANALOGUE_4+":               True,
        "ANALOGUE_1-":               True, "ANALOGUE_2-":               True, "ANALOGUE_3-":               True, "ANALOGUE_4-":               True,
        "ANALOGUE_DEADZONE_1":       True, "ANALOGUE_DEADZONE_2":       True, "ANALOGUE_DEADZONE_3":       True, "ANALOGUE_DEADZONE_4":       True,
        "ANALOGUE_DEADZONE_5":       True, "ANALOGUE_DEADZONE_6":       True, "ANALOGUE_DEADZONE_7":       True, "ANALOGUE_DEADZONE_8":       True,
        "EMULATE_CARDREADER":        True, "CARDFILE_01":               True, "CARDFILE_02":               True, "CPU_FREQ_GHZ":              True,
        "OR2_IP":                    True, "PLAYER_1_COIN":             True, "BOOST_RENDER_RES":          True,
    }

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "lindbergh loader",
            "keys": { "exit": "KEY_T", "coin": "KEY_5" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        romDir = rom.parent
        romName = rom.name
        _logger.debug("ROM path: %s", romDir)

        source_dir = Path("/usr/bin/lindbergh")

        ### target to romdir
        for file_name in ["lindbergh", "lindbergh.so"]:
            source_file = source_dir / file_name
            destination_file = romDir / file_name
            if not destination_file.exists() or source_file.stat().st_mtime > destination_file.stat().st_mtime:
                shutil.copy2(source_file, destination_file)
                _logger.debug("Updated %s", file_name)

        ### Setup eeprom files as necessary
        self.setup_eeprom()

        ### conf file
        self.setup_config(source_dir, system, gameResolution, guns, wheels, playersControllers, romDir, romName)

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
            # Check if file is executable
            if file_path.exists() and not os.access(file_path, os.X_OK):
                # Add executable permission (equivalent to chmod +x)
                current_permissions = file_path.stat().st_mode
                executable_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                file_path.chmod(executable_permissions)
                _logger.debug("Made %s executable", exe_file)

        environment={
                # Libraries
                "LD_LIBRARY_PATH": f"/lib32:/lib32/extralibs:/lib:/usr/lib:{romDir}",
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

        if system.config.get_bool("lindbergh_zink"):
            environment.update(
                {
                    "MESA_LOADER_DRIVER_OVERRIDE": "zink"
                }
            )

        # Run command
        if system.config.get_bool("lindbergh_test"):
            commandArray: list[str | Path] = [str(romDir / "lindbergh"), "-t"]
        else:
            commandArray: list[str | Path] = [str(romDir / "lindbergh")]

        return Command.Command(array=commandArray, env=environment)

    @staticmethod
    def extract_tar_xz(file_path: IO[bytes], extract_to: Path) -> None:
        _logger.debug("Extracting the file...")
        with tarfile.open(fileobj=file_path, mode="r:xz") as tar:
            for member in tar.getmembers():
                file_path_to_extract = extract_to / member.name
                if not file_path_to_extract.exists():
                    tar.extract(member, path=extract_to)
                else:
                    _logger.debug("Skipping %s, file already exists.", member.name)
        _logger.debug("Files extracted to %s", extract_to)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9

    def loadConf(self, configFile: Path, /) -> dict[str, Any]:
        try:
            with configFile.open('r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            _logger.debug("Configuration file %s not found.", configFile)
            lines = []

        conf: dict[str, Any] = { "raw": lines, "keys": {}}

        # find keys and values
        pattern = re.compile(r"^\s*(#?)\s*([A-Z0-9_]+)\s(.*)$")

        # analyze lines
        for n, line in enumerate(lines):
            matches = pattern.match(line)
            if matches:
                key = matches.group(2)

                if key in self.CONF_KEYS:
                    if key in conf["keys"]: # take care of duplicated keys
                        # if the 1st one is commented, prefer the last one
                        if conf["keys"][key]["commented"]:
                            conf["keys"][key] = { "value":     matches.group(3).strip(),
                                                  "commented": matches.group(1) == "#",
                                                  "line":      n,
                                                  "modified":  False
                                                 }
                        else:
                            # if the previous is not commented, prefer the last one if not commented and comment the previous
                            if matches.group(1) != "#":
                                lines[conf["keys"][key]["line"]] = f'# {lines[conf["keys"][key]["line"]]}'
                                conf["keys"][key] = { "value":     matches.group(3).strip(),
                                                      "commented": matches.group(1) == "#",
                                                      "line":      n,
                                                      "modified":  False
                                                     }
                    else:
                        conf["keys"][key] = { "value":     matches.group(3).strip(),
                                              "commented": matches.group(1) == "#",
                                              "line":      n,
                                              "modified":  False
                                             }
                else:
                    print(f"CONF: ignoring key /{key}/")
            else:
                strippedLine = line.rstrip()
                if strippedLine != "":
                    print(f"CONF: ignoring line {strippedLine}")

        return conf

    def setConf(self, conf: dict[str, Any], key: str, value: Any, /) -> None:
        if key not in self.CONF_KEYS:
            raise InvalidConfiguration(f"unknown conf key {key}")

        # new line
        if key not in conf["keys"]:
            conf["keys"][key] = { "line": len(conf["raw"]) }
            conf["raw"].append("###")

        conf["keys"][key]["value"]     = str(value)
        conf["keys"][key]["modified"]  = True
        conf["keys"][key]["commented"] = False

    def commentConf(self, conf: dict[str, Any], key: str, /) -> None:
        if key not in self.CONF_KEYS:
            raise InvalidConfiguration(f"unknown conf key {key}")

        if key in conf["keys"]:
            conf["keys"][key]["modified"]  = True
            conf["keys"][key]["commented"] = True

    def saveConf(self, conf: dict[str, Any], targetFile: Path, /) -> None:
        # update with modified lines
        for key in conf["keys"]:
            if conf["keys"][key]["modified"]:
                nline = conf["keys"][key]["line"]
                line = f'{key} {conf["keys"][key]["value"]}\n'
                if conf["keys"][key]["commented"]:
                    line = f"# {line}"
                conf["raw"][nline] = line

        try:
            with targetFile.open('w') as file:
                file.writelines(conf["raw"])
            _logger.debug("Configuration file %s updated successfully.", targetFile)
        except Exception as e:
            _logger.debug("Error updating configuration file: %s", e)

    def buildConfFile(
        self,
        conf: dict[str, Any],
        system: Emulator,
        gameResolution: Resolution,
        guns: Guns,
        wheels: DeviceInfoMapping,
        playersControllers: Controllers,
        romName: str,
        /,
    ) -> None:
        self.setConf(conf, "WIDTH",                     gameResolution['width'])
        self.setConf(conf, "HEIGHT",                    gameResolution['height'])
        self.setConf(conf, "FULLSCREEN",                1)
        self.setConf(conf, "REGION",                    system.config.get("lindbergh_region", "EX"))
        self.setConf(conf, "FPS_TARGET",                system.config.get("lindbergh_fps", "60"))
        self.setConf(conf, "FPS_LIMITER_ENABLED",       system.config.get_bool("lindbergh_limit", return_values=(1, 0)))
        self.setConf(conf, "FREEPLAY",                  system.config.get_bool("lindbergh_freeplay", return_values=(1, 0)))
        self.setConf(conf, "KEEP_ASPECT_RATIO",         system.config.get_bool("lindbergh_aspect", return_values=(1, 0)))
        self.setConf(conf, "DEBUG_MSGS",                system.config.get_bool("lindbergh_debug", return_values=(1, 0)))
        self.setConf(conf, "HUMMER_FLICKER_FIX",        system.config.get_bool("lindbergh_hummer", return_values=(1, 0)))
        self.setConf(conf, "OUTRUN_LENS_GLARE_ENABLED", system.config.get_bool("lindbergh_lens", return_values=(1, 0)))
        self.setConf(conf, "BOOST_RENDER_RES",          system.config.get_bool("lindbergh_boost", return_values=(1, 0)))
        self.setConf(conf, "SKIP_OUTRUN_CABINET_CHECK", 1 if "outrun" in romName.lower() or "outr2sdx" in romName.lower() else 0)
        self.setConf(conf, "SRAM_PATH",   f"{self.LINDBERGH_SAVES}/sram.bin.{Path(romName).stem}")
        self.setConf(conf, "EEPROM_PATH", f"{self.LINDBERGH_SAVES}/eeprom.bin.{Path(romName).stem}")

        ## Additional game specific options

        # Virtua Tennis - Card Reader
        if "tennis" in romName.lower() and system.config.get_bool("lindbergh_card"):
            self.setConf(conf, "EMULATE_CARDREADER", 1)
            self.setConf(conf, "CARDFILE_01", f"{self.LINDBERGH_SAVES}/VT3_Card_01.crd")
            self.setConf(conf, "CARDFILE_02", f"{self.LINDBERGH_SAVES}/VT3_Card_02.crd")
        else:
            self.setConf(conf, "EMULATE_CARDREADER", 0)

        # House of the Dead 4 - CPU speed
        cpu_speed = self.get_cpu_min_speed()
        if cpu_speed is not None:
            _logger.debug("Current CPU Speed: %.2f GHz", cpu_speed)
            if "hotd" in romName.lower() and system.config.get_bool("lindbergh_speed"):
                self.setConf(conf, "CPU_FREQ_GHZ", cpu_speed)

        # OutRun 2 - Network
        ip = self.get_ip_address()
        if not ip:
            _logger.debug("Primary destination unreachable. Trying fallback...")
            ip = self.get_ip_address(destination="8.8.8.8")
        if ip:
            _logger.debug("Current IP Address: %s", ip)
            if "outr2sdx" in romName.lower() and system.config.get_bool("lindbergh_ip"):
                self.setConf(conf, "OR2_IP", ip)
        else:
            _logger.debug("Unable to retrieve IP address.")

        # Primeval Hunt mode (touch screen)
        if "primeva" in romName.lower() or "primehunt" in romName.lower():
            self.setConf(conf, "PRIMEVAL_HUNT_MODE", system.config.get("lindbergh_hunt", "1"))

        ## Guns
        if system.config.use_guns and guns:
            need_guns_border = any(gun.needs_borders for gun in guns)
            if need_guns_border:
                bordersSize = system.guns_borders_size_name(guns)
                bordersInnerSize, bordersOuterSize = bezelsUtil.gunBordersSize(bordersSize)
                self.setConf(conf, "WHITE_BORDER_PERCENTAGE", bordersInnerSize)
                self.setConf(conf, "BLACK_BORDER_PERCENTAGE", bordersOuterSize)
            self.setConf(conf, "BORDER_ENABLED", 1 if need_guns_border else 0)
        else:
            self.setConf(conf, "BORDER_ENABLED", 0)

        self.setup_controllers(conf, system, romName, playersControllers, guns, wheels)

    def setup_controllers(
        self,
        conf: dict[str, Any],
        system: Emulator,
        romName: str,
        playersControllers: Controllers,
        guns: Guns,
        wheels: DeviceInfoMapping,
        /,
    ) -> None:
        # 0: SDL, 1: EVDEV, 2: RAW EVDEV
        if system.config.get("lindbergh_controller") == "1":
            input_mode = 0
        else:
            input_mode = 2


        shortRomName = Path(romName.lower()).stem

        self.setConf(conf, "INPUT_MODE", input_mode)

        # comment all player values
        for key in conf["keys"]:
            if key.startswith(("PLAYER_", "ANALOGUE_")) or key == "TEST_BUTTON":
                self.commentConf(conf, key)

        # no more config in sdl mode
        if input_mode == 1:
            return

        # add a test key via evdev
        if input_mode == 2:
            hkevent = hotkeygen.get_hotkeygen_event()
            if hkevent is not None:
                self.setConf(conf, "TEST_BUTTON",   f"{hkevent}:KEY:{ecodes.KEY_T}")
                # only 1 assignment possible for coins, let's it on the select button of player 1 for the moment
                # could be set to hotkeygen/coin and on player1/select via .keys, but different from sdl
                # self.setConf(conf, "PLAYER_1_COIN", f"{hkevent}:KEY:{ecodes.KEY_5}")

        # configure guns
        if input_mode == 2 and system.config.use_guns:
            self.setup_guns_evdev(conf, guns, shortRomName)

        # joysticks
        if input_mode == 2:
            self.setup_joysticks_evdev(conf, system, shortRomName, guns, wheels, playersControllers)

        # map service and test buttons for tests mode
        if system.config.get_bool("lindbergh_test"):
            if input_mode == 2:
                self.setup_test_mode_evdev(conf, playersControllers)

    def setup_test_mode_evdev(
        self,
        conf: dict[str, Any],
        playersControllers: Controllers,
        /,
    ) -> None:
        for pad in playersControllers[:1]:
            input_name = "b"
            if input_name in pad.inputs and pad.inputs[input_name].type == "button":
                self.setConf(conf, "TEST_BUTTON", f"{pad.device_path}:KEY:{pad.inputs[input_name].code}")
            input_name = "down"
            if input_name in pad.inputs and pad.inputs[input_name].type == "hat":
                if pad.inputs[input_name].value == "4": # down
                    # 16 is the HAT0 code, MAX for down/right
                    input_value = f"ABS:{16+1+int(pad.inputs[input_name].id)*2}:MAX"
                    self.setConf(conf, "PLAYER_1_BUTTON_SERVICE", f"{pad.device_path}:{input_value}")
            if input_name in pad.inputs and pad.inputs[input_name].type == "axis":
                relaxValues = pad.get_mapping_axis_relaxed_values()
                if input_name in relaxValues and relaxValues[input_name]["reversed"]:
                    input_value = f"ABS_NEG:{pad.inputs[input_name].code}"
                else:
                    input_value = f"ABS:{pad.inputs[input_name].code}"
                self.setConf(conf, f"PLAYER_1_BUTTON_SERVICE", f"{pad.device_path}:{input_value}:MAX")

    def setup_joysticks_evdev(
        self,
        conf: dict[str, Any],
        system: Emulator,
        shortRomName: str,
        guns: Guns,
        wheels: DeviceInfoMapping,
        playersControllers: Controllers,
        /,
    ) -> None:
        # button that are common to all players
        noPlayerButton = {
            "TEST_BUTTON": True,
            "ANALOGUE_1":  True,
            "ANALOGUE_2":  True,
            "ANALOGUE_3":  True,
            "ANALOGUE_4":  True,
            "ANALOGUE_5":  True,
            "ANALOGUE_6":  True,
            "ANALOGUE_7":  True,
            "ANALOGUE_8":  True,
        }

        # configure joysticks if no gun configured for the user
        nplayer = 1
        continuePlayers = True
        for pad in playersControllers:
            # Handle two players / controllers only, don't do if already configured for guns
            if nplayer <= 2 and continuePlayers and not (system.config.use_guns and len(guns) >= nplayer):
                relaxValues = pad.get_mapping_axis_relaxed_values()

                ### choose the adapted mapping
                if system.config.use_wheels:
                    lindberghCtrl = self.getMappingForJoystickOrWheel(
                        shortRomName,
                        "wheel",
                        nplayer,
                        pad,
                        # This test works because wheels are rearranged to be first in the player list
                        len(wheels) >= nplayer
                    )
                    _logger.debug("lindbergh wheel mapping for player %s", nplayer)
                elif system.config.use_guns:
                    lindberghCtrl = self.getMappingForJoystickOrWheel(shortRomName, "gun", nplayer, pad, False)
                    _logger.debug("lindbergh gun mapping for player %s", nplayer)
                else:
                    lindberghCtrl = self.getMappingForJoystickOrWheel(shortRomName, "pad", nplayer, pad, False)
                    _logger.debug("lindbergh pad mapping for player %s", nplayer)

                # some games must be configured for player 1 only (cause it uses some buttons of the player 2), so stop after player 1
                if nplayer == 1:
                    for input_name in lindberghCtrl:
                        if lindberghCtrl[input_name].endswith("_ON_PLAYER_2"):
                            continuePlayers = False

                # checker on buttons mapping (just to control we have no duplicates)
                x = {}
                for input_name in lindberghCtrl:
                    if lindberghCtrl[input_name] in x:
                        raise InvalidConfiguration(f"duplicate configuration key for {input_name} with value {lindberghCtrl[input_name]}")
                    x[lindberghCtrl[input_name]] = True

                ### configure each input
                controller_name = pad.device_path
                for input_name in lindberghCtrl:

                    # coin is only for player 1
                    if lindberghCtrl[input_name] == "COIN" and nplayer > 1:
                        continue

                    input_base_name = input_name
                    if input_name == "joystick1right":
                        input_base_name = "joystick1left"
                    if input_name == "joystick1down":
                        input_base_name = "joystick1up"
                    if input_name == "joystick2right":
                        input_base_name = "joystick2left"
                    if input_name == "joystick2down":
                        input_base_name = "joystick2up"

                    if input_base_name in pad.inputs and (pad.inputs[input_base_name].code is not None or pad.inputs[input_base_name].type == "hat"):
                        button_name = lindberghCtrl[input_name]

                        # some buttons of player1 are mapped on the player2...
                        player_input = nplayer
                        if button_name.endswith("_ON_PLAYER_2"):
                            button_name = button_name[:-12]
                            player_input = 2
                        ###

                        if pad.inputs[input_base_name].type == "button":
                            input_value = f"KEY:{pad.inputs[input_base_name].code}"
                            if button_name in noPlayerButton:
                                if nplayer == 1:
                                    self.setConf(conf, f"{button_name}", f"{controller_name}:{input_value}")
                            else:
                                if button_name.startswith("ANALOGUE_"):
                                    if nplayer == 1:
                                        self.setConf(conf, f"{button_name}", f"{controller_name}:{input_value}")
                                else:
                                    self.setConf(conf, f"PLAYER_{player_input}_{button_name}", f"{controller_name}:{input_value}")
                        elif pad.inputs[input_base_name].type == "axis":
                            if input_name in relaxValues and relaxValues[input_name]["reversed"]:
                                input_value = f"ABS_NEG:{pad.inputs[input_base_name].code}"
                            else:
                                input_value = f"ABS:{pad.inputs[input_base_name].code}"
                            if button_name.startswith("ANALOGUE_"):
                                if nplayer == 1:
                                    self.setConf(conf, f"{button_name}", f"{controller_name}:{input_value}")
                            else:
                                if input_name == "joystick1left" or input_name == "joystick1up" or input_name == "joystick2left" or input_name == "joystick2up" or input_name == "left" or input_name == "up":
                                    self.setConf(conf, f"PLAYER_{player_input}_{button_name}", f"{controller_name}:{input_value}:MIN")
                                else:
                                    self.setConf(conf, f"PLAYER_{player_input}_{button_name}", f"{controller_name}:{input_value}:MAX")
                        elif pad.inputs[input_base_name].type == "hat":
                            if pad.inputs[input_base_name].value == "1" or pad.inputs[input_base_name].value == "4": # up or down
                                # 16 is the HAT0 code
                                input_value = f"ABS:{16+1+int(pad.inputs[input_base_name].id)*2}"
                            else:
                                input_value = f"ABS:{16+int(pad.inputs[input_base_name].id)*2}"
                            if button_name.startswith("ANALOGUE_"):
                                if nplayer == 1:
                                    self.setConf(conf, f"{button_name}", f"{controller_name}:{input_value}")
                            else:
                                if pad.inputs[input_base_name].value == "1" or pad.inputs[input_base_name].value == "8": # up or left
                                    input_value += ":MIN"
                                else:
                                    input_value += ":MAX"
                                self.setConf(conf, f"PLAYER_{player_input}_{button_name}", f"{controller_name}:{input_value}")
                        else:
                            raise BatoceraException(f"invalid input type: {pad.inputs[input_base_name].type}")
                nplayer += 1

    def getMappingForJoystickOrWheel(  # noqa: RET503
        self,
        shortRomName: str,
        deviceType: Literal['wheel', 'gun', 'pad'],
        nplayer: int,
        pad: Controller,
        isRealWheel: bool,
        /,
    ) -> dict[str, str]:
        lindberghCtrl_pad = {
            "a":              "BUTTON_2",
            "b":              "BUTTON_1",
            "x":              "BUTTON_4",
            "y":              "BUTTON_3",
            "start":          "BUTTON_START",
            "select":         "COIN",
            "up":             "BUTTON_UP",
            "down":           "BUTTON_DOWN",
            "left":           "BUTTON_LEFT",
            "right":          "BUTTON_RIGHT",
            "joystick1up":    "ANALOGUE_2",
            "joystick1left":  "ANALOGUE_1",
            "pageup":         "BUTTON_5",
            "pagedown":       "BUTTON_6",
            "l2":             "BUTTON_7",
            "r2":             "BUTTON_8",
            "l3":             "BUTTON_SERVICE"
        }

        # the same mapping for a wheel or a pad for a wheel game should do the job
        lindberghCtrl_wheel = {
            "a":              "BUTTON_2",
            "b":              "BUTTON_1",
            "x":              "BUTTON_4",
            "y":              "BUTTON_3",
            "start":          "BUTTON_START",
            "select":         "COIN",
            "left":           "BUTTON_LEFT",
            "right":          "BUTTON_RIGHT",
            "joystick1left":  "ANALOGUE_1",
            "pageup":         "BUTTON_DOWN", # gear down
            "pagedown":       "BUTTON_UP",   # gear up
            "l2":             "ANALOGUE_3",
            "r2":             "ANALOGUE_2",
            "l3":             "BUTTON_SERVICE"
        }

        lindberghCtrl_gun = {
            "a":              "BUTTON_2",
            "b":              "BUTTON_1",
            "x":              "BUTTON_4",
            "y":              "BUTTON_3",
            "start":          "BUTTON_START",
            "select":         "COIN",
            "up":             "BUTTON_UP",
            "down":           "BUTTON_DOWN",
            "left":           "BUTTON_LEFT",
            "right":          "BUTTON_RIGHT",
            "joystick1up":    "ANALOGUE_2",
            "joystick1left":  "ANALOGUE_1",
            "pageup":         "BUTTON_5",
            "pagedown":       "BUTTON_6",
            "l2":             "BUTTON_7",
            "r2":             "BUTTON_8",
            "l3":             "BUTTON_SERVICE"
        }

        # mapping specific to games
        _logger.debug("lindberg mapping for game %s", shortRomName)

        if shortRomName == "hdkotr":
            lindberghCtrl_wheel["x"]  = "BUTTON_2"   # change view
            lindberghCtrl_wheel["l2"] = "ANALOGUE_4"
            lindberghCtrl_wheel["r2"] = "ANALOGUE_1"
            lindberghCtrl_wheel["joystick1left"] = "ANALOGUE_2"
            del lindberghCtrl_wheel["a"]
            del lindberghCtrl_wheel["y"]
            lindberghCtrl_wheel["pageup"]   = "BUTTON_4"
            lindberghCtrl_wheel["pagedown"] = "BUTTON_3"

        if shortRomName == "rtuned":
            lindberghCtrl_wheel["x"] = "BUTTON_DOWN"          # change view
            lindberghCtrl_wheel["a"] = "BUTTON_RIGHT"         # boost 1
            lindberghCtrl_wheel["y"] = "BUTTON_1_ON_PLAYER_2" # boost 2
            del lindberghCtrl_wheel["right"]

        if shortRomName.startswith("initiad"):
            lindberghCtrl_wheel["x"]    = "BUTTON_1"    # change view
            lindberghCtrl_wheel["up"]   = "BUTTON_UP"   # menu up
            lindberghCtrl_wheel["down"] = "BUTTON_DOWN" # menu down
            del lindberghCtrl_wheel["b"]

        if shortRomName.startswith("hummer"):
            lindberghCtrl_wheel["a"] = "BUTTON_DOWN_ON_PLAYER_2" # boost
            lindberghCtrl_wheel["x"] = "BUTTON_DOWN"             # change view
            del lindberghCtrl_wheel["pageup"]

        if shortRomName.startswith("segartv"):
            lindberghCtrl_wheel["a"] = "BUTTON_1_ON_PLAYER_2" # boost
            lindberghCtrl_wheel["x"] = "BUTTON_DOWN"          # change view
            del lindberghCtrl_wheel["pageup"]

        if shortRomName.startswith("outr"):
            lindberghCtrl_wheel["x"] = "BUTTON_DOWN" # view change

        # button up/down on player 2
        if shortRomName == "rtuned" or shortRomName.startswith(("segartv", "outr", "initiad")):
            lindberghCtrl_wheel["pageup"]   = "BUTTON_DOWN_ON_PLAYER_2"
            lindberghCtrl_wheel["pagedown"] = "BUTTON_UP_ON_PLAYER_2"

        # remap buttons if for non real wheel
        if deviceType == "wheel" and not isRealWheel:
            x = None
            y = None
            l = None  # noqa: E741
            r = None
            if "x" in lindberghCtrl_wheel:
                x = lindberghCtrl_wheel["x"]
                del lindberghCtrl_wheel["x"]
            if "y" in lindberghCtrl_wheel:
                y = lindberghCtrl_wheel["y"]
                del lindberghCtrl_wheel["y"]
            if "pageup" in lindberghCtrl_wheel:
                l = lindberghCtrl_wheel["pageup"]  # noqa: E741
                del lindberghCtrl_wheel["pageup"]
            if "pagedown" in lindberghCtrl_wheel:
                r = lindberghCtrl_wheel["pagedown"]
                del lindberghCtrl_wheel["pagedown"]
            if x is not None:
                lindberghCtrl_wheel["pageup"] = x # view     ## free x and y for gear up/down
            if y is not None:
                lindberghCtrl_wheel["b"]      = y # action 2 ## free x and y for gear up/down
            if r is not None:
                lindberghCtrl_wheel["x"]      = r
            if l is not None:
                lindberghCtrl_wheel["y"]      = l
        ####

        # pads without l2, but with l as a button, important for wheel
        if "l2" not in pad.inputs and "pageup" in pad.inputs and pad.inputs["pageup"].type == "button":
            lindberghCtrl_wheel["pageup"] = lindberghCtrl_wheel["l2"]
            del lindberghCtrl_wheel["l2"]
        # pads without r2, but with r as a button
        if "r2" not in pad.inputs and "pagedown" in pad.inputs and pad.inputs["pagedown"].type == "button":
            lindberghCtrl_wheel["pagedown"] = lindberghCtrl_wheel["r2"]
            del lindberghCtrl_wheel["r2"]

        # some pads have not analog axis, on some games, prefer the dpad
        if not shortRomName.startswith("vf5") and not shortRomName.startswith("vt"): # all but vf5 and vt3
            # pads without joystick1left, but with a hat
            if "joystick1left" not in pad.inputs and "left" in pad.inputs and (pad.inputs["left"].type == "hat" or pad.inputs["left"].type == "axis"):
                lindberghCtrl_wheel["left"] = lindberghCtrl_wheel["joystick1left"]
                if "right" in lindberghCtrl_wheel:
                    del lindberghCtrl_wheel["right"]
                del lindberghCtrl_wheel["joystick1left"]
                #
                lindberghCtrl_pad["left"] = lindberghCtrl_pad["joystick1left"]
                del lindberghCtrl_pad["right"]
                del lindberghCtrl_pad["joystick1left"]

            # pads without joystick1up, but with a hat
            if "joystick1up" not in pad.inputs and "up" in pad.inputs and (pad.inputs["up"].type == "hat" or pad.inputs["up"].type == "axis"):
                lindberghCtrl_pad["up"] = lindberghCtrl_pad["joystick1up"]
                del lindberghCtrl_pad["down"]
                del lindberghCtrl_pad["joystick1up"]
        ###

        # choose mapping
        if deviceType == "gun":
            # adjustment for player 2 gun
            for x in lindberghCtrl_gun:
                if lindberghCtrl_gun[x] == "ANALOGUE_1" and nplayer == 2:
                    lindberghCtrl_gun[x] = "ANALOGUE_3"
                if lindberghCtrl_gun[x] == "ANALOGUE_2" and nplayer == 2:
                    lindberghCtrl_gun[x] = "ANALOGUE_4"
            return lindberghCtrl_gun

        if deviceType == "wheel":
            return lindberghCtrl_wheel

        if deviceType == "pad":
            return lindberghCtrl_pad

    def setup_guns_evdev(self, conf: dict[str, Any], guns: Guns, shortRomName: str, /) -> None:
        nplayer = 1

        # common batocera mapping
        mappings_codes = {
            "left":   ecodes.BTN_LEFT,
            "right":  ecodes.BTN_RIGHT,
            "middle": ecodes.BTN_MIDDLE,
            "1": ecodes.BTN_1,
            "2": ecodes.BTN_2,
            "3": ecodes.BTN_3,
            "4": ecodes.BTN_4,
            "5": ecodes.BTN_5,
            "6": ecodes.BTN_6,
            "7": ecodes.BTN_7,
            "8": ecodes.BTN_8,
        }

        # lindberg gun mapping
        mappings_actions = {
            "left":   "BUTTON_1", # trigger = BUTTON_1
            "middle": "BUTTON_START",
            "1":      "COIN",
            "right":  "BUTTON_3", # action = BUTTON_3
            "2":      "BUTTON_2", # optional reload in most case = BUTTON_2
            "3":      "BUTTON_4",
            "4":      "BUTTON_5",
            "5":      "BUTTON_UP",
            "6":      "BUTTON_DOWN",
            "7":      "BUTTON_LEFT",
            "8":      "BUTTON_RIGHT",
        }

        if shortRomName == "2spicy":
            mappings_actions["right"] = "BUTTON_2"
            del mappings_actions["2"]

        if shortRomName == "ghostsev":
            mappings_actions["right"] = "BUTTON_2"
            mappings_actions["2"]     = "BUTTON_3"
            mappings_actions["7"]     = "BUTTON_4"
            del mappings_actions["3"]

        if shortRomName == "hotdex":
            mappings_actions["2"] = "BUTTON_LEFT"
            del mappings_actions["7"]
            del mappings_actions["8"]

        if shortRomName == "hotd4sp":
            mappings_actions["2"] = "BUTTON_4"
            del mappings_actions["3"]

        if shortRomName == "letsgojusp":
            # if there is only one gun, let the player1 able to press BUTTON_4 of player 2 (required)
            if len(guns) == 1:
                mappings_actions["7"] = "BUTTON_4"
                del mappings_actions["3"]
                mapping = "8"
                action = "BUTTON_4"
                if mapping in mappings_codes:
                    gun = guns[0]
                    code = mappings_codes[mapping]
                    self.setConf(conf, f"PLAYER_2_{action}", f"{gun.node}:KEY:{code}")
                    del mappings_actions[mapping]
            elif len(guns) > 1:
                mappings_actions["right"] = "BUTTON_4"
                del mappings_actions["3"]

        if shortRomName == "letsgoju":
            if len(guns) == 1:
                mapping = "right"
                action = "BUTTON_START"
                if mapping in mappings_codes:
                    gun = guns[0]
                    code = mappings_codes[mapping]
                    self.setConf(conf, f"PLAYER_2_{action}", f"{gun.node}:KEY:{code}")
                    del mappings_actions[mapping]

        for nplayer, gun in enumerate(guns[:2], start=1):
            _logger.debug("lindbergh gun for player %s", nplayer)
            xplayer = 1+(nplayer-1)*2
            yplayer = 1+(nplayer-1)*2+1
            evplayer = gun.node
            self.setConf(conf, f"ANALOGUE_{xplayer}", f"{evplayer}:ABS:0")
            self.setConf(conf, f"ANALOGUE_{yplayer}", f"{evplayer}:ABS:1")

            # reverse axis for let's go jungle
            if shortRomName == ("letsgoju"): # not for the p version
                self.setConf(conf, f"ANALOGUE_{xplayer}", f"{evplayer}:ABS_NEG:1")
                self.setConf(conf, f"ANALOGUE_{yplayer}", f"{evplayer}:ABS_NEG:0")

            # add shake for hotd4
            if shortRomName == "hotd4":
                xplayerp4 = xplayer + 4
                yplayerp4 = yplayer + 4
                self.setConf(conf, f"ANALOGUE_{xplayerp4}", f"{evplayer}:ABS:0:SHAKE")
                self.setConf(conf, f"ANALOGUE_{yplayerp4}", f"{evplayer}:ABS:1:SHAKE")

            for mapping in mappings_actions:
                if mapping in gun.buttons and mapping in mappings_codes:
                    code = mappings_codes[mapping]
                    action = mappings_actions[mapping]

                    # in hotdex, player2 reload is on button right (et butto left for player 1...)
                    if shortRomName == "hotdex" and nplayer == 2 and action == "BUTTON_LEFT":
                        action = "BUTTON_RIGHT"

                    if not (action == "COIN" and nplayer != 1): # COIN is only for player 1
                        self.setConf(conf, f"PLAYER_{nplayer}_{action}", f"{evplayer}:KEY:{code}")

    def setup_eeprom(self):
        DOWNLOADED_FLAG: Final = self.LINDBERGH_SAVES / "downloaded.txt"
        RAW_URL: Final = "https://raw.githubusercontent.com/batocera-linux/lindbergh-eeprom/main/lindbergh-eeprom.tar.xz"

        mkdir_if_not_exists(self.LINDBERGH_SAVES)
        if not DOWNLOADED_FLAG.exists():
            try:
                # Download the file
                with download(RAW_URL, self.LINDBERGH_SAVES) as downloaded:
                    # Extract the file
                    self.extract_tar_xz(downloaded, self.LINDBERGH_SAVES)
                    # Create the downloaded.txt flag file so we don't download again
                    DOWNLOADED_FLAG.write_text("Download and extraction successful.\n")
                    _logger.debug("Created flag file: %s", DOWNLOADED_FLAG)

            except Exception:
                _logger.exception("An error occurred")

    def setup_libraries(self, romDir: Path, romName: str) -> None:
        # Setup some library quirks for GPU support (NVIDIA?)
        source = Path("/lib32/libkswapapi.so")
        if source.exists():
            destination = Path(romDir) / "libGLcore.so.1"
            if not destination.exists():
                shutil.copy2(source, destination)
                _logger.debug("Copied: %s from %s", destination, source)

        # -= Game specific library versions =-
        if any(keyword in romName.lower() for keyword in ("harley", "hdkotr", "spicy", "rambo", "hotdex", "dead ex")):
            destCg = Path(romDir) / "libCg.so"
            destCgGL = Path(romDir) / "libCgGL.so"
            if not destCg.exists():
                shutil.copy2("/lib32/extralibs/libCg.so.harley", destCg)
                _logger.debug("Copied: %s", destCg)
            if not destCgGL.exists():
                shutil.copy2("/lib32/extralibs/libCgGL.so.harley", destCgGL)
                _logger.debug("Copied: %s", destCgGL)

        # fixes shadows and textures
        if any(keyword in romName.lower() for keyword in ("initiad", "letsgoju", "tennis")):
            destCg = Path(romDir) / "libCg.so"
            destCgGL = Path(romDir) / "libCgGL.so"
            if not destCg.exists():
                shutil.copy2("/lib32/extralibs/libCg.so.other", destCg)
                _logger.debug("Copied: %s", destCg)
            if not destCgGL.exists():
                shutil.copy2("/lib32/extralibs/libCgGL.so.other", destCgGL)
                _logger.debug("Copied: %s", destCgGL)

        # remove any legacy libsegaapi.so
        if Path(romDir, "libsegaapi.so").exists():
            Path(romDir, "libsegaapi.so").unlink()
            _logger.debug("Removed: %s/libsegaapi.so", romDir)

    def setup_config(
        self,
        source_dir: Path,
        system: Emulator,
        gameResolution: Resolution,
        guns: Guns,
        wheels: DeviceInfoMapping,
        playersControllers: Controllers,
        romDir: Path,
        romName: str,
        /,
    ) -> None:
        LINDBERGH_CONFIG_FILE = Path("/userdata/system/configs/lindbergh/lindbergh.conf")
        mkdir_if_not_exists(LINDBERGH_CONFIG_FILE.parent)

        # get an initial version if no version is here
        source_file = source_dir / "lindbergh.conf"
        if not LINDBERGH_CONFIG_FILE.exists() or source_file.stat().st_mtime > LINDBERGH_CONFIG_FILE.stat().st_mtime:
            shutil.copy2(source_file, LINDBERGH_CONFIG_FILE)
            _logger.debug("Updated lindbergh.conf")

        # load and modify it if needed and save it
        conf = self.loadConf(LINDBERGH_CONFIG_FILE)
        self.buildConfFile(conf, system, gameResolution, guns, wheels, playersControllers, romName)
        self.saveConf(conf, LINDBERGH_CONFIG_FILE)

        # copy the config file in the rom dir, where it is used
        shutil.copy2(LINDBERGH_CONFIG_FILE, romDir / "lindbergh.conf")

    def get_cpu_min_speed(self):
        try:
            # Run lscpu to get CPU frequency information
            result = subprocess.run(
                ["lscpu"],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout

            # Find the "CPU min MHz" value
            match = re.search(r"CPU min MHz:\s+([\d.]+)", output)
            if match:
                min_speed_mhz = float(match.group(1))
                # Convert to GHz
                _logger.debug(f"CPU min MHz is {min_speed_mhz}.")
                return min_speed_mhz / 1000

            _logger.debug("CPU min MHz information not found.")
            return None

        except subprocess.CalledProcessError as e:
            _logger.debug("Error running lscpu: %s", e)
            return None

    def get_ip_address(self, destination: str = "1.1.1.1", port: int = 80) -> Any | None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect((destination, port))
                return s.getsockname()[0]
        except Exception as e:
            _logger.debug("Error retrieving IP address: %s", e)
            return None
