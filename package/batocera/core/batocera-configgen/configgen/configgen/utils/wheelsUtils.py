from __future__ import annotations

import logging
import math
import os
import re
import signal
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

import evdev

from .. import controllersConfig
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from ..controller import Controller, ControllerList
    from ..Emulator import Emulator
    from ..types import DeviceInfoDict

_logger = logging.getLogger(__name__)

_WHEEL_MAPPING: Final = {
    "wheel":      "joystick1left",
    "accelerate": "r2",
    "brake":      "l2",
    "downshift":  "pageup",
    "upshift":    "pagedown",
}

# partial mapping between real pads buttons and batocera pads
_EMULATOR_MAPPING: Final = {
    "dreamcast": {
        "lt":   "l2",
        "rt":   "r2",
        "up":   "pageup",
        "down": "pagedown",
    },
    "gamecube": {
        "lt": "l2",
        "rt": "r2",
        "a":  "a",
        "b":  "b",
        "x":  "x",
        "y":  "y",
    },
    "saturn": {
        "l":      "l2",
        "r":      "r2",
        "a":      "b",
        "b":      "a",
        "c":      "pagedown",
        "x":      "y",
        "y":      "x",
        "z":      "pageup",
        "start":  "start",
    },
    "n64": {
        "l":     "pageup",
        "r":     "pagedown",
        "a":     "b",
        "b":     "y",
        "start": "start",
    },
    "wii": {
        "lt": "l2",
        "rt": "r2",
        "a":  "a",
        "b":  "b",
        "x":  "x",
        "y":  "y",
    },
    "wiiu": {
        "a":      "a",
        "b":      "b",
        "x":      "x",
        "y":      "y",
        "start":  "start",
        "select": "select",
    },
    "psx": {
        "cross":    "b",
        "square":   "y",
        "round":    "a",
        "triangle": "x",
        "start":    "start",
        "select":   "select",
    },
    "ps2": {
        "cross":    "b",
        "square":   "y",
        "round":    "a",
        "triangle": "x",
    },
    "xbox": {
        "lt": "l2",
        "rt": "r2",
        "a":  "b",
        "b":  "a",
        "x":  "y",
        "y":  "x",
    },
}


@contextmanager
def configure_wheels(
    controllers: ControllerList, system: Emulator, metadata: dict[str, str], /
) -> Iterator[tuple[ControllerList, DeviceInfoDict]]:
    if not system.config.use_wheels or not controllers:
        _logger.info("wheels disabled.")
        yield controllers, {}
        return

    # search wheels in case use_wheels is enabled for this game
    # force use_wheels in case es tells it has a wheel
    devices = controllersConfig.getDevicesInformation()

    _logger.info("wheels reconfiguration")

    _logger.info("before wheel reconfiguration :")
    for controller in controllers:
        _logger.info("  %s. index:%s dev:%s name:%s", controller.player_number, controller.index, controller.device_path, controller.real_name)

    # a map of just the items from metadata that start with "wheel_" with "wheel_" removed from the key
    wheel_metadata = {md_key[6:]: md_value for md_key, md_value in metadata.items() if md_key.startswith("wheel_")}

    # reconfigure wheel buttons
    for controller in controllers:
        if controller.device_path in devices and devices[controller.device_path]["isWheel"]:
            _logger.info("Wheel reconfiguration for pad %s", controller.real_name)
            original_inputs = controller.inputs.copy()

            # erase target keys
            for md_key, md_value in wheel_metadata.items():
                if (
                    (wheel_key := _WHEEL_MAPPING.get(md_key)) is not None
                    and md_value in _EMULATOR_MAPPING.get(system.name, {})
                    and wheel_key in controller.inputs
                ):
                    del controller.inputs[wheel_key]
                    _logger.info("wheel: erase the key %s", wheel_key)

            # fill with the wanted keys
            for md_key, md_value in wheel_metadata.items():
                if (wheel_key := _WHEEL_MAPPING.get(md_key)) is not None and (
                    wanted_key := _EMULATOR_MAPPING.get(system.name, {}).get(md_value)
                ) is not None:
                    if wheel_key in original_inputs:
                        controller.inputs[wanted_key] = original_inputs[wheel_key]
                        controller.inputs[wanted_key].name = wanted_key
                        _logger.info("wheel: fill key %s with %s", wanted_key, wheel_key)
                    else:
                        _logger.info("wheel: unable to replace %s with %s", wanted_key, wheel_key)

    # reconfigure wheel min/max/deadzone
    procs: list[subprocess.Popen[bytes]] = []
    recompute_sdl_ids = False
    new_pads: list[str] = []
    for controller in controllers:
        if (
            (device := devices.get(controller.device_path)) is not None
            and device["isWheel"]
            and "wheel_rotation" in device
        ):
            ra = int(device["wheel_rotation"])
            wanted_ra = ra
            wanted_deadzone = 0
            wanted_midzone  = 0

            # initialize values with games metadata
            if "rotation" in wheel_metadata:
                wanted_ra = int(wheel_metadata["rotation"])
            if "deadzone" in wheel_metadata:
                wanted_deadzone = int(wheel_metadata["deadzone"])
            if "midzone" in wheel_metadata:
                wanted_midzone = int(wheel_metadata["midzone"])

            # override with user configs
            if "wheel_rotation" in system.config:
                wanted_ra = int(system.config["wheel_rotation"])
            if "wheel_deadzone" in system.config:
                wanted_deadzone = int(system.config["wheel_deadzone"])
            if "wheel_midzone" in system.config:
                wanted_midzone = int(system.config["wheel_midzone"])

            _logger.info("wheel rotation angle is %s ; wanted wheel rotation angle is %s ; wanted deadzone is %s ; wanted midzone is %s", ra, wanted_ra, wanted_deadzone, wanted_midzone)

            # try to write range directly in physical wheel if the driver supports it
            range_path = Path(device["sysfs_path"]) / "range"
            if os.access(range_path, os.F_OK | os.R_OK | os.W_OK):
                range_path.write_text(str(wanted_ra))
                ra = wanted_ra

            # no need new device in some cases
            if wanted_ra < ra or wanted_deadzone > 0:
                reconfigure_result = _reconfigure_angle_rotation(controller, ra, wanted_ra, wanted_deadzone, wanted_midzone)
                if reconfigure_result is not None:
                    # replace sdl guid by virtualwheel guid for correct sdl mapping
                    controller.guid = "03000000010000000100000001000000"
                    newdev, p = reconfigure_result
                    _logger.info("replacing device %s by device %s for player %s", controller.device_path, newdev, controller.player_number)
                    devices[newdev] = device.copy()
                    devices[newdev]["eventId"] = cast('int', controllersConfig.dev2int(newdev))
                    controller.physical_device_path = controller.device_path  # save the physical device for ffb
                    controller.device_path = newdev  # needs to recompute sdl ids
                    recompute_sdl_ids = True
                    new_pads.append(newdev)
                    procs.append(p)

    # recompute sdl ids
    if recompute_sdl_ids:
        # build the new joystick list
        joysticks: dict[int, str] = {
            device["eventId"]: node for node, device in devices.items() if device["isJoystick"]
        }

        # add the new devices
        for pad_device_path in new_pads:
            matches = re.match(r"^/dev/input/event([0-9]*)$", pad_device_path)
            if matches is not None:
                joysticks[int(matches.group(1))] = pad_device_path

        # find new sdl numeration
        joysticks_by_dev: dict[str, int] = {
            x: current_id for current_id, (_, x) in enumerate(sorted(joysticks.items()))
        }

        # renumeration
        for controller in controllers:
            if (joystick_index := joysticks_by_dev.get(controller.device_path)) is not None:
                controller.index = joystick_index
                devices[controller.device_path]["joystick_index"] = joystick_index

        # fill physical_index
        for controller in controllers:
            if (
                controller.physical_device_path is not None
                and (device := devices.get(controller.physical_device_path)) is not None
                and device["joystick_index"] is not None
            ):
                controller.physical_index = device["joystick_index"]  # save the physical device for ffb

    # reorder players to priorize wheel pads
    controllers_new: ControllerList = []
    nplayer = 1
    for controller in controllers:
        if (
            controller.device_path in devices and devices[controller.device_path]["isWheel"]
        ) or controller.device_path in new_pads:
            controllers_new.append(controller.replace(player_number=nplayer))
            nplayer += 1

    for controller in controllers:
        if not (
            (controller.device_path in devices and devices[controller.device_path]["isWheel"])
            or controller.device_path in new_pads
        ):
            controllers_new.append(controller.replace(player_number=nplayer))
            nplayer += 1

    _logger.info("after wheel reconfiguration :")

    for controller in controllers_new:
        _logger.info("  %s. index:%s dev:%s name:%s", controller.player_number, controller.index, controller.device_path, controller.real_name)

    try:
        yield controllers_new, {key: device for key, device in devices.items() if device["isWheel"]}
    finally:
        try:
            _reset_controllers(procs)
        except Exception:
            _logger.error("hum, unable to reset wheel controllers !")
            # don't fail


def _reconfigure_angle_rotation(
    controller: Controller, rotation_angle: int, wanted_rotation_angle: int, wanted_deadzone: int, wanted_midzone: int
) -> tuple[str, subprocess.Popen[bytes]] | None:

    if "joystick1left" not in controller.inputs:
        raise BatoceraException(f"Wheel {controller.real_name} has no joystick1left configured. Strange for a wheel.")

    wheel_axis = int(controller.inputs["joystick1left"].id)
    input_device = evdev.InputDevice(controller.device_path)
    caps = input_device.capabilities()

    abs_min = None
    abs_max = None
    for v, absinfo in caps[evdev.ecodes.EV_ABS]:
        if v == wheel_axis:
            abs_min = absinfo.min
            abs_max = absinfo.max

    if abs_min is None or abs_max is None:
        _logger.warning("unable to get min/max of %s", controller.device_path)
        return None

    total_range = abs_max - abs_min
    new_min = abs_min
    new_max = abs_max
    if wanted_rotation_angle < rotation_angle:
        new_range = math.floor(total_range * wanted_rotation_angle / rotation_angle)
        new_min = abs_min + math.ceil((total_range - new_range) / 2)
        new_max = abs_max - math.floor((total_range - new_range) / 2)

    new_deadzone = 0
    if wanted_deadzone > 0 and wanted_deadzone > wanted_midzone:
        new_deadzone = math.floor(total_range * wanted_deadzone / rotation_angle)
        new_min -= new_deadzone // 2
        new_max += new_deadzone // 2

    new_midzone = 0
    if wanted_midzone > 0:
        new_midzone = math.floor(total_range * wanted_midzone / rotation_angle)
        new_min += new_midzone // 2
        new_max -= new_midzone // 2

    pipe_out, pipe_in = os.pipe()
    cmd = [
        "batocera-wheel-calibrator",
        "-d",
        controller.device_path,
        "-a",
        f"{wheel_axis}",
        "-m",
        f"{new_min}",
        "-M",
        f"{new_max}",
        "-z",
        f"{new_deadzone}",
        "-c",
        f"{new_midzone}",
    ]

    _logger.info(cmd)

    proc = subprocess.Popen(cmd, stdout=pipe_in, stderr=subprocess.PIPE)

    try:
        with os.fdopen(pipe_out) as fd:
            new_dev = fd.readline().rstrip("\n")
    except:
        os.kill(proc.pid, signal.SIGTERM)
        proc.communicate()
        raise

    return new_dev, proc


def _reset_controllers(wheel_processes: Iterable[subprocess.Popen[bytes]]) -> None:
    for proc in wheel_processes:
        _logger.info("killing wheel process %s", proc.pid)
        os.kill(proc.pid, signal.SIGTERM)
        proc.communicate()
