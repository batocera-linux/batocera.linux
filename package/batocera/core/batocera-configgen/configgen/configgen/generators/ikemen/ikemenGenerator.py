from __future__ import annotations

import json
import logging
import os
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from batocera_launch.emulators.ikemen import _nvidia_prime_environment
from batocera_launch_wine import wine

from ... import Command
from ...batoceraPaths import ensure_parents_and_open
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from collections.abc import Generator as Iterator

    from ...types import HotkeysContext, Resolution

_logger = logging.getLogger(__name__)

def get_windows_exe(rom: Path, /) -> Path | None:
    if not (rom / "autorun.cmd").is_file():
        return None

    return wine.get_game_exe(rom)

def get_wine_runner() -> wine.Runner:
    return wine.Runner('wine-proton', "ikemen")

_IKEMEN_SYSTEM_BINARY: Final = Path("/usr/bin/ikemen")

_IKEMEN_GAME_BINARY: Final = "ikemen_go_linux"

def get_linux_binary(game_dir: Path, /) -> Path:

    binary = next((entry for entry in game_dir.glob("*") if entry.name.lower() == _IKEMEN_GAME_BINARY), None)

    if binary is None or not binary.is_file():
        return _IKEMEN_SYSTEM_BINARY

    if not os.access(binary, os.X_OK):
        try:
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError as e:
            _logger.warning("%s can't be made executable (%s), running our own binary instead", binary, e)
            return _IKEMEN_SYSTEM_BINARY

        if not os.access(binary, os.X_OK):
            _logger.warning("%s stayed non executable, running our own binary instead", binary)
            return _IKEMEN_SYSTEM_BINARY

        _logger.info("made %s executable", binary)

    _logger.debug("linux binary: %s", binary)

    return binary

Keymapping =[
        {
            "Joystick": -1,
            "Buttons": [
                "UP",
                "DOWN",
                "LEFT",
                "RIGHT",
                "a",
                "s",
                "d",
                "z",
                "x",
                "c",
                "RETURN",
                "f",
                "v",
                "q"
            ]
        },
        {
            "Joystick": -1,
            "Buttons": [
                "KP_8",
                "KP_5",
                "KP_4",
                "KP_6",
                "p",
                "LBRACKET",
                "RBRACKET",
                "SEMICOLON",
                "QUOTE",
                "BACKSLASH",
                "SLASH",
                "o",
                "l",
                "PERIOD"
            ]
        },
        {
            "Joystick": -1,
            "Buttons": [
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used"
            ]
        },
        {
            "Joystick": -1,
            "Buttons": [
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used"
            ]
        }
    ]

Joymapping =[
        {
            "Joystick": 0,
            "Buttons": [
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used"
            ]
        },
        {
            "Joystick": 1,
            "Buttons": [
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used"
            ]
        },
        {
            "Joystick": 2,
            "Buttons": [
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used"
            ]
        },
        {
            "Joystick": 3,
            "Buttons": [
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used",
                "Not used"
            ]
        }
    ]

# the Buttons arrays above are positional, config.ini names those fourteen in order
_BUTTON_NAMES: Final = (
    "up", "down", "left", "right", "a", "b", "c", "x", "y", "z", "start", "d", "w", "menu",
)

def write_json_config(config_path: Path, resolution: Resolution, /, *, scale_internal_resolution: bool) -> None:
    conf: dict[str, object] = {}

    if config_path.is_file():
        try:
            with config_path.open() as c:
                conf = json.load(c)
        except Exception:
            # a config we can't read is left alone, the game's own paths live in it
            _logger.warning("%s could not be read, leaving it as it is", config_path)
            return

    # Joystick configuration seems completely broken in 0.98.2 Linux
    # so let's force keyboad and use a pad2key
    conf["KeyConfig"] = Keymapping
    conf["JoystickConfig"] = Joymapping
    conf["Fullscreen"] = True

    conf["FullscreenWidth"] = resolution["width"]
    conf["FullscreenHeight"] = resolution["height"]

    if scale_internal_resolution:
        conf["GameWidth"] = resolution["width"]
        conf["GameHeight"] = resolution["height"]

    js_out = json.dumps(conf, indent=2)
    with ensure_parents_and_open(config_path, "w") as jout:
        jout.write(js_out)

def write_ini_config(config_path: Path, resolution: Resolution, /, *, scale_internal_resolution: bool) -> None:
    video = {
        "Fullscreen": "1",
        "WindowWidth": str(resolution["width"]),
        "WindowHeight": str(resolution["height"]),
    }

    if scale_internal_resolution:
        video["GameWidth"] = str(resolution["width"])
        video["GameHeight"] = str(resolution["height"])

    wanted: dict[str, dict[str, str]] = {"Video": video}

    for section, mapping in (("Keys", Keymapping), ("Joystick", Joymapping)):
        for player, player_config in enumerate(mapping, start=1):
            wanted[f"{section}_P{player}"] = {
                "Joystick": str(player_config["Joystick"]),
                **dict(zip(_BUTTON_NAMES, cast('list[str]', player_config["Buttons"]), strict=True)),
            }

    lowered = {
        section.lower(): {key.lower(): value for key, value in values.items()}
        for section, values in wanted.items()
    }

    original = config_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()

    lines: list[str] = []
    values: dict[str, str] | None = None

    for line in original:
        stripped = line.strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            values = lowered.get(stripped[1:-1].lower())
        elif values and not stripped.startswith(";"):
            key, separator, _ = line.partition("=")
            if separator and (value := values.get(key.strip().lower())) is not None:
                line = f"{key}= {value}"

        lines.append(line)

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

class IkemenGenerator(Generator):

    def writesToRom(self, config) -> bool:
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ikemen",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC" }
        }

    @contextmanager
    def running(self, config, rom) -> Iterator[None]:
        # a game of its own leaves nothing behind, one through wine leaves a wineserver
        windows = get_windows_exe(rom) is not None
        try:
            yield
        finally:
            if windows:
                get_wine_runner().stop()

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        game_dir = wine.get_game_dir(rom)
        game_exe = get_windows_exe(rom)
        ikemen_binary = get_linux_binary(game_dir)

        save_dir = game_dir / "save"

        scale_internal_resolution = system.config.get_bool("scale_internal_resolution")

        #since December 2024, ikemen use config.ini
        if (ini_config := save_dir / "config.ini").is_file():
            write_ini_config(ini_config, gameResolution, scale_internal_resolution=scale_internal_resolution)
        elif (json_config := save_dir / "config.json").is_file() or (game_exe is None and ikemen_binary == _IKEMEN_SYSTEM_BINARY):
            write_json_config(json_config, gameResolution, scale_internal_resolution=scale_internal_resolution)
        else:
            _logger.warning(
                "%s ships no save/config.ini nor save/config.json, leaving the controls to its own engine",
                rom
            )

        if game_exe is None:
            environment: dict[str, str | Path] = {
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
            }
            environment.update(_nvidia_prime_environment())

            return Command.Command(array=[ikemen_binary], env=environment)

        wine_runner = get_wine_runner()
        wine_runner.create_or_update_prefix()

        wine_runner.install_wine_trick('openal')
        wine_runner.install_wine_trick('corefonts')

        # nvapi is nvidia only and an ikemen game never asks for it
        environment = wine_runner.get_environment()
        environment.update(wine.display_environment())
        environment.update(wine.dxvk_environment(wine_runner))
        environment.update(wine.nvidia_prime_environment())

        return Command.Command(
            array=wine_runner.game_command(game_exe),
            env=environment
        )

    def executionDirectory(self, config, rom):
        return wine.get_game_dir(rom)
