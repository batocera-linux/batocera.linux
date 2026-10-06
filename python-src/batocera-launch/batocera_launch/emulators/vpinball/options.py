from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from batocera_common.configparser import CaseSensitiveConfigParser
    from batocera_launch import SystemConfig


def configure_options(settings: CaseSensitiveConfigParser, config: SystemConfig) -> None:
    # init sections
    for section in ('Player', 'Plugin.AltSound'):
        if not settings.has_section(section):
            settings.add_section(section)

    # Ball trail
    balltrail = config.get_str('vpinball_balltrail', '0')
    settings.set('Player', 'BallTrail', '0' if balltrail == '0' else '1')
    settings.set('Player', 'BallTrailStrength', balltrail)

    # Visual Nudge Strength
    settings.set('Player', 'NudgeStrength', config.get_str('vpinball_nudgestrength', ''))

    # Performance settings
    settings.set('Player', 'MaxFramerate', config.get_str('vpinball_maxframerate', ''))

    # vsync
    settings.set('Player', 'SyncMode', config.get_str('vpinball_vsync', '2'))

    # presets
    if (presets := config.get_str('vpinball_presets')) != 'manual':
        match presets:
            case 'highend':
                fxaa = '3'
                sharpen = '2'
                disable_ao = '0'
                dynamic_ao = '1'
                ssrefl = '1'
                pfreflection = '5'
                force_filtering = '1'
                alpha_accuracy = '10'
            case 'lowend':
                fxaa = '0'
                sharpen = '0'
                disable_ao = '1'
                dynamic_ao = '0'
                ssrefl = '0'
                pfreflection = '3'
                force_filtering = '0'
                alpha_accuracy = '5'
            case _:
                fxaa = ''
                sharpen = ''
                disable_ao = ''
                dynamic_ao = ''
                ssrefl = ''
                pfreflection = ''
                force_filtering = ''
                alpha_accuracy = ''

        settings.set('Player', 'FXAA', fxaa)
        settings.set('Player', 'Sharpen', sharpen)
        settings.set('Player', 'DisableAO', disable_ao)
        settings.set('Player', 'DynamicAO', dynamic_ao)
        settings.set('Player', 'SSRefl', ssrefl)
        settings.set('Player', 'PFReflection', pfreflection)
        settings.set('Player', 'ForceAnisotropicFiltering', force_filtering)
        settings.set('Player', 'AlphaRampAccuracy', alpha_accuracy)

    # custom display physical setup
    if config.get_bool('vpinball_customphysicalsetup'):
        # Width
        screen_width = config.get_str('vpinball_screenwidth', '')
        # Height
        screen_height = config.get_str('vpinball_screenheight', '')
        # Inclination
        inclination = config.get_str('vpinball_screeninclination', '')
        # Y
        screen_y = config.get_str('vpinball_screenplayery', '')
        # Z
        screen_z = config.get_str('vpinball_screenplayerz', '')
    else:
        screen_width = ''
        screen_height = ''
        inclination = ''
        screen_y = ''
        screen_z = ''

    settings.set('Player', 'ScreenWidth', screen_width)
    settings.set('Player', 'ScreenHeight', screen_height)
    settings.set('Player', 'ScreenInclination', inclination)
    settings.set('Player', 'ScreenPlayerY', screen_y)
    settings.set('Player', 'ScreenPlayerZ', screen_z)

    # Sound balance
    settings.set('Player', 'MusicVolume', config.get_str('vpinball_musicvolume', ''))
    settings.set('Player', 'SoundVolume', config.get_str('vpinball_soundvolume', ''))

    # select which ID for sounddevices by running:
    # /usr/bin/vpinball/VPinballX_BGFX -listsnd
    settings.set('Player', 'SoundDevice', config.get_str('vpinball_sounddevice', ''))
    settings.set('Player', 'SoundDeviceBG', config.get_str('vpinball_sounddevicebg', ''))
