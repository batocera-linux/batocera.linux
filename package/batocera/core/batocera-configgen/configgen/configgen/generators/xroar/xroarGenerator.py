from __future__ import annotations

import pathlib
import subprocess
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class XroarGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xroar",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_Q"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        xroarConfigDir = CONFIGS / "xroar"
        mkdir_if_not_exists(xroarConfigDir)
        confFile = xroarConfigDir / "xroar.conf"

        # Write the configuration file
        with confFile.open("w") as f:
            # BIOS search paths
            f.write("rompath /userdata/bios/xroar\n")

            # Machine Selection
            f.write(f"default-machine {system.config.get('xroar_machine', 'coco2bus')}\n")

            # Set audio volume to 100
            f.write("ao-volume 100\n")

            # Cartridge Autostart
            if system.config.get_bool('xroar_cartauto'):
                f.write("cart-autorun\n")

            # VSync
            if system.config.get_bool('xroar_vsync'):
                f.write("vo-vsync\n")

            # Fullscreen
            f.write("fs\n")

        rom_path=str(rom)
        if rom.suffix.lower() in [".zip", ".7z"]:
            try:
                proc = subprocess.run(['batocera-xtract', 'l', str(rom)], capture_output=True, text=True)
                if proc.returncode == 10:
                    for line in proc.stdout.splitlines():
                        if pathlib.Path(line).suffix.lower() in [".rom", ".dsk", ".cas", ".ccc", ".wav"]:
                            subprocess.run(['batocera-xtract', 'pyx', str(rom), '/tmp', line], check=True)
                            rom_path = "/tmp/" + line
                            break

                if rom_path == str(rom):
                    raise Exception("Can't find a matching file in archive")

            except Exception as error:
                print(f"7z error: {error}")


        commandArray = ["xroar", "-c", str(confFile), rom_path]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 4/3
