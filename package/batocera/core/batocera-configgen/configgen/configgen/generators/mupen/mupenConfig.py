from __future__ import annotations

from typing import TYPE_CHECKING

from ...batoceraPaths import BIOS, SCREENSHOTS
from .mupenPaths import MUPEN_CONFIG_DIR, MUPEN_SAVES

if TYPE_CHECKING:
    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...types import Resolution
    from ...utils.configparser import CaseSensitiveConfigParser


def setMupenConfig(iniConfig: CaseSensitiveConfigParser, system: Emulator, controllers: Controllers, gameResolution: Resolution):

    # Hotkeys
    cleanHotKeyConfig(iniConfig)

    # Paths
    if not iniConfig.has_section("Core"):
        iniConfig.add_section("Core")
    iniConfig.set("Core", "Version", "1.01") # Version is important for the .ini creation otherwise, mupen remove the section
    iniConfig.set("Core", "ScreenshotPath", str(SCREENSHOTS))
    iniConfig.set("Core", "SaveStatePath",  str(MUPEN_SAVES))
    iniConfig.set("Core", "SaveSRAMPath",   str(MUPEN_SAVES))
    iniConfig.set("Core", "SharedDataPath", str(MUPEN_CONFIG_DIR))
    iniConfig.set("Core", "SaveFilenameFormat", "1000") # forces savesstates with rom name
    # TODO : Miss Mupen64Plus\hires_texture

    # 4MB RAM Extention Pack
    iniConfig.set("Core", "DisableExtraMem", str(system.config.get_bool("mupen64plus_DisableExtraMem")))

    # state_slot option, AutoStateSlotIncrement could be set too depending on the es option
    if state_slot := system.config.get_str('state_slot'):
        iniConfig.set("Core", "CurrentStateSlot", state_slot)

    # increment savestates
    iniConfig.set("Core", "AutoStateSlotIncrement", str(system.config.get_bool("incrementalsavestates", True)))

    # Create section for Audio-SDL
    if not iniConfig.has_section("Audio-SDL"):
        iniConfig.add_section("Audio-SDL")

    # Default to disable while it causes issues
    iniConfig.set("Audio-SDL", "AUDIO_SYNC", str(system.config.get_bool("mupen64plus_AudioSync")))

    # Audio buffer settings
    # In the future, add for Audio-OMX too?
    match system.config.get("mupen64plus_AudioBuffer"):
        case "Very High":
            primary_buffer_size = "16384"
            primary_buffer_target = "4096"
            secondary_buffer_size = "2048"
        case "High":  # (defaults provided by mupen64plus)
            primary_buffer_size = "16384"
            primary_buffer_target = "2048"
            secondary_buffer_size = "1024"
        case "Low":
            primary_buffer_size = "4096"
            primary_buffer_target = "1024"
            secondary_buffer_size = "512"
        case _:  # Medium
            primary_buffer_size = "8192"
            primary_buffer_target = "2048"
            secondary_buffer_size = "1024"

    iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_SIZE", primary_buffer_size)
    iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_TARGET", primary_buffer_target)
    iniConfig.set("Audio-SDL", "SECONDARY_BUFFER_SIZE", secondary_buffer_size)

    # Invert required when screen is rotated
    if gameResolution["width"] < gameResolution["height"]:
        width = gameResolution["height"]
        height = gameResolution["width"]
    else:
        width = gameResolution["width"]
        height = gameResolution["height"]

    # Internal Resolution
    if not iniConfig.has_section("Video-General"):
        iniConfig.add_section("Video-General")
    iniConfig.set("Video-General", "Version", "1")
    iniConfig.set("Video-General", "ScreenWidth", str(width))
    iniConfig.set("Video-General", "ScreenHeight", str(height))
    iniConfig.set("Video-General", "Fullscreen", "False") # required at least for drm boards (still true ?) ; hum, False required (at least for xorg + bcc)
    iniConfig.set("Video-General", "VerticalSync", "True")

    # Graphic Plugins
    # DOC : https://github.com/mupen64plus/mupen64plus-video-glide64mk2/blob/master/src/Glide64/Main.cpp
    if not iniConfig.has_section("Video-Glide64mk2"):
        iniConfig.add_section("Video-Glide64mk2")
    if not iniConfig.has_section("Video-GLideN64"):
        iniConfig.add_section("Video-GLideN64")
    # https://mupen64plus.org/wiki/index.php?title=Mupen64Plus_Plugin_Parameters
    # https://github.com/mupen64plus/mupen64plus-video-rice/blob/master/src/Config.cpp
    if not iniConfig.has_section("Video-Rice"):
        iniConfig.add_section("Video-Rice")

    iniConfig.set("Video-Rice", "Version", "1")
    iniConfig.set("Video-Glide64mk2", "Version", "1")

    # Widescreen Mode -> ONLY for GLIDE64 & MK2
    mupen_ratio = system.config.get("mupen64plus_ratio")
    ratio = system.config.get("ratio")

    if mupen_ratio == "16/9" or (not mupen_ratio and ratio == "16/9"):
        adjust_aspect = "1"
        aspect = "1"
        aspect_ratio = "2"
    elif mupen_ratio == "4/3" or (not mupen_ratio and ratio == "4/3"):
        adjust_aspect = "0"
        aspect = "0"
        aspect_ratio = "1"
    else:
        adjust_aspect = "-1"
        aspect = "-1"
        aspect_ratio = "3"

    # Glide64mk2.: Adjust screen aspect for wide screen mode: -1=Game default, 0=disable. 1=enable
    iniConfig.set("Video-Glide64mk2", "adjust_aspect", adjust_aspect)
    # Glide64mk2.: Aspect ratio: -1=Game default, 0=Force 4:3, 1=Force 16:9, 2=Stretch, 3=Original
    iniConfig.set("Video-Glide64mk2", "aspect", aspect)
    # GLideN64.: Screen aspect ratio (0=stretch, 1=force 4:3, 2=force 16:9, 3=adjust)
    iniConfig.set("Video-GLideN64",   "AspectRatio", aspect_ratio)

    # Textures Mip-Mapping (Filtering)
    match (mipmapping := system.config.get("mupen64plus_Mipmapping", "0")):
        case "1":
            filtering = "0"
        case "2":
            filtering = "1"
        case "3":
            filtering = "2"
            mipmapping = "3"
        case _:
            filtering = "-1"

    iniConfig.set("Video-Rice",       "Mipmapping", mipmapping)     # 0=no, 1=nearest, 2=bilinear, 3=trilinear
    iniConfig.set("Video-Glide64mk2", "filtering", filtering)     # -1=Game default, 0=automatic, 1=force bilinear, 2=force point sampled

    # Anisotropic Filtering
    anisotropic = system.config.get("mupen64plus_Anisotropic", "0")

    # Enable/Disable Anisotropic Filtering for Mipmapping (0=no filtering, 2-16=quality).
    iniConfig.set("Video-Rice", "AnisotropicFiltering", anisotropic)
    # Wrapper Anisotropic Filtering
    # This is uneffective if Mipmapping is false.
    iniConfig.set("Video-Glide64mk2", "wrpAnisotropic", "1" if anisotropic == "0" else anisotropic)

    # Anti-aliasing MSAA
    antialiasing = system.config.get("mupen64plus_AntiAliasing", "0")
    iniConfig.set("Video-Rice",       "MultiSampling",   antialiasing) # 0=off, 2, 4, 8, 16=quality
    iniConfig.set("Video-Glide64mk2", "wrpAntiAliasing", antialiasing) # Enable full-scene anti-aliasing by setting this to a value greater than 1

    # Hires textures
    load_hires_textures = system.config.get_bool("mupen64plus_LoadHiResTextures")
    iniConfig.set("Video-Rice", "LoadHiResTextures", str(load_hires_textures))
    iniConfig.set("Video-Glide64mk2", "ghq_hirs",    "1" if load_hires_textures else "0")  # Hi-res texture pack format (0 for none, 1 for Rice)

    # Texture Enhencement XBRZ -> ONLY for RICE
    # 0=None, 1=2X, 2=2XSAI, 3=HQ2X, 4=LQ2X, 5=HQ4X, 6=Sharpen, 7=Sharpen More, 8=External, 9=Mirrored
    iniConfig.set("Video-Rice", "TextureEnhancement", system.config.get("mupen64plus_TextureEnhancement", "0"))

    # Frameskip -> ONLY for GLIDE64MK2
    autoframeskip = "0"
    iniConfig.set("Video-Glide64mk2", "autoframeskip", "0")
    match system.config.get("mupen64plus_frameskip", "0"):
        case "automatic":
            # If true, skip up to maxframeskip frames to maintain clock schedule; if false, skip exactly maxframeskip frames
            autoframeskip = "1"
            maxframeskip = "5"
        case "0":
            maxframeskip = "0"
        case _ as frameskip:
            # If autoframeskip is false, skip exactly this many frames
            maxframeskip = frameskip

    iniConfig.set("Video-Glide64mk2", "autoframeskip", autoframeskip)
    iniConfig.set("Video-Glide64mk2", "maxframeskip",  maxframeskip)

    # Read framebuffer always -> for GLIDE64MK2
    iniConfig.set("Video-Glide64mk2", "fb_read_always", system.config.get("mupen64plus_fb_read_always", "-1"))

    # 64DD
    if not iniConfig.has_section("64DD"):
        iniConfig.add_section("64DD")
    # Filename of the 64DD IPL ROM
    if (system.name == 'n64dd'):
        iniConfig.set("64DD", "IPL-ROM", str(BIOS / "64DD_IPL.bin"))
    else:
        iniConfig.set("64DD", "IPL-ROM", "")
    iniConfig.set("64DD", "Disk", "")


    # Display FPS
    if system.config.show_fps:
        iniConfig.set("Video-Rice",       "ShowFPS",  "True")
        iniConfig.set("Video-Glide64mk2", "show_fps", "4")
    else:
        iniConfig.set("Video-Rice",       "ShowFPS",  "False")
        iniConfig.set("Video-Glide64mk2", "show_fps", "8") # 1=FPS counter, 2=VI/s counter, 4=% speed, 8=FPS transparent

        # Custom : allow the user to configure directly mupen64plus.cfg via batocera.conf via lines like : n64.mupen64plus.section.option=value
        for section_option, user_config_value in system.config.items(starts_with='mupen64plus.'):
            custom_section, _, custom_option = section_option.partition(".")
            if not iniConfig.has_section(custom_section):
                iniConfig.add_section(custom_section)
            iniConfig.set(custom_section, custom_option, str(user_config_value))

def cleanHotKeyConfig(iniConfig: CaseSensitiveConfigParser):
    if not iniConfig.has_section("CoreEvents"):
        return # nothing needs to be done

    iniConfig.set("CoreEvents", "Version", "1")
    iniConfig.set("CoreEvents", "Joy Mapping Stop", "")
    iniConfig.set("CoreEvents", "Joy Mapping Save State", "")
    iniConfig.set("CoreEvents", "Joy Mapping Load State", "")
    iniConfig.set("CoreEvents", "Joy Mapping Screenshot", "")
    iniConfig.set("CoreEvents", "Joy Mapping Increment Slot", "")
    iniConfig.set("CoreEvents", "Joy Mapping Fast Forward", "")
    iniConfig.set("CoreEvents", "Joy Mapping Reset", "")
    iniConfig.set("CoreEvents", "Joy Mapping Pause", "")
