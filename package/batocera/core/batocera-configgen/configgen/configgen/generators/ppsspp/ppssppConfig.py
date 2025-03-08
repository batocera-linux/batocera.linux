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
    if system.isOptSet('gfxbackend'):
        iniConfig.set("Graphics", "GraphicsBackend", system.config["gfxbackend"])
    else:
        iniConfig.set("Graphics", "GraphicsBackend", "0 (OPENGL)")
    # If Vulkan
    if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == "3 (VULKAN)":
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
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
        iniConfig.set("Graphics", "ShowFPSCounter", "3") # 1 for Speed%, 2 for FPS, 3 for both
    else:
        iniConfig.set("Graphics", "ShowFPSCounter", "0")

    # Frameskip
    iniConfig.set("Graphics", "FrameSkipType", "0") # Use number and not percent
    if system.isOptSet("frameskip") and system.config["frameskip"] != "automatic":
        iniConfig.set("Graphics", "FrameSkip", str(system.config["frameskip"]))
    elif system.isOptSet('rendering_mode') and not system.getOptBoolean('rendering_mode'):
        iniConfig.set("Graphics", "FrameSkip", "0")
    else:
        iniConfig.set("Graphics", "FrameSkip", "2")

    # Buffered rendering
    if system.isOptSet('rendering_mode') and not system.getOptBoolean('rendering_mode'):
        iniConfig.set("Graphics", "RenderingMode", "0")
        # Have to force autoframeskip off here otherwise PPSSPP sets rendering mode back to 1.
        iniConfig.set("Graphics", "AutoFrameSkip", "False")
    else:
        iniConfig.set("Graphics", "RenderingMode", "1")
        # Both internal resolution and auto frameskip are dependent on buffered rendering being on, only check these if the user is actually using buffered rendering.
        # Internal Resolution
        if system.isOptSet('internal_resolution'):
            iniConfig.set("Graphics", "InternalResolution", str(system.config["internal_resolution"]))
        else:
            iniConfig.set("Graphics", "InternalResolution", "1")
        # Auto frameskip
        if system.isOptSet("autoframeskip") and not system.getOptBoolean("autoframeskip"):
            iniConfig.set("Graphics", "AutoFrameSkip", "False")
        else:
            iniConfig.set("Graphics", "AutoFrameSkip", "True")

    # VSync Interval
    if system.isOptSet('vsyncinterval') and not system.getOptBoolean('vsyncinterval'):
        iniConfig.set("Graphics", "VSyncInterval", "False")
    else:
        iniConfig.set("Graphics", "VSyncInterval", "True")

    # Texture Scaling Level
    if system.isOptSet('texture_scaling_level'):
        iniConfig.set("Graphics", "TexScalingLevel", system.config["texture_scaling_level"])
    else:
        iniConfig.set("Graphics", "TexScalingLevel", "1")
    # Texture Scaling Type
    if system.isOptSet('texture_scaling_type'):
        iniConfig.set("Graphics", "TexScalingType", system.config["texture_scaling_type"])
    else:
        iniConfig.set("Graphics", "TexScalingType", "0")
    # Texture Deposterize
    if system.isOptSet('texture_deposterize'):
        iniConfig.set("Graphics", "TexDeposterize", system.config["texture_deposterize"])
    else:
        iniConfig.set("Graphics", "TexDeposterize", "True")

    # Anisotropic Filtering
    if system.isOptSet('anisotropic_filtering'):
        iniConfig.set("Graphics", "AnisotropyLevel", system.config["anisotropic_filtering"])
    else:
        iniConfig.set("Graphics", "AnisotropyLevel", "3")
    # Texture Filtering
    if system.isOptSet('texture_filtering'):
        iniConfig.set("Graphics", "TextureFiltering", system.config["texture_filtering"])
    else:
        iniConfig.set("Graphics", "TextureFiltering", "1")

   ## [SYSTEM PARAM]
    if not iniConfig.has_section("SystemParam"):
        iniConfig.add_section("SystemParam")

    # Forcing Nickname to Batocera or User name
    if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') and system.isOptSet('retroachievements.username') and system.config.get('retroachievements.username', "") != "":
        iniConfig.set("SystemParam", "NickName", system.config.get('retroachievements.username', ""))
    else:
        iniConfig.set("SystemParam", "NickName", "Batocera")
    # Disable Encrypt Save (permit to exchange save with different machines)
    iniConfig.set("SystemParam", "EncryptSave", "False")


    ## [GENERAL]
    if not iniConfig.has_section("General"):
        iniConfig.add_section("General")

    # Rewinding
    if system.isOptSet('rewind') and system.getOptBoolean('rewind'):
        iniConfig.set("General", "RewindFlipFrequency", "300") # 300 = every 5 seconds
    else:
        iniConfig.set("General", "RewindFlipFrequency",  "0")
    # Cheats
    if system.isOptSet('enable_cheats'):
        iniConfig.set("General", "EnableCheats", system.config["enable_cheats"])
    else:
        iniConfig.set("General", "EnableCheats", "False")
    # Don't check for a new version
    iniConfig.set("General", "CheckForNewVersion", "False")

    # SaveState
    if system.isOptSet('state_slot'):
        iniConfig.set("General", "StateSlot", str(system.config["state_slot"]))
    else:
        iniConfig.set("General", "StateSlot", "0")

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
