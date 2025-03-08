from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from ...batoceraPaths import ensure_parents_and_open
from ...utils import vulkan
from ...utils.configparser import CaseSensitiveConfigParser
from .ppssppPaths import PPSSPP_PSP_SYSTEM_DIR

if TYPE_CHECKING:
    from ...Emulator import Emulator


_logger = logging.getLogger(__name__)

ppssppConfig: Final   = PPSSPP_PSP_SYSTEM_DIR / 'ppsspp.ini'
ppssppControls: Final = PPSSPP_PSP_SYSTEM_DIR / 'controls.ini'

def writePPSSPPConfig(system: Emulator):
    iniConfig = CaseSensitiveConfigParser(interpolation=None)
    if ppssppConfig.exists():
        try:
            iniConfig.read(ppssppConfig, encoding='utf_8_sig')
        except Exception:
            pass

    createPPSSPPConfig(iniConfig, system)
    # Save the ini file
    with ensure_parents_and_open(ppssppConfig, 'w') as configfile:
        iniConfig.write(configfile)

def createPPSSPPConfig(iniConfig: CaseSensitiveConfigParser, system: Emulator):

    ## [GRAPHICS]
    if not iniConfig.has_section("Graphics"):
        iniConfig.add_section("Graphics")

    # Graphics Backend
    gfxbackend = system.config.get("gfxbackend", "0 (OPENGL)")
    iniConfig.set("Graphics", "GraphicsBackend", gfxbackend)
    # If Vulkan
    if gfxbackend == "3 (VULKAN)":
        # Check if we have a discrete GPU & if so, set the Name
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            if vulkan.has_discrete_gpu():
                _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                discrete_name = vulkan.get_discrete_gpu_name()
                if discrete_name:
                    _logger.debug("Using Discrete GPU Name: %s for PPSSPP", discrete_name)
                    iniConfig.set("Graphics", "VulkanDevice", discrete_name)
                else:
                    _logger.debug("Couldn't get discrete GPU Name")
            else:
                _logger.debug("Discrete GPU is not available on the system. Using default.")
        else:
            _logger.debug("Vulkan driver is not available on the system. Falling back to OpenGL")
            iniConfig.set("Graphics", "GraphicsBackend", "0 (OPENGL)")

    # Display FPS
    iniConfig.set("Graphics", "ShowFPSCounter", "3" if system.config.show_fps else "0") # 1 for Speed%, 2 for FPS, 3 for both

    # Frameskip
    iniConfig.set("Graphics", "FrameSkipType", "0") # Use number and not percent
    frameskip = system.config.get_str("frameskip")
    if not frameskip or frameskip == "automatic":
        if not system.config.get_bool('rendering_mode', True):
            frameskip = "0"
        else:
            frameskip = "2"
    iniConfig.set("Graphics", "FrameSkip", frameskip)

    # Buffered rendering
    rendering_mode = system.config.get_bool('rendering_mode', True, return_values=("1", "0"))
    auto_frameskip = "False"

    iniConfig.set("Graphics", "RenderingMode", rendering_mode)

    if rendering_mode == "1":
        # Both internal resolution and auto frameskip are dependent on buffered rendering being on, only check these if the user is actually using buffered rendering.
        iniConfig.set("Graphics", "InternalResolution", system.config.get_str("internal_resolution", "1"))
        # Auto frameskip
        auto_frameskip = str(system.config.get_bool("autoframeskip", True))

    # Have to force autoframeskip off here otherwise PPSSPP sets rendering mode back to 1.
    iniConfig.set("Graphics", "AutoFrameSkip", auto_frameskip)

    # VSync Interval
    iniConfig.set("Graphics", "VSyncInterval", str(system.config.get_bool('vsyncinterval', True)))

    # Texture Scaling Level
    iniConfig.set("Graphics", "TexScalingLevel", system.config.get("texture_scaling_level", "1"))

    # Texture Scaling Type
    iniConfig.set("Graphics", "TexScalingType", system.config.get("texture_scaling_type", "0"))

    # Texture Deposterize
    iniConfig.set("Graphics", "TexDeposterize", system.config.get("texture_deposterize", "True"))

    # Anisotropic Filtering
    iniConfig.set("Graphics", "AnisotropyLevel", system.config.get("anisotropic_filtering", "3"))

    # Texture Filtering
    iniConfig.set("Graphics", "TextureFiltering", system.config.get("texture_filtering", "1"))

   ## [SYSTEM PARAM]
    if not iniConfig.has_section("SystemParam"):
        iniConfig.add_section("SystemParam")

    # Forcing Nickname to Batocera or User name
    username = "Batocera"
    if system.config.get_bool('retroachievements') and (config_username := system.config.get('retroachievements.username')):
        username = config_username
    iniConfig.set("SystemParam", "NickName", username)
    # Disable Encrypt Save (permit to exchange save with different machines)
    iniConfig.set("SystemParam", "EncryptSave", "False")


    ## [GENERAL]
    if not iniConfig.has_section("General"):
        iniConfig.add_section("General")

    # Rewinding
    iniConfig.set("General", "RewindFlipFrequency", system.config.get_bool('rewind', return_values=("300", "0"))) # 300 = every 5 seconds
    # Cheats
    iniConfig.set("General", "EnableCheats", system.config.get("enable_cheats", "False"))
    # Don't check for a new version
    iniConfig.set("General", "CheckForNewVersion", "False")

    # SaveState
    iniConfig.set("General", "StateSlot", system.config.get_str("state_slot", "0"))

    ## [UPGRADE] - don't upgrade
    if not iniConfig.has_section("Upgrade"):
        iniConfig.add_section("Upgrade")
    iniConfig.set("Upgrade", "UpgradeMessage", "")
    iniConfig.set("Upgrade", "UpgradeVersion", "")
    iniConfig.set("Upgrade", "DismissedVersion", "")

    # Custom : allow the user to configure directly PPSSPP via batocera.conf via lines like : ppsspp.section.option=value
    for section_option, user_config_value in system.config.items(starts_with='ppsspp.'):
        custom_section, _, custom_option = section_option.partition('.')
        if not iniConfig.has_section(custom_section):
            iniConfig.add_section(custom_section)
        iniConfig.set(custom_section, custom_option, str(user_config_value))
