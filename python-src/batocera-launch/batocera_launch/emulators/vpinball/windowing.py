from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from batocera_common.configparser import CaseSensitiveConfigParser
    from batocera_launch import Resolution, SystemConfig
    from batocera_launch.types import ScreenInfo


def configure_ini(
    settings: CaseSensitiveConfigParser,
    config: SystemConfig,
    resolution: Resolution,
    screens: list[ScreenInfo],
) -> None:
    # init sections
    for section in ('Player', 'TableOverride', 'Backglass'):
        if not settings.has_section(section):
            settings.add_section(section)

    # disable full screen to move the window if necessary (and bcc won't full screen windows)
    settings.set('Player', 'PlayfieldFullScreen', '0')

    # disable any kind of automatic vpx rotation
    settings.set('TableOverride', 'ViewCabMode', '2')

    # Reasonable constants / default values
    r_screen = 16 / 9

    # which windows to display, and where ?
    backglass_config = get_backglass_configuration(config, screens)

    playfield_screen, backglass_screen = get_playfield_and_backglass_screens(config, screens)

    dmdsize = get_dmd_window_size(config)

    # Playfield
    if config.get_str('vpinball_playfield') != 'manual':
        configure_playfield(settings, screens, playfield_screen)

    # playfield mode
    if 'vpinball_playfieldmode' in config:
        settings.set('Player', 'BGSet', config.get_str('vpinball_playfieldmode', ''))
    elif screens[playfield_screen].resolution.width < screens[playfield_screen].resolution.height:
        settings.set('Player', 'BGSet', '1')  # pincab / cabinet
    else:
        settings.set('Player', 'BGSet', '0')  # desktop mode

    # backglass
    if backglass_config != 'manual':
        configure_backglass(settings, backglass_config, screens, backglass_screen, r_screen, resolution, dmdsize)


def get_backglass_configuration(config: SystemConfig, screens: list[ScreenInfo]) -> str:
    val = config.get_str('vpinball_backglass', '')
    if val == '':
        val = 'screen2' if len(screens) > 1 else 'disabled'
    if len(screens) <= 1 and val == 'screen2':
        val = 'disabled'
    return val


def get_playfield_and_backglass_screens(config: SystemConfig, screens: list[ScreenInfo]) -> tuple[int, int]:
    # determine playField and backglass screens numbers
    reverse_playfield_and_backglass = False
    if 'vpinball_inverseplayfieldandbackglass' in config:
        reverse_playfield_and_backglass = config.get_bool('vpinball_inverseplayfieldandbackglass')
    else:
        # auto : if the screen 2 is vertical while the first screen is not, inverse
        if (
            len(screens) >= 2
            and screens[0].resolution.width > screens[0].resolution.height
            and screens[1].resolution.width < screens[1].resolution.height
        ):
            reverse_playfield_and_backglass = True

    playfield_screen, backglass_screen = 0, 1
    if reverse_playfield_and_backglass and len(screens) > 1:
        playfield_screen, backglass_screen = 1, 0

    return playfield_screen, backglass_screen


def configure_playfield(settings: CaseSensitiveConfigParser, screens: list[ScreenInfo], playfield_screen: int) -> None:
    settings.set('Player', 'PlayfieldDisplay', 'absolute')
    settings.set('Player', 'PlayfieldWndX', str(screens[playfield_screen].x))
    settings.set('Player', 'PlayfieldWndY', str(screens[playfield_screen].y))
    settings.set('Player', 'PlayfieldWidth', str(screens[playfield_screen].resolution.width))
    settings.set('Player', 'PlayfieldHeight', str(screens[playfield_screen].resolution.height))


def get_dmd_window_size(config: SystemConfig) -> list[int]:
    if 'vpinball_dmdsize' not in config:
        return [1024, 256]  # like 128x32
    if config.get_str('vpinball_dmdsize') == '128x16':
        return [1024, 128]
    if config.get_str('vpinball_dmdsize') == '192x64':
        return [1024, 341]
    if config.get_str('vpinball_dmdsize') == '256x64':
        return [1024, 128]
    return [1024, 256]  # like 128x32


def configure_backglass(
    settings: CaseSensitiveConfigParser,
    backglass_config: str,
    screens: list[ScreenInfo],
    backglass_screen: int,
    r_screen: float,
    resolution: Resolution,
    dmdsize: list[int],  # kept for parity with the old generator; unused there too
) -> None:
    r_window = 4 / 3  # Usual Ratio for this window
    small, medium, large = 20, 25, 30
    x, y, width = 0, 0, medium

    if backglass_config == 'disabled':
        settings.set('Backglass', 'BackglassOutput', '0')
        return

    settings.set('Backglass', 'BackglassOutput', '1')
    # disable full screen to move the window if necessary (and bcc wants no fullscreen)
    settings.set('Backglass', 'BackglassFullScreen', '0')

    settings.set('Backglass', 'BackglassDisplay', 'absolute')
    if backglass_config == 'screen2':
        settings.set('Backglass', 'BackglassWndX', str(screens[backglass_screen].x))
        settings.set('Backglass', 'BackglassWndY', str(screens[backglass_screen].y))
        settings.set('Backglass', 'BackglassWidth', str(screens[backglass_screen].resolution.width))
        settings.set('Backglass', 'BackglassHeight', str(screens[backglass_screen].resolution.height))
    else:
        if backglass_config == 'topright_small':
            width = small
            x = 100 - width
        if backglass_config == 'topright_medium':
            width = medium
            x = 100 - width
        if backglass_config == 'topright_large':
            width = large
            x = 100 - width
        if backglass_config == 'topleft_small':
            width = small
            x = 0
        if backglass_config == 'topleft_medium':
            width = medium
            x = 0
        if backglass_config == 'topleft_large':
            width = large
            x = 0
        # apply settings
        height = relative_height_calculate(r_screen, r_window, width)
        settings.set('Backglass', 'BackglassWndX', convert_to_pixel(resolution.width, x))
        settings.set('Backglass', 'BackglassWndY', convert_to_pixel(resolution.height, y))
        settings.set('Backglass', 'BackglassWidth', convert_to_pixel(resolution.width, width))
        settings.set('Backglass', 'BackglassHeight', convert_to_pixel(resolution.height, height))


# necessary trick because people can plug their 1080p laptop on a 4k TV
# (and because VPinballX.ini uses absolute pixel coordinates)
def convert_to_pixel(total_size: int, percentage: float) -> str:
    return str(int(int(total_size) * float(percentage) * 1e-2))


# Calculates the relative height, depending on the screen ratio
# (normally 16/9), the element ratio (4/3 for the backglass) and the relative width
def relative_height_calculate(r_screen: float, r_element: float, relative_width: float) -> int:
    return int(r_screen * relative_width / r_element)
