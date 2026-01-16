from __future__ import annotations

import configparser
import filecmp
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Any

from ... import Command
from ...batoceraPaths import BIOS, SAVES, mkdir_if_not_exists
from ...utils import vulkan, wine
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class DemulGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "demul",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    @staticmethod
    def sync_directories(source_dir: Path, dest_dir: Path):
        dcmp = filecmp.dircmp(source_dir, dest_dir)
        # Files that are only in the source directory or are different
        differing_files = dcmp.diff_files + dcmp.left_only
        for file in differing_files:
            src_path = source_dir / file
            dest_path = dest_dir / file
            # Copy and overwrite the files from source to destination
            shutil.copy2(src_path, dest_path)

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Determine what system to define for demul
        demulsystem = system.name

        wine_runner = wine.Runner("wine-proton", "demul")
        demulSaves = SAVES / demulsystem
        emupath = wine_runner.bottle_dir / "demul"
        
        # Check Vulkan first
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
        else:
            _logger.debug("*** Vulkan driver required is not available on the system!!! ***")
            sys.exit()

        # Set to 32bit environment as Demul is 32-bit
        os.environ["WINEARCH"] = "win32"

        # Make system directories
        mkdir_if_not_exists(wine_runner.bottle_dir)
        mkdir_if_not_exists(demulSaves)

        # Create dir & copy demul binary to wine bottle as necessary
        source_emu = Path("/usr/demul")
        
        if not emupath.exists():
            shutil.copytree(source_emu, emupath)
        
        # Check binary then copy updated files as necessary
        if not filecmp.cmp(source_emu / "demul.exe", emupath / "demul.exe"):
            self.sync_directories(source_emu, emupath)

        # Install necessary wine tricks if needed
        wine_runner.install_wine_trick("d3dcompiler_47") 

        # Handle DLLs (DXVK)
        # Since we are using WINEARCH=win32, 32-bit DLLs go into system32
        dll_files = ["d3d11.dll", "dxgi.dll", "d3dcompiler_43.dll", "d3dcompiler_47.dll"]
        
        for dll in dll_files:
            try:
                src_path = wine.WINE_BASE / "dxvk" / "x32" / dll
                # In a win32 prefix, system32 holds 32-bit files
                dest_path = wine_runner.bottle_dir / "drive_c" / "windows" / "system32" / dll
                
                if src_path.exists():
                    # Remove existing link/file if it already exists to ensure update
                    if dest_path.exists() or dest_path.is_symlink():
                        dest_path.unlink()
                    dest_path.symlink_to(src_path)
            except Exception as e:
                _logger.debug("Error creating 32-bit link for %s: %s", dll, e)

        # Simplify ROM name extraction
        romname = rom.name
        smplromname = rom.stem

        # Prepare Config Parsing
        configFileName = emupath / "Demul.ini"
        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str

        if configFileName.exists():
            try:
                with configFileName.open("r", encoding="utf_8_sig") as fp:
                    Config.read_file(fp)
            except Exception:
                pass

        # Define paths for Windows context (mapped to Z:)
        nvram = demulSaves
        nvram_path_win = PureWindowsPath(nvram)
        roms0 = BIOS
        roms0_path_win = PureWindowsPath(roms0)
        
        # Specific rom paths
        roms1 = Path("/userdata/roms/hikaru")
        roms1_path_win = PureWindowsPath(roms1)
        roms2 = Path("/userdata/roms/gaelco")
        roms2_path_win = PureWindowsPath(roms2)
        roms3 = Path("/userdata/roms/cave3rd")
        roms3_path_win = PureWindowsPath(roms3)
        
        plugins = Path("/userdata/saves/demul/demul/plugins/")
        # If user plugins don't exist, point to emu plugins
        if not plugins.exists():
             plugins = emupath / "plugins"
        plugins_path_win = PureWindowsPath(plugins)

        # [files] section
        if not Config.has_section("files"):
            Config.add_section("files")
        Config.set("files", "nvram", f"Z:{nvram_path_win}")
        Config.set("files", "roms0", f"Z:{roms0_path_win}")
        Config.set("files", "romsPathsCount", "8")
        Config.set("files", "roms1", f"Z:{roms1_path_win}")
        Config.set("files", "roms2", f"Z:{roms2_path_win}")
        Config.set("files", "roms3", f"Z:{roms3_path_win}")

        # [plugins] section
        if not Config.has_section("plugins"):
            Config.add_section("plugins")
        Config.set("plugins", "directory", f"Z:{plugins_path_win}")
        Config.set("plugins", "spu", "spuDemul.dll")
        Config.set("plugins", "pad", "padDemul.dll")
        Config.set("plugins", "net", "netDemul.dll")
        
        # Gaelco won't work with the new DX11 plugin
        if demulsystem == "gaelco":
            Config.set("plugins", "gpu", "gpuDX11old.dll")
        else:
            Config.set("plugins", "gpu", "gpuDX11.dll")

        # Plugin for images (GDR)
        if ".zip" in romname or ".7z" in romname:
            Config.set("plugins", "gdr", "gdrImage.dll")

        # Save Demul.ini
        with configFileName.open("w", encoding="utf_8_sig") as configfile:
            Config.write(configfile)

        # Adjust fullscreen & resolution in gpuDX11.ini (or old)
        if demulsystem == "gaelco":
            gpuConfigFileName = emupath / "gpuDX11old.ini"
        else:
            gpuConfigFileName = emupath / "gpuDX11.ini"
        
        GpuConfig = configparser.ConfigParser(interpolation=None)
        GpuConfig.optionxform = str
        
        if gpuConfigFileName.exists():
            try:
                with gpuConfigFileName.open("r", encoding="utf_8_sig") as fp:
                    GpuConfig.read_file(fp)
            except Exception:
                pass

        if not GpuConfig.has_section("main"):
            GpuConfig.add_section("main")
        
        # Always fullscreen
        GpuConfig.set("main", "UseFullscreen", "1")
        
        # Aspect Ratio
        if system.isOptSet("demulRatio"):
            GpuConfig.set("main", "aspect", format(system.config["demulRatio"]))
        else:
            GpuConfig.set("main", "aspect", "1")

        # VSync
        if system.isOptSet("demulVSync"):
            GpuConfig.set("main", "Vsync", format(system.config["demulVSync"]))
        else:
            GpuConfig.set("main", "Vsync", "0")
        
        # Scaling
        if system.isOptSet("demulScaling"):
            GpuConfig.set("main", "scaling", format(system.config["demulScaling"]))
        else:
            GpuConfig.set("main", "scaling", "1")

        if not GpuConfig.has_section("resolution"):
            GpuConfig.add_section("resolution")
        
        # Use game resolution
        GpuConfig.set("resolution", "Width", str(gameResolution["width"]))
        GpuConfig.set("resolution", "Height", str(gameResolution["height"]))

        # Save GPU ini
        with gpuConfigFileName.open("w", encoding="utf_8_sig") as configfile:
            GpuConfig.write(configfile)

        # Setup Command 
        commandArray = [wine_runner.wine, emupath / "demul.exe"]
        
        if demulsystem:
            commandArray.append(f"-run={demulsystem}")
        
        commandArray.append(f"-rom={smplromname}")

        environment = wine_runner.get_environment()
        
        # Add necessary overrides
        environment.update(
            {
                "LD_LIBRARY_PATH": f"/lib32:/usr/lib32:{environment.get('LD_LIBRARY_PATH', '')}",
                "WINEDLLOVERRIDES": "d3d11,dxgi,d3dcompiler_47=n,b",
                # Audio handling for Pipewire
                "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
            }
        )

        # Handle window quirks with Demul systems
        if system.name in ["cave3rd", "gaelco"]:
            if os.environ.get("WAYLAND_DISPLAY"):
                trigger_cmd = (
                    "sleep 5 && "
                    "export DISPLAY=:0 && "
                    "xdotool getactivewindow key F3"
                )
            else:
                trigger_cmd = (
                    "sleep 5 && "
                    "export DISPLAY=:0 && "
                    "xdotool getactivewindow key F3 && "
                    "xdotool getactivewindow key alt+Return"
                )

            try:
                subprocess.Popen(
                    ["sh", "-c", trigger_cmd],
                    env=os.environ,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            except Exception as e:
                _logger.error(f"Failed to schedule Alt+Enter: {e}")

        return Command.Command(array=commandArray, env=environment)

    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        aspect = config.get("demulRatio")
        if aspect == "0" or aspect == "2":
            return 16/9
        return 4/3
