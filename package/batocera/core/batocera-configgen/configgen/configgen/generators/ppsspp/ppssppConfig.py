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
ppssppRetroach: Final = PPSSPP_PSP_SYSTEM_DIR / 'ppsspp_retroachievements.dat'

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

def writeRetroAchievements(token: str):
    if token:
        with ensure_parents_and_open(ppssppRetroach, 'w') as retroach_file:
            retroach_file.write(token)


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

    # Resolution
    iniConfig.set("Graphics", "InternalResolution", system.config.get_str("internal_resolution", "1"))

    # Software rendering (always false)
    iniConfig.set("Graphics", "SoftwareRenderer", "False")

    # Always fullscreen
    iniConfig.set("Graphics", "FullScreen", "True")

    # VSync
    iniConfig.set("Graphics", "VSync", str(system.config.get_bool('vsync', False)))

    # Frame skipping
    iniConfig.set("Graphics", "FrameSkip", system.config.get_str("frameskip", "0"))

    # Frame skipping type - Use number and not percent
    iniConfig.set("Graphics", "FrameSkipType", "0")

    # Auto frameskip
    iniConfig.set("Graphics", "AutoFrameSkip", str(system.config.get_bool("autoframeskip", False)))

    # Skip Buffer Effects
    iniConfig.set("Graphics", "SkipBufferEffects", str(system.config.get_bool('skip_buffer_effects', False)))

    # Disable Culling
    iniConfig.set("Graphics", "DisableRangeCulling", str(system.config.get_bool('disable_culling', False)))

    # Skip GPU Readbacks
    iniConfig.set("Graphics", "SkipGPUReadbackMode", system.config.get_str('skip_gpu_readbacks', "0"))

    # Lazy texture caching
    iniConfig.set("Graphics", "TextureBackoffCache", str(system.config.get_bool('lazy_texture_caching', False)))

    # Spline / Bezier curves quality
    iniConfig.set("Graphics", "SplineBezierQuality", system.config.get_str('curves_quality', "2"))

    # Duplicate Frames
    iniConfig.set("Graphics", "RenderDuplicateFrames", str(system.config.get_bool('duplicate_frames', False)))

    # Buffer Graphics Commands
    iniConfig.set("Graphics", "InflightFrames", system.config.get_str('buffer_graphics', "3"))

    # Hardware transfom - always true
    iniConfig.set("Graphics", "HardwareTransform", "True")

    # Software skinning
    iniConfig.set("Graphics", "SoftwareSkinning", str(system.config.get_bool('software_skinning', True)))

    # Hardware Tessellation
    iniConfig.set("Graphics", "HardwareTessellation", str(system.config.get_bool('hardware_tessellation', False)))

    # Texture Scaling Type
    iniConfig.set("Graphics", "TexScalingType", system.config.get_str("texture_scaling_type", "0"))

    # Texture Scaling Level
    iniConfig.set("Graphics", "TexScalingLevel", system.config.get_str("texture_scaling_level", "1"))

    # Texture Deposterize
    iniConfig.set("Graphics", "TexDeposterize", str(system.config.get_bool("texture_deposterize", False)))

    # Anisotropic Filtering
    iniConfig.set("Graphics", "AnisotropyLevel", system.config.get_str("anisotropic_filtering", "4"))

    # Texture Filtering
    iniConfig.set("Graphics", "TextureFiltering", system.config.get_str("texture_filtering", "1"))

    # Smart 2D texture filtering
    iniConfig.set("Graphics", "Smart2DTexFiltering", str(system.config.get_bool("smart_2d", False)))

    # Display FPS
    iniConfig.set("Graphics", "ShowFPSCounter", "3" if system.config.show_fps else "0") # 1 for Speed%, 2 for FPS, 3 for both

    # Set other defaults
    iniConfig.set("Graphics", "DisplayIntegerScale", "False")

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

    # Set 32GB memstick size
    iniConfig.set("SystemParam", "MemStickSize", "32")

    ## [GENERAL]
    if not iniConfig.has_section("General"):
        iniConfig.add_section("General")

    # First run, false
    iniConfig.set("General", "FirstRun", "False")

    # Rewinding
    iniConfig.set("General", "RewindFlipFrequency", system.config.get_bool('rewind', return_values=("300", "0"))) # 300 = every 5 seconds
    # Cheats
    iniConfig.set("General", "EnableCheats", str(system.config.get_bool("enable_cheats", False)))
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

    ## [RetroAchievements]
    if not iniConfig.has_section("Achievements"):
        iniConfig.add_section("Achievements")

    if system.config.get_bool('retroachievements'):
        iniConfig.set("Achievements", "AchievementsUserName", system.config.get_str("retroachievements.username", ""))
        iniConfig.set("Achievements", "AchievementsChallengeMode", str(system.config.get_bool("retroachievements.hardcore", False)))
        iniConfig.set("Achievements", "AchievementsEncoreMode", str(system.config.get_bool("retroachievements.encore", False)))
        iniConfig.set("Achievements", "AchievementsUnofficial", str(system.config.get_bool("retroachievements.unofficial", False)))
        iniConfig.set("Achievements", "AchievementsSoundEffects", "True")
        iniConfig.set("Achievements", "AchievementsEnable", "True")
        writeRetroAchievements(system.config.get_str("retroachievements.token", ""))
    else:
        iniConfig.set("Achievements", "AchievementsEnable", "False")
        iniConfig.set("Achievements", "AchievementsChallengeMode", "False")

    # Custom : allow the user to configure directly PPSSPP via batocera.conf via lines like : ppsspp.section.option=value
    for section_option, user_config_value in system.config.items(starts_with='ppsspp.'):
        custom_section, _, custom_option = section_option.partition('.')
        if not iniConfig.has_section(custom_section):
            iniConfig.add_section(custom_section)
        iniConfig.set(custom_section, custom_option, str(user_config_value))
