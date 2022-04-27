#!/usr/bin/env python
import os, sys
import batoceraFiles
import settings
import subprocess
import json

def setMupenConfig(iniConfig, system, controllers, gameResolution):

    # Hotkeys
    setHotKeyConfig(iniConfig, controllers)

    # Paths
    if not iniConfig.has_section("Core"):
        iniConfig.add_section("Core")
    iniConfig.set("Core", "Version", "1.01") # Version is important for the .ini creation otherwise, mupen remove the section
    iniConfig.set("Core", "ScreenshotPath", batoceraFiles.SCREENSHOTS)
    iniConfig.set("Core", "SaveStatePath",  batoceraFiles.mupenSaves)
    iniConfig.set("Core", "SaveSRAMPath",   batoceraFiles.mupenSaves)
    iniConfig.set("Core", "SharedDataPath", batoceraFiles.mupenConf)
    # TODO : Miss Mupen64Plus\hires_texture

    # 4MB RAM Extention Pack
    if system.isOptSet("mupen64plus_DisableExtraMem") and system.config["mupen64plus_DisableExtraMem"] == 'True':
        iniConfig.set("Core", "DisableExtraMem", "True")
    else:
        iniConfig.set("Core", "DisableExtraMem", "False")        # Disable 4MB expansion RAM pack. May be necessary for some games

    # Create section for Audio-SDL
    if not iniConfig.has_section("Audio-SDL"):
        iniConfig.add_section("Audio-SDL")

    # Default to disable while it causes issues
    if system.isOptSet("mupen64plus_AudioSync") and system.config["mupen64plus_AudioSync"] == 'True':
        iniConfig.set("Audio-SDL", "AUDIO_SYNC", "True")
    else:
        iniConfig.set("Audio-SDL", "AUDIO_SYNC", "False")

    # Audio buffer settings
    # In the future, add for Audio-OMX too?
    if system.isOptSet("mupen64plus_AudioBuffer"):
        # Very High
        if system.config["mupen64plus_AudioBuffer"] == "Very High":
            iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_SIZE", "16384")
            iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_TARGET", "4096")
            iniConfig.set("Audio-SDL", "SECONDARY_BUFFER_SIZE", "2048")
        # High (defaults provided by mupen64plus)
        if system.config["mupen64plus_AudioBuffer"] == "High":
            iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_SIZE", "16384")
            iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_TARGET", "2048")
            iniConfig.set("Audio-SDL", "SECONDARY_BUFFER_SIZE", "1024")
        # Low
        if system.config["mupen64plus_AudioBuffer"] == "Low":
            iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_SIZE", "4096")
            iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_TARGET", "1024")
            iniConfig.set("Audio-SDL", "SECONDARY_BUFFER_SIZE", "512")
    else:
        # Medium
        iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_SIZE", "8192")
        iniConfig.set("Audio-SDL", "PRIMARY_BUFFER_TARGET", "2048")
        iniConfig.set("Audio-SDL", "SECONDARY_BUFFER_SIZE", "1024")

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
    iniConfig.set("Video-General", "Fullscreen", "True") # required at least for drm boards
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
    if (system.isOptSet("mupen64plus_ratio") and system.config["mupen64plus_ratio"] == "16/9") or (not system.isOptSet("mupen64plus_ratio") and system.isOptSet("ratio") and system.config["ratio"] == "16/9"):
        # Glide64mk2.: Adjust screen aspect for wide screen mode: -1=Game default, 0=disable. 1=enable
        iniConfig.set("Video-Glide64mk2", "adjust_aspect", "1")
        # Glide64mk2.: Aspect ratio: -1=Game default, 0=Force 4:3, 1=Force 16:9, 2=Stretch, 3=Original
        iniConfig.set("Video-Glide64mk2", "aspect", "1")
        # GLideN64.: Screen aspect ratio (0=stretch, 1=force 4:3, 2=force 16:9, 3=adjust)
        iniConfig.set("Video-GLideN64",   "AspectRatio", "2")
    elif (system.isOptSet("mupen64plus_ratio") and system.config["mupen64plus_ratio"] == "4/3") or (not system.isOptSet("mupen64plus_ratio") and system.isOptSet("ratio") and system.config["ratio"] == "4/3"):
        # 4/3
        iniConfig.set("Video-Glide64mk2", "adjust_aspect", "0")
        iniConfig.set("Video-Glide64mk2", "aspect", "0")
        iniConfig.set("Video-GLideN64",   "AspectRatio", "1")
    else:
        iniConfig.set("Video-Glide64mk2", "adjust_aspect", "-1")
        iniConfig.set("Video-Glide64mk2", "aspect", "-1")
        iniConfig.set("Video-GLideN64",   "AspectRatio", "3")

    # Textures Mip-Mapping (Filtering)
    if system.isOptSet("mupen64plus_Mipmapping") and system.config["mupen64plus_Mipmapping"] != 0:
        if system.config["mupen64plus_Mipmapping"] == "1":
            iniConfig.set("Video-Rice",       "Mipmapping", "1")
            iniConfig.set("Video-Glide64mk2", "filtering",  "0")
        elif system.config["mupen64plus_Mipmapping"] == "2":
            iniConfig.set("Video-Rice",       "Mipmapping", "2")
            iniConfig.set("Video-Glide64mk2", "filtering",  "1")
        else:
            iniConfig.set("Video-Rice",       "Mipmapping", "3")
            iniConfig.set("Video-Glide64mk2", "filtering",  "2")
    else:
        iniConfig.set("Video-Rice",       "Mipmapping", "0")     # 0=no, 1=nearest, 2=bilinear, 3=trilinear
        iniConfig.set("Video-Glide64mk2", "filtering", "-1")     # -1=Game default, 0=automatic, 1=force bilinear, 2=force point sampled

    # Anisotropic Filtering
    if system.isOptSet("mupen64plus_Anisotropic") and system.config["mupen64plus_Anisotropic"] != 0:
        iniConfig.set("Video-Rice", "AnisotropicFiltering", system.config["mupen64plus_Anisotropic"])
        iniConfig.set("Video-Glide64mk2", "wrpAnisotropic", system.config["mupen64plus_Anisotropic"])
    else:
        iniConfig.set("Video-Rice", "AnisotropicFiltering", "0") # Enable/Disable Anisotropic Filtering for Mipmapping (0=no filtering, 2-16=quality).
                                                                 # This is uneffective if Mipmapping is false.
        iniConfig.set("Video-Glide64mk2", "wrpAnisotropic", "1") # Wrapper Anisotropic Filtering

    # Anti-aliasing MSAA
    if system.isOptSet("mupen64plus_AntiAliasing") and system.config["mupen64plus_AntiAliasing"] != 0:
        iniConfig.set("Video-Rice",       "MultiSampling",   system.config["mupen64plus_AntiAliasing"])
        iniConfig.set("Video-Glide64mk2", "wrpAntiAliasing", system.config["mupen64plus_AntiAliasing"])
    else:
        iniConfig.set("Video-Rice",       "MultiSampling",   "0") # 0=off, 2, 4, 8, 16=quality
        iniConfig.set("Video-Glide64mk2", "wrpAntiAliasing", "0") # Enable full-scene anti-aliasing by setting this to a value greater than 1

    # Hires textures
    if system.isOptSet("mupen64plus_LoadHiResTextures") and system.config["mupen64plus_LoadHiResTextures"] == 'True':
        iniConfig.set("Video-Rice", "LoadHiResTextures", "True")
        iniConfig.set("Video-Glide64mk2", "ghq_hirs",    "1")
    else:
        iniConfig.set("Video-Rice", "LoadHiResTextures", "False")
        iniConfig.set("Video-Glide64mk2", "ghq_hirs",    "0")    # Hi-res texture pack format (0 for none, 1 for Rice)


    # Texture Enhencement XBRZ -> ONLY for RICE
    if system.isOptSet("mupen64plus_TextureEnhancement") and system.config["mupen64plus_TextureEnhancement"] != 0:
        iniConfig.set("Video-Rice", "TextureEnhancement", system.config["mupen64plus_TextureEnhancement"])
    else:
        iniConfig.set("Video-Rice", "TextureEnhancement", "0")   # 0=None, 1=2X, 2=2XSAI, 3=HQ2X, 4=LQ2X, 5=HQ4X, 6=Sharpen, 7=Sharpen More, 8=External, 9=Mirrored


    # Frameskip -> ONLY for GLIDE64MK2
    iniConfig.set("Video-Glide64mk2", "autoframeskip", "0")
    if system.isOptSet("mupen64plus_frameskip") and system.config["mupen64plus_frameskip"] != 0:
        if system.config["mupen64plus_frameskip"] == "=automatic":
            # If true, skip up to maxframeskip frames to maintain clock schedule; if false, skip exactly maxframeskip frames
            iniConfig.set("Video-Glide64mk2", "autoframeskip", "1")
            iniConfig.set("Video-Glide64mk2", "maxframeskip",  "5")
        else:
            # If autoframeskip is false, skip exactly this many frames
            iniConfig.set("Video-Glide64mk2", "maxframeskip", system.config["mupen64plus_frameskip"])
    else:
        iniConfig.set("Video-Glide64mk2", "maxframeskip", "0")

    # Read framebuffer always -> for GLIDE64MK2
    if system.isOptSet("mupen64plus_fb_read_always") and system.config["mupen64plus_fb_read_always"] != "-1":
        iniConfig.set("Video-Glide64mk2", "fb_read_always", system.config["mupen64plus_fb_read_always"])
    else:
        iniConfig.set("Video-Glide64mk2", "fb_read_always", "-1") # -1 = Game default

    # 64DD
    if not iniConfig.has_section("64DD"):
        iniConfig.add_section("64DD")
    # Filename of the 64DD IPL ROM
    if (system.name == 'n64dd'):
        iniConfig.set("64DD", "IPL-ROM", batoceraFiles.BIOS + "/64DD_IPL.bin")
    else:
        iniConfig.set("64DD", "IPL-ROM", "")
    iniConfig.set("64DD", "Disk", "")


    # Display FPS
    if system.config['showFPS'] == 'true':
        iniConfig.set("Video-Rice",       "ShowFPS",  "True")
        iniConfig.set("Video-Glide64mk2", "show_fps", "4")
    else:
        iniConfig.set("Video-Rice",       "ShowFPS",  "False")
        iniConfig.set("Video-Glide64mk2", "show_fps", "8") # 1=FPS counter, 2=VI/s counter, 4=% speed, 8=FPS transparent

        # Custom : allow the user to configure directly mupen64plus.cfg via batocera.conf via lines like : n64.mupen64plus.section.option=value
        for user_config in system.config:
            if user_config[:12] == "mupen64plus.":
                section_option = user_config[12:]
                section_option_splitter = section_option.find(".")
                custom_section = section_option[:section_option_splitter]
                custom_option = section_option[section_option_splitter+1:]
                if not iniConfig.has_section(custom_section):
                    iniConfig.add_section(custom_section)
                iniConfig.set(custom_section, custom_option, str(system.config[user_config]))

def setHotKeyConfig(iniConfig, controllers):
    if not iniConfig.has_section("CoreEvents"):
        iniConfig.add_section("CoreEvents")
    iniConfig.set("CoreEvents", "Version", "1")

    if '1' in controllers:
        if 'hotkey' in controllers['1'].inputs:
            if 'start' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Stop", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['start'])))
            if 'y' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Save State", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['y'])))
            if 'x' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Load State", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['x'])))
            if 'pageup' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Screenshot", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['pageup'])))
            if 'up' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Increment Slot", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['up'])))
            if 'right' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Fast Forward", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['right'])))
            if 'a' in controllers['1'].inputs:
                iniConfig.set("CoreEvents", "Joy Mapping Reset", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['a'])))
            if 'b' in controllers['1'].inputs:
                #iniConfig.set("CoreEvents", "Joy Mapping Pause", "\"J{}{}/{}\"".format(controllers['1'].index, createButtonCode(controllers['1'].inputs['hotkey']), createButtonCode(controllers['1'].inputs['b'])))
                iniConfig.set("CoreEvents", "Joy Mapping Pause", "")


def createButtonCode(button):
    if(button.type == 'axis'):
        if button.value == '-1':
            return 'A'+button.id+'-'
        else:
            return 'A'+button.id+'+'
    if(button.type == 'button'):
        return 'B'+button.id
    if(button.type == 'hat'):
        return 'H'+button.id+'V'+button.value
