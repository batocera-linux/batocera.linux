from __future__ import annotations

import logging
import platform
import shutil
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser

from ... import Command
from ...batoceraPaths import (
    CONFIGS,
    LOGS,
    SAVES,
    SCREENSHOTS,
    ensure_parents_and_open,
    mkdir_if_not_exists,
)
from ...controller import Controller, Controllers, generate_sdl_game_controller_config
from ...gun import Guns, guns_need_crosses
from ...utils import vulkan
from ..Generator import Generator

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

SUPERMODEL_SHARE: Final = Path("/usr/share/supermodel")
SUPERMODEL_CONFIG: Final = CONFIGS / "supermodel"
SUPERMODEL_SAVES: Final = SAVES / "supermodel"
SUPERMODEL_SCREENSHOTS: Final = SCREENSHOTS / "supermodel"


def get_pad_input(
    pad: Controller | None,
    name_or_names: str | list[str],
    full_axis: bool = False,
    force_pos: bool = False,
) -> str | None:

    if not pad or not hasattr(pad, "inputs"):
        return None

    if isinstance(name_or_names, str):
        names = [name_or_names]
    else:
        names = name_or_names

    input_obj = None

    for name in names:
        if name in pad.inputs:
            input_obj = pad.inputs[name]
            break

    if not input_obj:
        return None

    player_num = getattr(pad, "player", 1)
    prefix = f"JOY{player_num}"

    if input_obj.type == "button":
        btn_num = int(input_obj.id) + 1
        return f"{prefix}_BUTTON{btn_num}"

    if input_obj.type == "axis":
        axis_id = int(input_obj.id)
        axis_map = {
            0: "XAXIS",
            1: "YAXIS",
            2: "ZAXIS",
            3: "RXAXIS",
            4: "RYAXIS",
            5: "RZAXIS",
        }
        axis_name = axis_map.get(axis_id, f"AXIS{axis_id}")

        if full_axis:
            return f"{prefix}_{axis_name}"

        if force_pos:
            return f"{prefix}_{axis_name}_POS"

        if str(input_obj.value) in ("1", "+1"):
            direction = "_POS"
        else:
            direction = "_NEG"
        return f"{prefix}_{axis_name}{direction}"

    if input_obj.type == "hat":
        hat_map = {"1": "UP", "2": "RIGHT", "4": "DOWN", "8": "LEFT"}
        hat_dir = hat_map.get(str(input_obj.value), "UP")
        hat_num = int(input_obj.id) + 1
        return f"{prefix}_POV{hat_num}_{hat_dir}"

    return None


class SupermodelGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "supermodel",
            "keys": {
                "exit": "KEY_ESC",
                "menu": ["KEY_LEFTALT", "KEY_P"],
                "pause": ["KEY_LEFTALT", "KEY_P"],
                "reset": ["KEY_LEFTALT", "KEY_R"],
                "save_state": "KEY_F5",
                "restore_state": "KEY_F7",
                "next_state": "KEY_F6",
            },
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Detect if we are running on an ARM system (uses GLES)
        is_arm = platform.machine().startswith(("arm", "aarch"))

        # Configure audio channels (defaults to Stereo / 2-channel)
        audio_channels = system.config.get("m3_audio_channels", "2")
        commandArray: list[str | Path] = ["supermodel", "-fullscreen", f"-channels={audio_channels}"]

        # Graphics Backend selection (OpenGL or Vulkan)
        graphics_backend = system.config.get("graphics_backend")
        if graphics_backend == "Vulkan":
            if vulkan.is_available():
                vulkan_version = vulkan.get_version()
                if vulkan_version >= "1.1":
                    _logger.debug("Vulkan driver is available. Using Vulkan version: %s", vulkan_version)
                    commandArray.append("-graphics-backend=Vulkan")
                else:
                    _logger.debug("Vulkan version %s is lower than 1.1! Falling back to OpenGL.", vulkan_version)
                    commandArray.append("-graphics-backend=OpenGL")
            else:
                _logger.debug("*** Vulkan driver is not available on the system! Falling back to OpenGL. ***")
                commandArray.append("-graphics-backend=OpenGL")
        elif graphics_backend:
            commandArray.append(f"-graphics-backend={graphics_backend}")

        # 3D Engine selection (force New3D on ARM/GLES devices to prevent exit)
        if is_arm or system.config.get("engine3D") == "new3d":
            commandArray.append("-new3d")
        else:
            commandArray.extend(["-multi-texture", "-legacy3d"])

        # SCSP Sound Engine selection
        if system.config.get("m3_scsp") == "legacy":
            commandArray.append("-legacy-scsp")
        else:
            commandArray.append("-new-scsp")

        # Widescreen
        if system.config.get_bool("m3_wideScreen"):
            commandArray.append("-wide-screen")
            commandArray.append("-wide-bg")
            system.config["bezel"] = "none"

        # Quad rendering (Automatically disabled on ARM/GLES due to performance constraints)
        if not is_arm and system.config.get_bool("quadRendering"):
            commandArray.append("-quad-rendering")

        # Supersampling
        if (ss := system.config.get("m3_supersampling")) and ss != "1":  # 1 represents "Off"
            commandArray.append(f"-ss={ss}")

        # Render scale (defaults to 1 for ARM, 0 for x86_64)
        default_renderscale = "1" if is_arm else "0"
        renderscale = system.config.get("m3_renderscale", default_renderscale)
        if renderscale != "0":
            commandArray.append(f"-render-scale={renderscale}")

        # Stretch to fill
        if system.config.get_bool("m3_stretch"):
            commandArray.append("-stretch")

        # Vsync
        if system.config.get("m3_vsync") == "0":
            commandArray.append("-no-vsync")
        else:
            commandArray.append("-vsync")

        # Accurate refresh rate (true model 3 hz)
        if system.config.get_bool("m3_true_hz"):
            commandArray.append("-true-hz")

        # Disable white flashes
        if system.config.get_bool("m3_no_white_flash"):
            commandArray.append("-no-white-flash")

        # Crosshairs
        if crosshairs := system.config.get("crosshairs"):
            commandArray.append(f"-crosshairs={crosshairs}")
        else:
            if guns_need_crosses(guns):
                if len(guns) == 1:
                    commandArray.append("-crosshairs=1")
                else:
                    commandArray.append("-crosshairs=3")

        # Force feedback
        if system.config.get_bool("forceFeedback"):
            commandArray.append("-force-feedback")

        # PowerPC frequency
        if freq := system.config.get("ppcFreq"):
            commandArray.append(f"-ppc-frequency={freq}")

        # CRT colour
        if color := system.config.get("crt_colour"):
            commandArray.append(f"-crtcolors={color}")

        # Upscale mode
        if upscale_mode := system.config.get("upscale_mode"):
            commandArray.append(f"-upscalemode={upscale_mode}")

        # Set Resolution
        commandArray.append(f"-res={gameResolution['width']},{gameResolution['height']}")
        # Logs
        commandArray.extend([f"-log-output={LOGS / 'Supermodel.log'}", rom])
        # Copy nvram files as needed
        copy_nvram_files()
        # Copy gun asset files as needed
        copy_asset_files()
        # Copy xml files as needed
        copy_xml()

        # Do the controller configs
        configPadsIni(system, rom, guns, playersControllers)

        return Command.Command(
            array=commandArray,
            env={
                "SUPERMODEL_CONFIG_PATH": SUPERMODEL_CONFIG,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
            },
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get_bool("m3_stretch"):
            return 16 / 9
        if config.get("m3_wideScreen") == "1":
            return 16 / 9
        return 4 / 3


def copy_nvram_files():
    sourceDir = SUPERMODEL_SHARE / "NVRAM"
    targetDir = SUPERMODEL_SAVES / "NVRAM"

    mkdir_if_not_exists(targetDir)

    # create nv files which are in source and have a newer modification time than in target
    for sourceFile in sourceDir.iterdir():
        if sourceFile.suffix == ".nv":
            targetFile = targetDir / sourceFile.name
            if not targetFile.exists():
                # if the target file doesn't exist, just copy the source file
                copyfile(sourceFile, targetFile)
            else:
                # if the target file exists and has an older modification time than the source file, create a backup and copy the new file
                if sourceFile.stat().st_mtime > targetFile.stat().st_mtime:
                    backupFile = targetFile.with_suffix(f"{targetFile.suffix}.bak")
                    if backupFile.exists():
                        backupFile.unlink()
                    targetFile.rename(backupFile)
                    copyfile(sourceFile, targetFile)


def copy_asset_files():
    sourceDir = SUPERMODEL_SHARE / "Assets"
    targetDir = SUPERMODEL_CONFIG / "Assets"
    if not sourceDir.exists():
        return
    mkdir_if_not_exists(targetDir)

    # create asset files which are in source and have a newer modification time than in target
    for sourceFile in sourceDir.iterdir():
        targetFile = targetDir / sourceFile.name
        if not targetFile.exists() or sourceFile.stat().st_mtime > targetFile.stat().st_mtime:
            copyfile(sourceFile, targetFile)


def copy_xml():
    source_path = SUPERMODEL_SHARE / "Games.xml"
    dest_path = SUPERMODEL_CONFIG / "Games.xml"
    mkdir_if_not_exists(dest_path.parent)
    if not dest_path.exists() or source_path.stat().st_mtime > dest_path.stat().st_mtime:
        shutil.copy2(source_path, dest_path)


def configPadsIni(system: Emulator, rom: Path, guns: Guns, playersControllers: Controllers) -> None:

    templateFile = SUPERMODEL_SHARE / "Supermodel.ini.template"
    targetFile = SUPERMODEL_CONFIG / "Supermodel.ini"

    # Ensure required target directories exist
    mkdir_if_not_exists(SUPERMODEL_SAVES / "Saves")
    mkdir_if_not_exists(SUPERMODEL_SCREENSHOTS)
    mkdir_if_not_exists(SUPERMODEL_CONFIG / "Analysis")

    # template
    templateConfig = CaseSensitiveConfigParser(interpolation=None)
    templateConfig.read(templateFile, encoding="utf_8_sig")

    # target
    targetConfig = CaseSensitiveConfigParser(interpolation=None)

    for section in templateConfig.sections():
        targetConfig.add_section(section)
        for key, value in templateConfig.items(section):
            targetConfig.set(section, key, value)

    if not targetConfig.has_section("Global"):
        targetConfig.add_section("Global")

    # Batocera directory path configuration
    targetConfig.set("Global", "AnalysisPath", str(SUPERMODEL_CONFIG / "Analysis"))
    targetConfig.set("Global", "NVRAMPath", str(SUPERMODEL_SAVES / "NVRAM"))
    targetConfig.set("Global", "SavesPath", str(SUPERMODEL_SAVES / "Saves"))
    targetConfig.set("Global", "ScreenshotsPath", str(SUPERMODEL_SCREENSHOTS))
    targetConfig.set("Global", "AssetsPath", str(SUPERMODEL_CONFIG / "Assets"))
    targetConfig.set("Global", "LogPath", str(LOGS))

    # Network Outputs configuration (MAME-compatible outputs)
    m3_outputs = system.config.get("m3_outputs", "none")
    targetConfig.set("Global", "Outputs", m3_outputs)

    if m3_outputs == "net":
        outputs_lf = "true" if system.config.get_bool("m3_outputs_lf") else "false"
        targetConfig.set("Global", "OutputsWithLF", outputs_lf)

        tcp_port = system.config.get("m3_outputs_tcp", "0")
        targetConfig.set("Global", "OutputsTCPPort", tcp_port)

        udp_port = system.config.get("m3_outputs_udp", "0")
        targetConfig.set("Global", "OutputsUDPBroadcastPort", udp_port)
    else:
        targetConfig.set("Global", "Outputs", "none")

    # Locate Player 1 and Player 2 controllers
    pad1 = None
    pad2 = None

    if isinstance(playersControllers, dict):
        pad1 = playersControllers.get(1) or playersControllers.get("1")
        pad2 = playersControllers.get(2) or playersControllers.get("2")
    else:
        for pad in playersControllers:
            p_num = str(getattr(pad, "player", "1"))
            if p_num == "1" and not pad1:
                pad1 = pad
            elif p_num == "2" and not pad2:
                pad2 = pad

    def build_binding(default_keys: str, pad_bind: str | None) -> str:
        if pad_bind:
            # Prevent duplicate entries if pad_bind is already in default_keys
            if pad_bind in default_keys.split(","):
                return default_keys
            return f"{default_keys},{pad_bind}" if default_keys else pad_bind
        return default_keys

    p1_start: str | None = None
    p1_select: str | None = None
    p2_start: str | None = None
    p2_select: str | None = None

    # Dynamically bind Player 1
    if pad1:
        p1_start = get_pad_input(pad1, "start")
        p1_select = get_pad_input(pad1, "select")
        p1_up = get_pad_input(pad1, "up") or "JOY1_POV1_UP"
        p1_down = get_pad_input(pad1, "down") or "JOY1_POV1_DOWN"
        p1_left = get_pad_input(pad1, "left") or "JOY1_POV1_LEFT"
        p1_right = get_pad_input(pad1, "right") or "JOY1_POV1_RIGHT"

        p1_south = get_pad_input(pad1, "b") or "JOY1_BUTTON1"
        p1_east = get_pad_input(pad1, "a") or "JOY1_BUTTON2"
        p1_west = get_pad_input(pad1, "y") or "JOY1_BUTTON3"
        p1_north = get_pad_input(pad1, "x") or "JOY1_BUTTON4"

        p1_l1 = get_pad_input(pad1, ["pageup", "l1", "left_shoulder"]) or "JOY1_BUTTON5"
        p1_r1 = get_pad_input(pad1, ["pagedown", "r1", "right_shoulder"]) or "JOY1_BUTTON6"
        p1_l2 = get_pad_input(pad1, ["l2", "left_trigger"], force_pos=True) or "JOY1_ZAXIS_POS"
        p1_r2 = get_pad_input(pad1, ["r2", "right_trigger"], force_pos=True) or "JOY1_RZAXIS_POS"

        p1_lstick_x = get_pad_input(pad1, ["joystick1left", "joystick1right"], full_axis=True) or "JOY1_XAXIS"
        p1_lstick_y = get_pad_input(pad1, ["joystick1up", "joystick1down"], full_axis=True) or "JOY1_YAXIS"
        p1_rstick_x = get_pad_input(pad1, ["joystick2left", "joystick2right"], full_axis=True) or "JOY1_RXAXIS"
        p1_rstick_y = get_pad_input(pad1, ["joystick2up", "joystick2down"], full_axis=True) or "JOY1_RYAXIS"

        p1_rstick_left = get_pad_input(pad1, "joystick2left") or "JOY1_RXAXIS_NEG"
        p1_rstick_down = get_pad_input(pad1, "joystick2down") or "JOY1_RYAXIS_POS"
        p1_rstick_up = get_pad_input(pad1, "joystick2up") or "JOY1_RYAXIS_NEG"
        p1_rstick_right = get_pad_input(pad1, "joystick2right") or "JOY1_RXAXIS_POS"

        targetConfig.set("Global", "InputStart1", build_binding("KEY_1", p1_start or "JOY1_BUTTON8"))
        targetConfig.set("Global", "InputCoin1", build_binding("KEY_3", p1_select or "JOY1_BUTTON7"))

        targetConfig.set("Global", "InputJoyUp", build_binding("KEY_UP", p1_up))
        targetConfig.set("Global", "InputJoyDown", build_binding("KEY_DOWN", p1_down))
        targetConfig.set("Global", "InputJoyLeft", build_binding("KEY_LEFT", p1_left))
        targetConfig.set("Global", "InputJoyRight", build_binding("KEY_RIGHT", p1_right))

        targetConfig.set("Global", "InputPunch", build_binding("KEY_A", p1_west))
        targetConfig.set("Global", "InputKick", build_binding("KEY_S", p1_north))
        targetConfig.set("Global", "InputGuard", build_binding("KEY_D", p1_south))
        targetConfig.set("Global", "InputEscape", build_binding("KEY_F", p1_east))

        targetConfig.set("Global", "InputShift", build_binding("KEY_A", p1_south))
        targetConfig.set("Global", "InputBeat", build_binding("KEY_S", p1_west))
        targetConfig.set("Global", "InputCharge", build_binding("KEY_D", p1_north))
        targetConfig.set("Global", "InputJump", build_binding("KEY_F", p1_east))

        targetConfig.set("Global", "InputShortPass", build_binding("KEY_A", p1_south))
        targetConfig.set("Global", "InputLongPass", build_binding("KEY_S", p1_west))
        targetConfig.set("Global", "InputShoot", build_binding("KEY_D", p1_east))

        targetConfig.set("Global", "InputSteering", p1_lstick_x)
        targetConfig.set("Global", "InputAccelerator", build_binding("KEY_UP,JOY1_RZAXIS_POS", p1_r2))
        targetConfig.set("Global", "InputBrake", build_binding("KEY_DOWN,JOY1_ZAXIS_POS", p1_l2))

        targetConfig.set("Global", "InputGearShiftUp", build_binding("KEY_Y", p1_r1))
        targetConfig.set("Global", "InputGearShiftDown", build_binding("KEY_H", p1_l1))

        targetConfig.set("Global", "InputGearShift1", build_binding("KEY_Q", p1_rstick_left))
        targetConfig.set("Global", "InputGearShift2", build_binding("KEY_W", p1_rstick_down))
        targetConfig.set("Global", "InputGearShift3", build_binding("KEY_E", p1_rstick_up))
        targetConfig.set("Global", "InputGearShift4", build_binding("KEY_R", p1_rstick_right))

        targetConfig.set("Global", "InputVR1", build_binding("KEY_A", p1_up))
        targetConfig.set("Global", "InputVR2", build_binding("KEY_S", p1_down))
        targetConfig.set("Global", "InputVR3", build_binding("KEY_D", p1_left))
        targetConfig.set("Global", "InputVR4", build_binding("KEY_F", p1_right))

        targetConfig.set("Global", "InputViewChange", build_binding("KEY_A", p1_south))
        targetConfig.set("Global", "InputHandBrake", build_binding("KEY_S", p1_east))
        targetConfig.set("Global", "InputRearBrake", build_binding("KEY_S", p1_east))
        targetConfig.set("Global", "InputMusicSelect", build_binding("KEY_D", p1_north))

        if not (system.config.use_guns and guns):
            targetConfig.set("Global", "InputAnalogJoyX", build_binding("MOUSE_XAXIS", p1_lstick_x))
            targetConfig.set("Global", "InputAnalogJoyY", build_binding("MOUSE_YAXIS", p1_lstick_y))
            targetConfig.set("Global", "InputGunX", build_binding("MOUSE_XAXIS", p1_rstick_x))
            targetConfig.set("Global", "InputGunY", build_binding("MOUSE_YAXIS", p1_rstick_y))
            targetConfig.set("Global", "InputAnalogGunX", build_binding("MOUSE_XAXIS", p1_rstick_x))
            targetConfig.set("Global", "InputAnalogGunY", build_binding("MOUSE_YAXIS", p1_rstick_y))
            targetConfig.set("Global", "InputAnalogJoyTrigger", build_binding("KEY_A,MOUSE_LEFT_BUTTON", p1_r2))
            targetConfig.set("Global", "InputTrigger", build_binding("KEY_A,MOUSE_LEFT_BUTTON", p1_r2))
            targetConfig.set("Global", "InputAnalogTriggerLeft", build_binding("KEY_A,MOUSE_LEFT_BUTTON", p1_r2))
            targetConfig.set("Global", "InputAnalogJoyEvent", build_binding("KEY_S,MOUSE_RIGHT_BUTTON", p1_l2))
            targetConfig.set("Global", "InputOffscreen", build_binding("KEY_S,MOUSE_RIGHT_BUTTON", p1_l2))
            targetConfig.set("Global", "InputAnalogTriggerRight", build_binding("KEY_S,MOUSE_RIGHT_BUTTON", p1_l2))

    # Dynamically bind Player 2
    if pad2:
        p2_start = get_pad_input(pad2, "start")
        p2_select = get_pad_input(pad2, "select")
        p2_up = get_pad_input(pad2, "up") or "JOY2_POV1_UP"
        p2_down = get_pad_input(pad2, "down") or "JOY2_POV1_DOWN"
        p2_left = get_pad_input(pad2, "left") or "JOY2_POV1_LEFT"
        p2_right = get_pad_input(pad2, "right") or "JOY2_POV1_RIGHT"

        p2_south = get_pad_input(pad2, "b") or "JOY2_BUTTON1"
        p2_east = get_pad_input(pad2, "a") or "JOY2_BUTTON2"
        p2_west = get_pad_input(pad2, "y") or "JOY2_BUTTON3"
        p2_north = get_pad_input(pad2, "x") or "JOY2_BUTTON4"

        targetConfig.set("Global", "InputStart2", build_binding("KEY_2", p2_start or "JOY2_BUTTON8"))
        targetConfig.set("Global", "InputCoin2", build_binding("KEY_4", p2_select or "JOY2_BUTTON7"))

        targetConfig.set("Global", "InputJoyUp2", p2_up)
        targetConfig.set("Global", "InputJoyDown2", p2_down)
        targetConfig.set("Global", "InputJoyLeft2", p2_left)
        targetConfig.set("Global", "InputJoyRight2", p2_right)

        targetConfig.set("Global", "InputPunch2", p2_west)
        targetConfig.set("Global", "InputKick2", p2_north)
        targetConfig.set("Global", "InputGuard2", p2_south)
        targetConfig.set("Global", "InputEscape2", p2_east)

        targetConfig.set("Global", "InputShortPass2", p2_south)
        targetConfig.set("Global", "InputLongPass2", p2_west)
        targetConfig.set("Global", "InputShoot2", p2_east)

    # Evdev for guns or sdlgamepad for controllers
    for section in targetConfig.sections():
        if section.strip() in ["Global", rom.stem]:
            # for an input system
            if section.strip() != "Global":
                targetConfig.set(section, "InputSystem", "to be defined")
            for key, _ in targetConfig.items(section):
                if key == "InputSystem":
                    if system.config.use_guns and guns:
                        targetConfig.set(section, key, "evdev")
                    else:
                        targetConfig.set(section, key, "sdlgamepad")
                elif system.config.use_guns and guns:
                    # Player 1 gun bindings
                    if key == "InputAnalogJoyX":
                        targetConfig.set(section, key, "MOUSE1_XAXIS_INV")
                    elif key == "InputAnalogJoyY":
                        targetConfig.set(section, key, "MOUSE1_YAXIS_INV")
                    elif key in ("InputGunX", "InputAnalogGunX"):
                        targetConfig.set(section, key, "MOUSE1_XAXIS")
                    elif key in ("InputGunY", "InputAnalogGunY"):
                        targetConfig.set(section, key, "MOUSE1_YAXIS")
                    elif key in ("InputTrigger", "InputAnalogTriggerLeft", "InputAnalogJoyTrigger"):
                        targetConfig.set(section, key, "MOUSE1_LEFT_BUTTON")
                    elif key in ("InputOffscreen", "InputAnalogTriggerRight"):
                        targetConfig.set(section, key, "MOUSE1_RIGHT_BUTTON")
                    elif key == "InputStart1":
                        targetConfig.set(section, key, f"MOUSE1_BUTTONX1,{p1_start or 'JOY1_BUTTON8'}")
                    elif key == "InputCoin1":
                        targetConfig.set(section, key, f"MOUSE1_BUTTONX2,{p1_select or 'JOY1_BUTTON7'}")
                    elif key == "InputAnalogJoyEvent":
                        targetConfig.set(section, key, "KEY_S,MOUSE1_MIDDLE_BUTTON")
                    # Player 2 gun bindings
                    elif len(guns) >= 2:
                        p2_gun_start = p2_start or "JOY2_BUTTON8"
                        p2_gun_select = p2_select or "JOY2_BUTTON7"
                        if key == "InputAnalogJoyX2":
                            targetConfig.set(section, key, "MOUSE2_XAXIS_INV")
                        elif key == "InputAnalogJoyY2":
                            targetConfig.set(section, key, "MOUSE2_YAXIS_INV")
                        elif key in ("InputGunX2", "InputAnalogGunX2"):
                            targetConfig.set(section, key, "MOUSE2_XAXIS")
                        elif key in ("InputGunY2", "InputAnalogGunY2"):
                            targetConfig.set(section, key, "MOUSE2_YAXIS")
                        elif key in ("InputTrigger2", "InputAnalogTriggerLeft2", "InputAnalogJoyTrigger2"):
                            targetConfig.set(section, key, "MOUSE2_LEFT_BUTTON")
                        elif key in ("InputOffscreen2", "InputAnalogTriggerRight2"):
                            targetConfig.set(section, key, "MOUSE2_RIGHT_BUTTON")
                        elif key == "InputStart2":
                            targetConfig.set(section, key, f"MOUSE2_BUTTONX1,{p2_gun_start}")
                        elif key == "InputCoin2":
                            targetConfig.set(section, key, f"MOUSE2_BUTTONX2,{p2_gun_select}")
                        elif key == "InputAnalogJoyEvent2":
                            targetConfig.set(section, key, "MOUSE2_MIDDLE_BUTTON")

    # save the ini file
    with ensure_parents_and_open(targetFile, "w") as configfile:
        targetConfig.write(configfile)
