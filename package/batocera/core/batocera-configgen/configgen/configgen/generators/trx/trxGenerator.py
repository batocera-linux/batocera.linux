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

import io
import json
import logging
import re
import shutil
import socket
import subprocess
import tarfile
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import ROMS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ...types import HotkeysContext

# Commit of LostArtefacts/TRX-data containing media files and expansions
# Update as needed for new versions so the assets get updated
TRX_DATA_COMMIT = "371be77631a40ec96babf57a7179afeee9cd30b8"

class TRXGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "trx",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "save_state": "KEY_F5", "restore_state": "KEY_F6" }
        }

    def _has_internet(self) -> bool:
        try:
            socket.gethostbyname("github.com")
            return True
        except OSError:
            return False

    def _setup_assets(self, trxRomPath: Path) -> None:
        version_file = trxRomPath / "cfg" / ".trx_data_commit"
        
        local_commit = ""
        if version_file.exists():
            try:
                local_commit = version_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

        # If up-to-date, skip the download instantly
        if local_commit == TRX_DATA_COMMIT:
            return

        # Skip if offline to avoid blocking or hanging the game boot
        if not self._has_internet():
            _logger.debug("System is offline. Skipping TRX assets setup.")
            return

        # YAD dialog for a graphical download progress bar
        yad_proc = subprocess.Popen(
            [
                "yad", "--progress",
                "--title=Tomb Raider Assets",
                "--text=Downloading TRX media assets...",
                "--auto-close",
                "--width=400",
                "--height=110",
                "--window-icon=system-run"
            ],
            stdin=subprocess.PIPE,
            text=True
        )

        # Initialize progress bar to 0%
        if yad_proc.stdin:
            try:
                yad_proc.stdin.write("0\n")
                yad_proc.stdin.flush()
            except OSError:
                pass

        # See https://github.com/LostArtefacts/TRX-data/blob/main/tools/zip_ship for guidance
        try:
            url = f"https://github.com/LostArtefacts/TRX-data/archive/{TRX_DATA_COMMIT}.tar.gz"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

            with urllib.request.urlopen(req) as response:
                total_size = int(response.info().get('Content-Length', 0))
                downloaded = 0
                buffer = io.BytesIO()

                while True:
                    block = response.read(65536)
                    if not block:
                        break
                    buffer.write(block)
                    downloaded += len(block)

                    if total_size > 0 and yad_proc.stdin:
                        percent = int(downloaded * 100 / total_size)
                        try:
                            yad_proc.stdin.write(f"{percent}\n")
                            yad_proc.stdin.flush()
                        except OSError:
                            pass

                buffer.seek(0)
                with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
                    tar.extractall(path=trxRomPath)

                # Locate the extracted directory dynamically to handle SHA-length folder names safely
                temp_extracted = None
                for item in trxRomPath.iterdir():
                    if item.is_dir() and item.name.startswith("TRX-data-"):
                        temp_extracted = item
                        break

                if temp_extracted and temp_extracted.exists():
                    games_list = ["tr1", "tr1-ub", "tr2", "tr2-gm", "tr3", "tr3-la"]

                    for g in games_list:
                        ship_dir = temp_extracted / g / "ship"
                        if ship_dir.exists() and ship_dir.is_dir():
                            for file_path in ship_dir.rglob("*"):
                                if file_path.is_file():
                                    rel_path = file_path.relative_to(ship_dir)
                                    mapped_rel = rel_path
                                    
                                    # Apply specific remapping rules matching upstream package scripts
                                    if rel_path.is_relative_to("data/images"):
                                        mapped_rel = Path(f"games/{g}/images") / rel_path.relative_to("data/images")
                                    elif g == "tr2" and rel_path.is_relative_to("music"):
                                        mapped_rel = Path("games/tr2/music") / rel_path.relative_to("music")
                                    elif g == "tr2-gm":
                                        if rel_path.name == "main_gm.sfx":
                                            mapped_rel = Path("games/tr2-gm/main.sfx")
                                        elif rel_path.name == "title_gm.tr2":
                                            mapped_rel = Path("games/tr2-gm/levels/title.tr2")
                                        elif rel_path.is_relative_to("data"):
                                            mapped_rel = Path("games/tr2-gm/levels") / rel_path.relative_to("data")

                                    dest_file = trxRomPath / mapped_rel
                                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(file_path, dest_file)

                    # Clean up temporary tarball extract folder
                    shutil.rmtree(temp_extracted, ignore_errors=True)

                # Write local version validation file
                version_file.parent.mkdir(parents=True, exist_ok=True)
                version_file.write_text(TRX_DATA_COMMIT, encoding="utf-8")

        except Exception as e:
            _logger.debug("Error during TRX on-demand asset setup: %s", e)
        finally:
            try:
                yad_proc.stdin.close()
            except Exception:
                pass
            try:
                yad_proc.wait(timeout=2)
            except Exception:
                pass

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        trxRomPath = ROMS / "traider"

        # Copy shared package configurations/shaders etc
        for item in Path("/usr/bin/trx").iterdir():
            dest = trxRomPath / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        
        # Make sure binary is executable
        trx_bin_dest = trxRomPath / "TRX"
        if trx_bin_dest.exists():
            trx_bin_dest.chmod(0o755)

        # Download missing/outdated assets on demand
        self._setup_assets(trxRomPath)

        # Create or update display settings configuration
        trxConfigPath = trxRomPath / "cfg" / "shell.json5"
        mkdir_if_not_exists(trxConfigPath.parent)
        config_data = {}

        if trxConfigPath.exists():
            try:
                content = trxConfigPath.read_text(encoding="utf-8")
                # Remove JSON5 comments and trailing commas so python's json can decode it
                content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                content = re.sub(r',(\s*[\]}])', r'\1', content)
                config_data = json.loads(content)
            except Exception as e:
                _logger.debug("Failed to parse JSON5 format in %s: %s. Overwriting with clean settings.", trxConfigPath, e)

        # Update settings
        config_data.update(
            {
                "is_fullscreen": True,
                "width": gameResolution["width"],
                "height": gameResolution["height"]
            }
        )

        try:
            trxConfigPath.write_text(json.dumps(config_data, indent=2), encoding="utf-8")
        except Exception as e:
            _logger.debug("Error writing configuration file %s: %s", trxConfigPath, e)

        # Detect mod from the launcher file's parent folder
        valid_mods = {
            "tr1", "tr1-ub", "tr1-demo-pc", "tr1-level",
            "tr2", "tr2-gm", "tr2-level",
            "tr3", "tr3-la", "tr3-level"
        }
        mod = rom.parent.name if rom.parent.name in valid_mods else "tr1"

        return Command.Command(
            array=[trx_bin_dest, "--mod", mod],
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1):
            return 16/9
        return 4/3
