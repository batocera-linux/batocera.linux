from __future__ import annotations

import logging
import re
import shutil
import struct
from typing import TYPE_CHECKING, Any

from ruamel.yaml import YAML

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.fs import directory_differences
from batocera_common.yaml import safe_load_yaml12

from ... import Command
from ...batoceraPaths import BIOS, CACHE, CONFIGS, configure_emulator, mkdir_if_not_exists
from ...exceptions import BatoceraException
from ...utils import vulkan
from ..Generator import Generator
from . import rpcs3Controllers
from .rpcs3Paths import (
    RPCS3_BIN,
    RPCS3_CONFIG,
    RPCS3_CONFIG_DIR,
    RPCS3_CURRENT_CONFIG,
    RPCS3_DEV_HDD0_DIR,
    RPCS3_IMPORTED_PATCH,
    RPCS3_PATCH_CONFIG,
    RPCS3_USIO_CONFIG,
    RPCS3_VFS_CONFIG,
)

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext, Resolution

_logger = logging.getLogger(__name__)


# USB device tuning for the arcade PS3 titles (System 357/369, Taiko, ...) shipped as a
# PSN squashfs. These all share the SCEEXE000 title-id, so they cannot be told apart by
# their dev_hdd0/game/<id> directory; instead they are matched on the PARAM.SFO TITLE.
# Each entry maps a /dev_usbNNN slot to the emulated USB I/O board id (Serial/VID/PID);
# the slot Path is filled at runtime from the squashfs overlay when it ships that folder.
# NOTE: keys must be the exact PARAM.SFO TITLE. Only "DarkEscape" is confirmed so far;
# the others are keyed by their working name pending the real TITLE value.
_ARCADE_USB_CONFIG: dict[str, dict[str, dict[str, str]]] = {
    "DarkEscape": {
        "/dev_usb000": {"Serial": "268611070000", "VID": "0b9a", "PID": "0c00"},
    },
    "TEKKEN6": {
        "/dev_usb000": {"Serial": "76C0D0000000", "VID": "0693", "PID": "0026"},
        "/dev_usb007": {"Serial": "76C0D0003038", "VID": "0693", "PID": "0026", "Path": ""},
    },
    "TEKKEN6BR": {
        "/dev_usb000": {"Serial": "026450800000", "VID": "0693", "PID": "0026"},
        "/dev_usb007": {"Serial": "76C0D0003038", "VID": "0693", "PID": "0026", "Path": ""},
    },
    "RazingStorm": {
        "/dev_usb000": {"Serial": "026391000000", "VID": "0693", "PID": "0026"},
    },
    "Sailor zombie": {
        "/dev_usb000": {"Serial": "271711170000", "VID": "0b9a", "PID": "0c10"},
    },
    "DZB3": {
        "/dev_usb000": {"Serial": "267210000000", "VID": "0B9A", "PID": "0C00"},
    },
    "Deadstorm Pirates Special Edition": {
        "/dev_usb000": {"Serial": "272311000000", "VID": "0B9A", "PID": "0C00"},
    },
    # Tekken Tag Tournament 2 and its Unlimited revision share the same TITLE.
    "TEKKEN TAG TOURNAMENT 2": {
        "/dev_usb000": {"Serial": "267910000000", "VID": "0B9A", "PID": "0C00"},
    },
    # Taiko no Tatsujin variants all share the same I/O board ids.
    **{
        taiko: {
            "/dev_usb000": {"Serial": "000000000000", "VID": "13fe", "PID": "4100"},
            "/dev_usb001": {"Serial": "268411060021", "VID": "0b9a", "PID": "0c00"},
        }
        for taiko in (
            "Taiko no Tatsujin",          # Sorairo Version
            "Taiko no Tatsujin(S101)",    # Blue Version
            "Taiko no Tatsujin(S111)",    # Green Version
            "Taiko no Tatsujin(ST41)",    # Momoiro Version
            "Taiko no Tatsujin(ST48)",    # Wadaiko Master
            "Taiko no Tatsujin(ST51)",    # Kimidori Version
            "Taiko no Tatsujin(ST61)",    # Murasaki Version
            "Taiko no Tatsujin(ST71)",    # White Version
            "Taiko no Tatsujin(ST87)",    # Red Version
            "Taiko no Tatsujin(ST91)",    # Yellow Version
        )
    },
}

# RPCS3 game patches required by the arcade titles, merged into the user's
# patches/imported_patch.yml. New PPU entries are added without overwriting any the
# user may already have.
_ARCADE_PATCHES: dict[str, Any] = {
    "Version": 1.2,
    "PPU-31faa92273d6269ea41b4d158e443f3d0e4174a7": {
        "Bypass Security Checks (Green)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x004b69e8", "0x38600000"]],
        },
    },
    "PPU-17fe05b18e1e6b40d5387418529be44fdf5e39a3": {
        "Bypass Security Checks (Wadaiko)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x00347060", "0x38600000"]],
        },
    },
    "PPU-d3af4341bb24860b223158db5b0093c87bf91d90": {
        "Bypass Security Checks (Momoiro)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x0032d910", "0x38600000"]],
        },
    },
    "PPU-f20ba6cf299b3873d7007f8a4f1e8efd2319ade4": {
        "Bypass Security Checks (Murasaki)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x0039d238", "0x38600000"]],
        },
    },
    "PPU-2e6b644196e1fa089efd4d87db9c43fe81e81263": {
        "Bypass Security Checks (Red)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x0041ec50", "0x38600000"]],
        },
    },
    "PPU-58f3c6e971e82e67b0c69cfdd362e0ca60ce92a4": {
        "Bypass Security Checks (White)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x0041f738", "0x38600000"]],
        },
    },
    "PPU-de4bd316b3e0a94b1620dc0b8c663f3ff865f409": {
        "Bypass Security Checks (Yellow)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x00456638", "0x38600000"]],
        },
    },
    "PPU-0ac0a218b038d56c015bc33018f2875d406547e8": {
        "Bypass Security Checks (Blue)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x00474b78", "0x38600000"]],
        },
    },
    "PPU-0b8c2d5f0d1819cdaafaa297da508065b7b00edb": {
        "Bypass Security Checks (Kimidori)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x0035b4c8", "0x38600000"]],
        },
    },
    "PPU-78cfd074e799c0aeaf5e4241c597f741ba10bd1a": {
        "Bypass Security Checks (KATSU-DON)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x00299e10", "0x38600000"]],
        },
    },
    "PPU-38935c6c0a4cc67b8908ed312fafaa8a605a18e4": {
        "Bypass Security Checks (Sorairo)": {
            "Games": {"Taiko no Tatsujin": {"SCEEXE000": ["01.00"]}},
            "Author": "GetzeAve",
            "Notes": "Yes.",
            "Patch Version": 1.0,
            "Patch": [["be32", "0x002d5098", "0x38600000"]],
        },
    },
}

# Patch enable state required by the Taiko titles, merged into patches/patch_config.yml.
_TAIKO_PATCH_CONFIG: dict[str, Any] = {
    "PPU-38935c6c0a4cc67b8908ed312fafaa8a605a18e4": {
        "Bypass Security Checks (Sorairo)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-78cfd074e799c0aeaf5e4241c597f741ba10bd1a": {
        "Bypass Security Checks (KATSU-DON)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-2e6b644196e1fa089efd4d87db9c43fe81e81263": {
        "Bypass Security Checks (Red)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-d3af4341bb24860b223158db5b0093c87bf91d90": {
        "Bypass Security Checks (Momoiro)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-17fe05b18e1e6b40d5387418529be44fdf5e39a3": {
        "Bypass Security Checks (Wadaiko)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-31faa92273d6269ea41b4d158e443f3d0e4174a7": {
        "Bypass Security Checks (Green)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-f20ba6cf299b3873d7007f8a4f1e8efd2319ade4": {
        "Bypass Security Checks (Murasaki)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-de4bd316b3e0a94b1620dc0b8c663f3ff865f409": {
        "Bypass Security Checks (Yellow)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-0ac0a218b038d56c015bc33018f2875d406547e8": {
        "Bypass Security Checks (Blue)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-58f3c6e971e82e67b0c69cfdd362e0ca60ce92a4": {
        "Bypass Security Checks (White)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
    "PPU-0b8c2d5f0d1819cdaafaa297da508065b7b00edb": {
        "Bypass Security Checks (Kimidori)": {
            "Taiko no Tatsujin": {"SCEEXE000": {"01.00": {"Enabled": True}}},
        },
    },
}

# USIO emulated arcade I/O board button mapping (Taiko / Tekken / card reader), written
# verbatim as the global usio.yml for arcade titles.
_USIO_CONFIG = """\
Player 1:
  Test: R3
  Coin: Select
  Service: L3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
Player 2:
  Test: R3
  Coin: Select
  Service: L3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
Player 3:
  Test: Select
  Coin: L3
  Service: R3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
Player 4:
  Test: Select
  Coin: L3
  Service: R3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
"""

class Rpcs3Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "rpcs3",
            "keys": { "exit": "/usr/bin/rpcs3-exit", "menu": ["KEY_LEFTSHIFT", "KEY_F10"],
                      "pause": ["KEY_LEFTCTRL", "KEY_P"] }
        }

    def _migrate_dev_hdd0(self) -> None:
        legacy_dev_hdd0 = RPCS3_CONFIG_DIR / "dev_hdd0"
        if not legacy_dev_hdd0.exists():
            # New install or fully migrated: nothing to do
            return

        if RPCS3_DEV_HDD0_DIR.exists():
            # Partial or failed migration: leave it alone
            _logger.warning(
                "Skipping RPCS3 dev_hdd0 migration: target directory already exists at %s", RPCS3_DEV_HDD0_DIR
            )
            return

        mkdir_if_not_exists(RPCS3_DEV_HDD0_DIR.parent)

        try:
            shutil.copytree(legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)
        except Exception:
            _logger.exception("Failed to copy RPCS3 dev_hdd0 from %s to %s", legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)
            return

        _logger.debug("Successfully copied RPCS3 dev_hdd0 from %s to %s", legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)

        differences = directory_differences(legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)
        if differences:
            _logger.error("RPCS3 dev_hdd0 migration verification failed:\n%s", differences.report())
            return

        _logger.debug("Verified RPCS3 dev_hdd0 migration from %s to %s", legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)

        shutil.rmtree(legacy_dev_hdd0)

        _logger.debug("Completed RPCS3 dev_hdd0 migration from %s to %s", legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        self._migrate_dev_hdd0()

        mkdir_if_not_exists(RPCS3_DEV_HDD0_DIR)

        rom_dev_hdd0 = rom / "dev_hdd0"
        rom_dev_hdd1 = rom / "dev_hdd1"
        rom_game_dir = rom_dev_hdd0 / "game"

        # Detect PSN game packed as a squashfs: emulatorlauncher has already mounted the
        # squashfs and (via writesToRom=True) created a writable overlayfs, so rom is
        # /var/run/overlays/<stem> mirroring the dev_hdd0 layout.
        is_psn_squashfs = rom.is_dir() and str(rom).startswith("/var/run/") and rom_game_dir.is_dir()

        # Arcade PS3 titles are matched on their PARAM.SFO TITLE and get a per-game USB I/O
        # board tuning. Arcade titles always use the keyboard input config (lightguns and
        # gamepads are driven through it); other titles keep the gamepad config.
        arcade_title = Rpcs3Generator._matchArcadeTitle(rom, is_psn_squashfs)
        usb_tuning = _ARCADE_USB_CONFIG[arcade_title] if arcade_title else None
        use_keyboard = bool(arcade_title)

        rpcs3Controllers.generateControllerConfig(system, playersControllers, rom, keyboard=use_keyboard)

        # Taking care of the CurrentSettings.ini file
        mkdir_if_not_exists(RPCS3_CURRENT_CONFIG.parent)

        # Generates CurrentSettings.ini with values to disable prompts on first run

        rpcsCurrentSettings = CaseSensitiveConfigParser(interpolation=None)
        if RPCS3_CURRENT_CONFIG.exists():
            rpcsCurrentSettings.read(RPCS3_CURRENT_CONFIG)

        # Sets Gui Settings to close completely and disables some popups
        if not rpcsCurrentSettings.has_section("main_window"):
            rpcsCurrentSettings.add_section("main_window")

        rpcsCurrentSettings.set("main_window", "confirmationBoxExitGame", "false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledInstallPUP","false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledWelcome","false")

        with RPCS3_CURRENT_CONFIG.open("w") as configfile:
            rpcsCurrentSettings.write(configfile)

        mkdir_if_not_exists(RPCS3_CONFIG.parent)

        # Generate a default config if it doesn't exist otherwise just open the existing
        rpcs3ymlconfig: dict[str, dict[str, Any]] = {}
        if RPCS3_CONFIG.is_file():
            rpcs3ymlconfig = safe_load_yaml12(RPCS3_CONFIG, dict[str, dict[str, Any]]) or {}

        # VFS is no longer stored in config.yml: RPCS3 reads it from a dedicated vfs.yml
        # file. Drop any stale VFS section that older versions may have written here.
        rpcs3ymlconfig.pop("VFS", None)

        # Add Nodes if not in the file
        if "Core" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Core"] = {}
        if "Video" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Video"] = {}
        if "Audio" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Audio"] = {}
        if "Input/Output" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Input/Output"] = {}
        if "System" not in rpcs3ymlconfig:
            rpcs3ymlconfig["System"] = {}
        if "Net" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Net"] = {}
        if "Savestate" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Savestate"] = {}
        if "Miscellaneous" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Miscellaneous"] = {}
        if "Log" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Log"] = {}

        # -= [Core] =-
        # Set the PPU Decoder based on config
        rpcs3ymlconfig["Core"]["PPU Decoder"] = system.config.get("rpcs3_ppudecoder", "Recompiler (LLVM)")
        # Set the SPU Decoder based on config
        rpcs3ymlconfig["Core"]["SPU Decoder"] = system.config.get("rpcs3_spudecoder", "Recompiler (LLVM)")
        # Set the SPU XFloat Accuracy based on config
        rpcs3ymlconfig["Core"]["XFloat Accuracy"] = system.config.get("rpcs3_spuxfloataccuracy", "Approximate")
        # Set the Default Core Values we need
        # Force to True for now to account for updates where exiting config file present. (True results in less stutter when a SPU module is in cache)
        rpcs3ymlconfig["Core"]["SPU Cache"] = True
        # Preferred SPU Threads
        rpcs3ymlconfig["Core"]["Preferred SPU Threads"] = system.config.get_int("rpcs3_sputhreads", 0)
        # SPU Loop Detection
        rpcs3ymlconfig["Core"]["SPU loop detection"] = system.config.get_bool("rpcs3_spuloopdetection")
        # SPU Block Size
        rpcs3ymlconfig["Core"]["SPU Block Size"] = system.config.get("rpcs3_spublocksize", "Safe")
        # Max Power Saving CPU-Preemptions
        # values are maximum yields per frame threshold
        rpcs3ymlconfig["Core"]["Max CPU Preempt Count"] = system.config.get_int("rpcs3_maxcpu_preemptcount", 0)
        # Sleep Timers Accuracy
        rpcs3ymlconfig["Core"]["Sleep Timers Accuracy"] = system.config.get("rpcs3_sleep_timers_accuracy", "As Host")

        # -= [Video] =-
        # gfx backend - default to Vulkan
        # Check Vulkan first to be sure
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            if system.config.get("rpcs3_gfxbackend") == "OpenGL":
                _logger.debug("User selected OpenGL")
                rpcs3ymlconfig["Video"]["Renderer"] = "OpenGL"
            else:
                rpcs3ymlconfig["Video"]["Renderer"] = "Vulkan"

            if vulkan.has_discrete_gpu():
                _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                discrete_name = vulkan.get_discrete_gpu_name()
                if discrete_name:
                    _logger.debug("Using Discrete GPU Name: %s for RPCS3", discrete_name)
                    if "Vulkan" not in rpcs3ymlconfig["Video"]:
                        rpcs3ymlconfig["Video"]["Vulkan"] = {}
                    rpcs3ymlconfig["Video"]["Vulkan"]["Adapter"] = discrete_name
                else:
                    _logger.debug("Couldn't get discrete GPU Name")
            else:
                _logger.debug("Discrete GPU is not available on the system. Using default.")
        else:
            _logger.debug("Vulkan driver is not available on the system. Falling back to OpenGL")
            rpcs3ymlconfig["Video"]["Renderer"] = "OpenGL"

        # System aspect ratio (the setting in the PS3 system itself, not the displayed ratio) a.k.a. TV mode.
        # If not set, see if the screen ratio is closer to 4:3 or 16:9 and pick that.
        rpcs3ymlconfig["Video"]["Aspect ratio"] = system.config.get("rpcs3_ratio") or Rpcs3Generator.getClosestRatio(gameResolution)
        # Shader compilation
        rpcs3ymlconfig["Video"]["Shader Mode"] = system.config.get("rpcs3_shadermode", "Async Shader Recompiler")
        # Vsync
        rpcs3ymlconfig["Video"]["VSync"] = system.config.get("rpcs3_vsync", "Full")
        # Stretch to display area
        rpcs3ymlconfig["Video"]["Stretch To Display Area"] = system.config.get_bool("rpcs3_stretchdisplay")
        # Frame Limit
        # Frame limit checks for specific values("Auto", "Off", "30", "50", "59.94", "60")
        # Second Frame Limit can be any float/integer. 0 = disabled.
        match system.config.get("rpcs3_framelimit"):
            case system.config.MISSING:
                rpcs3ymlconfig["Video"]["Frame limit"] = "Auto"
                rpcs3ymlconfig["Video"]["Second Frame Limit"] = 0
            # Check for valid Frame Limit value, if it's not a Frame Limit value apply to Second Frame Limit
            case "Off" | "30" | "50" | "59.94" | "60" as framelimit:
                rpcs3ymlconfig["Video"]["Frame limit"] = framelimit
                rpcs3ymlconfig["Video"]["Second Frame Limit"] = 0
            case _ as framelimit:
                rpcs3ymlconfig["Video"]["Second Frame Limit"] = framelimit
                rpcs3ymlconfig["Video"]["Frame limit"] = "Off"
        # Write Color Buffers (Deadstorm Pirates needs it for Target Hitting)
        rpcs3ymlconfig["Video"]["Write Color Buffers"] = (
            system.config.get_bool("rpcs3_colorbuffers")
            or arcade_title == "Deadstorm Pirates Special Edition"
        )
        # Read Color Buffers
        rpcs3ymlconfig["Video"]["Read Color Buffers"] = system.config.get_bool("rpcs3_read_colorbuffers")
        # Disable Vertex Cache
        rpcs3ymlconfig["Video"]["Disable Vertex Cache"] = system.config.get_bool("rpcs3_vertexcache")
        # Anisotropic Filtering
        rpcs3ymlconfig["Video"]["Anisotropic Filter Override"] = system.config.get_int("rpcs3_anisotropic", 0)
        # MSAA
        rpcs3ymlconfig["Video"]["MSAA"] = system.config.get("rpcs3_aa", "Auto")
        # ZCULL
        match system.config.get("rpcs3_zcull"):
            case "Approximate":
                rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = False
                rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = False
            case "Relaxed":
                rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = False
                rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = True
            case _:
                rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = True
                rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = False

        # Shader Precision
        rpcs3ymlconfig["Video"]["Shader Precision"] = system.config.get("rpcs3_shader", "High")
        # Internal resolution (CHANGE AT YOUR OWN RISK)
        rpcs3ymlconfig["Video"]["Resolution"] = "1280x720"
        # Resolution scaling
        rpcs3ymlconfig["Video"]["Resolution Scale"] = system.config.get_int("rpcs3_resolution_scale", 100)
        # Resolution scale threshold
        rpcs3ymlconfig["Video"]["Minimum Scalable Dimension"] = int(system.config.get_float("rpcs3_resolution_scale_threshold", 16))
        # Output Scaling
        rpcs3ymlconfig["Video"]["Output Scaling Mode"] = system.config.get("rpcs3_scaling", "Bilinear")
        # Number of Shader Compilers
        rpcs3ymlconfig["Video"]["Shader Compiler Threads"] = system.config.get_int("rpcs3_num_compilers", 0)
        # Multithreaded RSX
        rpcs3ymlconfig["Video"]["Multithreaded RSX"] = system.config.get_bool("rpcs3_rsx")
        # Write Depth Buffer
        rpcs3ymlconfig["Video"]["Write Depth Buffer"] = system.config.get_bool("rpcs3_write_depth_buffers")
        # Force CPU blit emulation
        rpcs3ymlconfig["Video"]["Force CPU Blit"] = system.config.get_bool("rpcs3_force_cpu_blit_emulation")

        if "Vulkan" not in rpcs3ymlconfig["Video"]:
            rpcs3ymlconfig["Video"]["Vulkan"] = {}

        # Async Texture Streaming
        rpcs3ymlconfig["Video"]["Vulkan"]["Asynchronous Texture Streaming 2"] = system.config.get_bool("rpcs3_async_texture")

        # -= [Audio] =-
        # defaults
        rpcs3ymlconfig["Audio"]["Renderer"] = "Cubeb"
        rpcs3ymlconfig["Audio"]["Master Volume"] = 100
        # audio format
        rpcs3ymlconfig["Audio"]["Audio Format"] = system.config.get("rpcs3_audio_format", "Automatic")
        # convert to 16 bit
        rpcs3ymlconfig["Audio"]["Convert to 16 bit"] = system.config.get_bool("rpcs3_audio_16bit")
        # audio buffering
        rpcs3ymlconfig["Audio"]["Enable Buffering"] = system.config.get_bool("rpcs3_audiobuffer", True)
        # audio buffer duration
        rpcs3ymlconfig["Audio"]["Desired Audio Buffer Duration"] = system.config.get_int("rpcs3_audiobuffer_duration", 100)
        # time stretching
        if system.config.get_bool("rpcs3_timestretch"):
            rpcs3ymlconfig["Audio"]["Enable Time Stretching"] = True
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = True
        else:
            rpcs3ymlconfig["Audio"]["Enable Time Stretching"] = False
        # time stretching threshold
        rpcs3ymlconfig["Audio"]["Time Stretching Threshold"] = system.config.get_int("rpcs3_timestretch_threshold", 75)

        # -= [Input/Output] =-
        # gun stuff
        if system.config.use_guns and guns:
            rpcs3ymlconfig["Input/Output"]["Move"] = "Gun"
            rpcs3ymlconfig["Input/Output"]["Camera"] = "Fake"
            rpcs3ymlconfig["Input/Output"]["Camera type"] = "PS Eye"
            self._generateGunConfig()
        # Gun crosshairs
        rpcs3ymlconfig["Input/Output"]["Show move cursor"] = system.config.get_bool("rpcs3_crosshairs")

        # -= [Miscellaneous] =-
        rpcs3ymlconfig["Miscellaneous"]["Exit RPCS3 when process finishes"] = True
        rpcs3ymlconfig["Miscellaneous"]["Start games in fullscreen mode"] = True
        rpcs3ymlconfig["Miscellaneous"]["Show shader compilation hint"] = False
        rpcs3ymlconfig["Miscellaneous"]["Prevent display sleep while running games"] = True
        rpcs3ymlconfig["Miscellaneous"]["Show trophy popups"] = False

        # -= [System] =-
        # Arcade titles require a zeroed Console PSID; keep it unset for everything else.
        if arcade_title:
            rpcs3ymlconfig["System"]["Console PSID"] = 0
        else:
            rpcs3ymlconfig["System"].pop("Console PSID", None)

        with RPCS3_CONFIG.open("w") as file:
            yaml = YAML(pure=True)
            yaml.default_flow_style = False
            yaml.dump(rpcs3ymlconfig, file)

        dev_hdd0 = f"{rom_dev_hdd0 if is_psn_squashfs else RPCS3_DEV_HDD0_DIR}/"
        # For a PSN squashfs, redirect /dev_hdd1/ to the overlay when it ships one.
        dev_hdd1 = f"{rom_dev_hdd1 if is_psn_squashfs and rom_dev_hdd1.is_dir() else '$(EmulatorDir)dev_hdd1'}/"

        rpcs3vfsconfig: dict[str, Any] = {
            "$(EmulatorDir)": "",
            "/dev_hdd0/": dev_hdd0,
            "/dev_hdd1/": dev_hdd1,
            "/dev_flash/": "$(EmulatorDir)dev_flash/",
            "/dev_flash2/": "$(EmulatorDir)dev_flash2/",
            "/dev_flash3/": "$(EmulatorDir)dev_flash3/",
            "/dev_bdvd/": "$(EmulatorDir)dev_bdvd/",
            "/games/": "$(EmulatorDir)games/",
            "/app_home/": "",
            "/dev_usb***/": Rpcs3Generator._buildUsbConfig(rom, is_psn_squashfs, usb_tuning or {}),
        }

        with RPCS3_VFS_CONFIG.open("w") as file:
            yaml = YAML(pure=True)
            yaml.default_flow_style = False
            yaml.dump(rpcs3vfsconfig, file)

        # arcade titles need their game patches imported and the USIO board input mapping;
        # Taiko titles also need the matching patch enable state
        if arcade_title:
            Rpcs3Generator._mergePatchFile(RPCS3_IMPORTED_PATCH, _ARCADE_PATCHES)
            RPCS3_USIO_CONFIG.write_text(_USIO_CONFIG, encoding="utf-8")
        if arcade_title and arcade_title.startswith("Taiko no Tatsujin"):
            Rpcs3Generator._mergePatchFile(RPCS3_PATCH_CONFIG, _TAIKO_PATCH_CONFIG)

        # copy icon files to config
        icon_target = RPCS3_CONFIG_DIR / 'Icons'
        mkdir_if_not_exists(icon_target)
        shutil.copytree('/usr/share/rpcs3/Icons/', icon_target, dirs_exist_ok=True, copy_function=shutil.copy2)

        # determine the rom name

        if rom.suffix == ".psn":
            romName: Path | None = None

            with rom.open() as fp:
                for line in fp:
                    if len(line) >= 9:
                        romName = RPCS3_DEV_HDD0_DIR / "game" / line.strip().upper() / "USRDIR" / "EBOOT.BIN"

            if romName is None:
                raise BatoceraException(f'No game ID found in {rom}')

        elif is_psn_squashfs:
            # rom is /var/run/overlays/<stem>; dev_hdd0 is redirected there via vfs.yml.
            # Scan for the game ID directory and pass EBOOT.BIN directly to RPCS3.
            romName = None
            for game_id_dir in rom_game_dir.iterdir():
                eboot = game_id_dir / "USRDIR" / "EBOOT.BIN"
                if eboot.exists():
                    romName = eboot
                    break
            if romName is None:
                raise BatoceraException(f'No PSN game found in squashfs {rom}')

        elif rom.suffix.lower() == ".iso":
            romName = rom
        elif configure_emulator(rom):
            romName: Path | None = None
        else:
            romName = rom / "PS3_GAME" / "USRDIR" / "EBOOT.BIN"

        if romName:
            commandArray: list[Path | str] = [RPCS3_BIN, romName]
        else:
            commandArray: list[Path | str] = [RPCS3_BIN]

        if not system.config.get_bool("rpcs3_gui") and romName:
            commandArray.append("--no-gui")

        # firmware not installed and available : instead of starting the game, install it
        if Rpcs3Generator.getFirmwareVersion() is None and (BIOS / "PS3UPDAT.PUP").exists():
            commandArray = [RPCS3_BIN, "--installfw", BIOS / "PS3UPDAT.PUP"]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_CACHE_HOME": CACHE
            }
        )

    def writesToRom(self, config) -> bool:
        return True

    def _generateGunConfig(self):
        # D-Pad mapping is face buttons of the PS Move △ =up ✕ =down □ =left ○ =right
        gunMapping = {
            "T": 1,
            "Move": 2,
            "Start": 3,
            "Select": 4,
            "Triangle": 8,
            "Cross": 9,
            "Square": 10,
            "Circle": 11
        }
        with (RPCS3_CONFIG_DIR / "gem_gun.yml").open("w") as f:
            for player in range(1, 5):
                f.write(f"Player {player}:\n")
                for psmove, gun_num in gunMapping.items():
                    f.write(f"  {psmove}: Gun Button {gun_num}\n")

    @staticmethod
    def _readSfoTitle(sfo: Path) -> str | None:
        # Minimal PSF (PARAM.SFO) reader: return the TITLE value (a UTF-8 string entry).
        try:
            data = sfo.read_bytes()
        except OSError:
            return None
        if len(data) < 20 or data[:4] != b"\x00PSF":
            return None
        key_table_start, data_table_start, entries = struct.unpack_from("<III", data, 8)
        for i in range(entries):
            key_offset, _fmt, value_len, _value_max, data_offset = struct.unpack_from("<HHIII", data, 20 + i * 16)
            key_start = key_table_start + key_offset
            key_end = data.index(b"\x00", key_start)
            if data[key_start:key_end] != b"TITLE":
                continue
            raw = data[data_table_start + data_offset:data_table_start + data_offset + value_len]
            return raw.split(b"\x00", 1)[0].decode("utf-8", "replace") or None
        return None

    @staticmethod
    def _deepMergeMissing(dst: dict[str, Any], src: dict[str, Any]) -> bool:
        # Recursively add keys from src missing in dst; never overwrite an existing value.
        changed = False
        for key, value in src.items():
            if key not in dst:
                dst[key] = value
                changed = True
            elif isinstance(dst[key], dict) and isinstance(value, dict):
                if Rpcs3Generator._deepMergeMissing(dst[key], value):
                    changed = True
        return changed

    @staticmethod
    def _mergePatchFile(target: Path, data: dict[str, Any]) -> None:
        # Create the target patch file from data if absent, otherwise merge in only the keys
        # not yet present (preserving the user's own patches and enable/disable state).
        yaml = YAML()  # round-trip: preserve the user's file formatting and the hex literals
        mkdir_if_not_exists(target.parent)
        if not target.is_file():
            with target.open("w") as stream:
                yaml.dump(data, stream)
            return

        with target.open("r") as stream:
            existing = yaml.load(stream) or {}
        if Rpcs3Generator._deepMergeMissing(existing, data):
            with target.open("w") as stream:
                yaml.dump(existing, stream)

    @staticmethod
    def _matchArcadeTitle(rom: Path, is_psn_squashfs: bool) -> str | None:
        # Match an arcade PSN squashfs title via its PARAM.SFO TITLE (a key of _ARCADE_USB_CONFIG).
        # Arcade titles all ship under the same SCEEXE000 title-id.
        if not is_psn_squashfs:
            return None
        title = Rpcs3Generator._readSfoTitle(rom / "dev_hdd0" / "game" / "SCEEXE000" / "PARAM.SFO")
        if title and title in _ARCADE_USB_CONFIG:
            _logger.debug("Matched RPCS3 arcade title '%s'", title)
            return title
        return None

    @staticmethod
    def _buildUsbConfig(rom: Path, is_psn_squashfs: bool, tuning: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
        # Build the full /dev_usb***/ block (slots 000-007). Every tuned slot (one carrying
        # an emulated USB I/O board Serial/VID/PID) reads its data from the overlay's single
        # dev_usb000 folder, so its Path defaults there; a slot may override "Path" (e.g. ""
        # for a pure passthrough device). Untuned dev_usb000 keeps the RPCS3 default mount
        # (or the overlay folder if shipped) and the rest stay empty.
        overlay_usb000_dir = rom / "dev_usb000"
        overlay_usb000 = f"{overlay_usb000_dir}/"
        # the tuned I/O board needs the folder to exist; create it in the writable overlay
        if tuning and is_psn_squashfs:
            mkdir_if_not_exists(overlay_usb000_dir)
        usb: dict[str, dict[str, str]] = {}
        for index in range(8):
            slot = f"/dev_usb00{index}"
            tuned = tuning.get(slot, {})
            usb_dir = rom / f"dev_usb00{index}"
            if tuned:
                path = tuned.get("Path", overlay_usb000 if is_psn_squashfs else "")
            elif is_psn_squashfs and usb_dir.is_dir():
                path = f"{usb_dir}/"
            elif index == 0:
                path = "$(EmulatorDir)dev_usb000/"
            else:
                path = ""
            usb[slot] = {"Path": path, "Serial": tuned.get("Serial", ""),
                         "VID": tuned.get("VID", ""), "PID": tuned.get("PID", "")}
        return usb

    @staticmethod
    def getClosestRatio(gameResolution: Resolution) -> str:
        screenRatio = gameResolution["width"] / gameResolution["height"]
        if screenRatio < 1.6:
            return "4:3"
        return "16:9"

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9

    @staticmethod
    def getFirmwareVersion() -> str | None:
        try:
            with (RPCS3_CONFIG_DIR / "dev_flash" / "vsh" / "etc" / "version.txt").open("r") as stream:
                lines = stream.readlines()
            for line in lines:
                matches = re.match("^release:(.*):", line)
                if matches:
                    return matches[1]
        except Exception:
            return None
        return None
