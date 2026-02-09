from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ...batoceraPaths import ensure_parents_and_open
from ...utils import vulkan
from ...utils.configparser import CaseSensitiveConfigParser
from .xemuPaths import XEMU_CONFIG

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...types import Resolution

_logger = logging.getLogger(__name__)

def writeIniFile(system: Emulator, rom: Path, playersControllers: Controllers, gameResolution: Resolution) -> None:
    iniConfig = CaseSensitiveConfigParser(interpolation=None)

    if XEMU_CONFIG.exists():
        try:
            iniConfig.read(XEMU_CONFIG, encoding='utf_8_sig')
        except Exception:
            pass

    createXemuConfig(iniConfig, system, rom, playersControllers, gameResolution)
    # save the ini file
    with ensure_parents_and_open(XEMU_CONFIG, 'w') as configfile:
        iniConfig.write(configfile)

def createXemuConfig(iniConfig: CaseSensitiveConfigParser, system: Emulator, rom: Path, playersControllers: Controllers, gameResolution: Resolution) -> None:
    # Create INI sections
    if not iniConfig.has_section("general"):
        iniConfig.add_section("general")
    if not iniConfig.has_section("sys"):
        iniConfig.add_section("sys")
    if not iniConfig.has_section("sys.files"):
        iniConfig.add_section("sys.files")
    if not iniConfig.has_section("audio"):
        iniConfig.add_section("audio")
    if not iniConfig.has_section("display"):
        iniConfig.add_section("display")
    if not iniConfig.has_section("display.quality"):
        iniConfig.add_section("display.quality")
    if not iniConfig.has_section("display.vulkan"):
        iniConfig.add_section("display.vulkan")
    if not iniConfig.has_section("display.window"):
        iniConfig.add_section("display.window")
    if not iniConfig.has_section("display.ui"):
        iniConfig.add_section("display.ui")
    if not iniConfig.has_section("input.bindings"):
        iniConfig.add_section("input.bindings")
    if not iniConfig.has_section("net"):
        iniConfig.add_section("net")
    if not iniConfig.has_section("net.udp"):
        iniConfig.add_section("net.udp")


    # Boot Animation Skip
    iniConfig.set("general", "skip_boot_anim", system.config.get("xemu_bootanim", "false"))

    # Disable welcome screen on first launch
    iniConfig.set("general", "show_welcome", "false")

    # Set Screenshot directory
    iniConfig.set("general", "screenshot_dir", '"/userdata/screenshots"')

    # Fill sys sections
    iniConfig.set("sys", "mem_limit", f'"{system.config.get("xemu_memory", "64")}"')

    if system.name == "chihiro":
        iniConfig.set("sys", "mem_limit", '"128"')
        iniConfig.set("sys.files", "flashrom_path", '"/userdata/bios/cerbios.bin"')
    else:
        iniConfig.set("sys.files", "flashrom_path", '"/userdata/bios/Complex_4627.bin"')

    iniConfig.set("sys.files", "bootrom_path", '"/userdata/bios/mcpx_1.0.bin"')
    iniConfig.set("sys.files", "hdd_path", '"/userdata/saves/xbox/xbox_hdd.qcow2"')
    iniConfig.set("sys.files", "eeprom_path", '"/userdata/saves/xbox/xemu_eeprom.bin"')
    iniConfig.set("sys.files", "dvd_path", f'"{rom}"')

    # Audio quality
    iniConfig.set("audio", "use_dsp", system.config.get("xemu_use_dsp", "false"))

    # API
    renderer = system.config.get("xemu_api", "VULKAN")

    if system.name == "chihiro":
        renderer = "OPENGL"
        _logger.debug("Chihiro system, defaulting to OpenGL due to a Xemu bug")

    iniConfig.set("display", "renderer", f'"{renderer}"')

    # Vulkan GPU selection
    if renderer == "VULKAN" and vulkan.is_available():
        gpu_name = None
        if vulkan.has_discrete_gpu():
            _logger.debug("A discrete GPU is available on the system. We will use that for performance")
            gpu_name = vulkan.get_discrete_gpu_name()
            if gpu_name:
                _logger.debug("Using Discrete GPU Name: %s for Xemu", gpu_name)
            else:
                _logger.debug("Discrete GPU detected but couldn't get name.")

        if not gpu_name:
            _logger.debug("Using default GPU for Xemu")
            gpu_name = vulkan.get_default_gpu_name()

        if gpu_name:
            iniConfig.set("display.vulkan", "preferred_physical_device", f'"{gpu_name}"')
        else:
            # Worst case fallback: empty string triggers Xemu auto-detection
            iniConfig.set("display.vulkan", "preferred_physical_device", '""')

    # Rendering resolution
    iniConfig.set("display.quality", "surface_scale", system.config.get("xemu_render", "1")) # render scale by default

    # start fullscreen
    iniConfig.set("display.window", "fullscreen_on_startup", "true")

    # Window size
    window_res = f'{gameResolution["width"]}x{gameResolution["height"]}'
    iniConfig.set("display.window", "startup_size", f'"{window_res}"')

    # Vsync
    iniConfig.set("display.window", "vsync", system.config.get("xemu_vsync", "true"))

    # don't show the menubar
    iniConfig.set("display.ui", "show_menubar", "false")

    # Scaling
    iniConfig.set("display.ui", "fit", f'"{system.config.get("xemu_scaling", "scale")}"')

    # Aspect ratio
    iniConfig.set("display.ui", "aspect_ratio", f'"{system.config.get("xemu_aspect", "auto")}"')

    # Fill input section
    # first, clear
    for i in range(1,5):
        iniConfig.remove_option("input.bindings", f"port{i}")
    for nplayer, pad in enumerate(playersControllers[:4], start=1):
        iniConfig.set("input.bindings", f"port{nplayer}", f'"{pad.guid}"')

    # Network
    # Documentation: https://github.com/xemu-project/xemu/blob/master/config_spec.yml
    if network_type := system.config.get("xemu_networktype"):
        iniConfig.set("net", "enable", "true")
        iniConfig.set("net", "backend", f'"{network_type}"')
    else:
        iniConfig.set("net", "enable", "false")
    # Additionnal settings for udp: if nothing is entered in these fields, the xemu.toml is untouched
    if udpremote := system.config.get("xemu_udpremote"):
        iniConfig.set("net.udp", "remote_addr", f'"{udpremote}"')
    if udpbind := system.config.get("xemu_udpbind"):
        iniConfig.set("net.udp", "bind_addr", f'"{udpbind}"')
