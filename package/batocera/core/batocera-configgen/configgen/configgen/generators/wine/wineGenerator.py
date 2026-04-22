from __future__ import annotations

import json
import logging
import os
import subprocess
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger("ESLog")

# ─── Gun button mapping ────────────────────────────────────
#
# Virtual lightgun button layout (universal Batocera standard):
#   BTN_LEFT   = Trigger          (passthrough via X11)
#   BTN_RIGHT  = Action/Secondary (passthrough via X11)
#   BTN_MIDDLE = Start            (mapped per player)
#   BTN_1      = Select/Coin      (mapped per player)
#   BTN_2      = Sub1             (unmapped by default)
#   BTN_3      = Sub2             (unmapped by default)
#   BTN_4      = Sub3             (unmapped by default)
#   BTN_5..8   = D-Pad            (shared across all players)

PLAYER_MAPPING = [
    {"BTN_MIDDLE": "KEY_1", "BTN_1": "KEY_5"},   # P1: Start=1, Coin=5
    {"BTN_MIDDLE": "KEY_2", "BTN_1": "KEY_6"},   # P2: Start=2, Coin=6
    {"BTN_MIDDLE": "KEY_3", "BTN_1": "KEY_7"},   # P3: Start=3, Coin=7
    {"BTN_MIDDLE": "KEY_4", "BTN_1": "KEY_8"},   # P4: Start=4, Coin=8
]

SHARED_MAPPING = {
    "BTN_2":  None,
    "BTN_3":  None,
    "BTN_4":  None,
    "BTN_5":  "KEY_UP",
    "BTN_6":  "KEY_DOWN",
    "BTN_7":  "KEY_LEFT",
    "BTN_8":  "KEY_RIGHT",
}

GUN_CONFIG_PATH = "/var/run/wine-guns.json"

# ─── DemulShooter game detection ───────────────────────────
#
# Maps BepInEx plugin DLL prefix to ds-bridge game format.
# DLL naming: {Prefix}_BepInEx_DemulShooter_Plugin.dll

DEMULSHOOTER_GAMES = {
    "PointBlankX":       "pbx",
    "Drakon":            "pbx",
    "NerfArcade":        "pbx",
    "RabbidsHollywood":  "rha",
    "WildWestShootout":  "wws",
    "TombRaider":        "tra",
    "OperationWolf":     "owr",
    "MIB":               "mib",
    "MissionImpossible": "mia",
    "NightHunter2":      "nha2",
    "MarsSortie":        "marss",
    "PVZ":               "pvz",
}


def _detect_demulshooter(rom_path):
    #Detect DemulShooter BepInEx plugin in the game directory.
    #Returns the game format string (e.g. "rha") or None.
    plugins_dir = os.path.join(rom_path, "BepInEx", "plugins")
    if not os.path.isdir(plugins_dir):
        return None

    for dll in glob(os.path.join(plugins_dir, "*_BepInEx_DemulShooter_Plugin.dll")):
        basename = os.path.basename(dll)
        prefix = basename.split("_BepInEx_DemulShooter_Plugin")[0]
        game_fmt = DEMULSHOOTER_GAMES.get(prefix)
        if game_fmt:
            eslog.info("Wine gun: DemulShooter detected: %s -> %s", prefix, game_fmt)
            return game_fmt

    return None


def _build_player_mapping(player_index, metadata):
    #Build the full mapping for one player
    mapping = dict(SHARED_MAPPING)

    if player_index < len(PLAYER_MAPPING):
        mapping.update(PLAYER_MAPPING[player_index])
    else:
        mapping.update(PLAYER_MAPPING[0])

    if metadata:
        for btn_name in list(mapping.keys()):
            player_key = "gun_p{}_{}".format(player_index + 1, btn_name.lower())
            override = metadata.get(player_key)

            if override is None:
                global_key = "gun_" + btn_name.lower()
                override = metadata.get(global_key)

            if override is not None:
                if override == "" or override.lower() == "none":
                    mapping[btn_name] = None
                else:
                    mapping[btn_name] = override.upper()
                    eslog.info("Wine gun P%d: override %s -> %s",
                               player_index + 1, btn_name, override.upper())

    return {k: v for k, v in mapping.items() if v is not None}


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

        if system.name == "windows":
            commandArray = ["batocera-wine", "windows", "play", rom]

            environment: dict[str, str | Path] = {}

            # ── Language ──
            try:
                language = subprocess.check_output(
                    "batocera-settings-get system.language",
                    shell=True, text=True
                ).strip()
            except subprocess.CalledProcessError:
                language = 'en_US'
            if language:
                environment.update({
                    "LANG": language + ".UTF-8",
                    "LC_ALL": language + ".UTF-8"
                })

            # ── SDL controller config ──
            if system.config.get_bool("sdl_config", True):
                environment.update({
                    "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                    "SDL_JOYSTICK_HIDAPI": "0"
                })

            # ── NVIDIA Vulkan ──
            if Path('/var/tmp/nvidia.prime').exists():
                variables_to_remove = [
                    '__NV_PRIME_RENDER_OFFLOAD',
                    '__VK_LAYER_NV_optimus',
                    '__GLX_VENDOR_LIBRARY_NAME'
                ]
                for variable_name in variables_to_remove:
                    if variable_name in os.environ:
                        del os.environ[variable_name]
                environment.update({
                    'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/nvidia_icd.i686.json',
                })

            # ── Light gun support via rawinput ──
            if system.config.use_guns and guns:
                self._setup_guns(guns, metadata, rom, gameResolution)
                environment.update({
                    "WINE_FORCE_RAWINPUT": "1",
                    "WINE_RAWMOUSE_COUNT": str(len(guns))
                })

            return Command.Command(array=commandArray, env=environment)

        raise BatoceraException("Invalid system: " + system.name)

    def getMouseMode(self, config, rom):
        return config.get_bool('force_mouse')

    # ─── Light gun setup ───

    def _setup_guns(self, guns, metadata, rom, gameResolution):
        #Write per-player gun config + optional DemulShooter bridge config.
        num_guns = len(guns)
        eslog.info("Wine: %d light gun(s) detected", num_guns)

        gun_configs = []
        for i in range(num_guns):
            mapping = _build_player_mapping(i, metadata)
            gun_configs.append({"player": i + 1, "mapping": mapping})
            eslog.info("Wine gun P%d: %s", i + 1,
                       ", ".join("{}->{}".format(k, v) for k, v in mapping.items()))

        config = {"guns": gun_configs}

        ds_game = _detect_demulshooter(str(rom))
        if ds_game:
            width = gameResolution.get("width", 1920) if gameResolution else 1920
            height = gameResolution.get("height", 1080) if gameResolution else 1080
            config["ds_bridge"] = {
                "game": ds_game,
                "width": int(width),
                "height": int(height),
            }
            eslog.info("Wine gun: DemulShooter bridge: game=%s %dx%d",
                       ds_game, width, height)

        try:
            with open(GUN_CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            eslog.info("Wine gun: config written to %s", GUN_CONFIG_PATH)
        except Exception as e:
            eslog.error("Wine gun: failed to write config: %s", e)
