from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from ...batoceraPaths import mkdir_if_not_exists
from ...settings.unixSettings import UnixSettings
from .moonlightPaths import MOONLIGHT_CONFIG, MOONLIGHT_CONFIG_DIR, MOONLIGHT_STAGING_CONFIG, MOONLIGHT_STAGING_DIR

if TYPE_CHECKING:
    from ...Emulator import Emulator


def generateMoonlightConfig(system: Emulator):

    mkdir_if_not_exists(MOONLIGHT_STAGING_DIR)

    # If user made config file exists, copy to staging directory for use
    if MOONLIGHT_CONFIG.exists():
        shutil.copy(MOONLIGHT_CONFIG, MOONLIGHT_STAGING_CONFIG)
    else:
        # truncate existing config and create new one
        MOONLIGHT_STAGING_CONFIG.open("w").close()

        moonlightConfig = UnixSettings(MOONLIGHT_STAGING_CONFIG, separator=' ')

        # resolution
        match system.config.get("moonlight_resolution"):
            case "1":
                width = '1920'
                height = '1080'
            case "2":
                width = '3840'
                height = '2160'
            case _:
                width = '1280'
                height = '720'

        moonlightConfig.save('width', width)
        moonlightConfig.save('height', height)

        # rotate
        moonlightConfig.save('rotate', system.config.get("moonlight_rotate", '0'))

        # framerate
        match system.config.get("moonlight_framerate"):
            case "0":
                framerate = '30'
            case "2":
                framerate = '120'
            case _:
                framerate = '60'

        moonlightConfig.save('fps', framerate)

        # bitrate
        match system.config.get("moonlight_bitrate"):
            case "0":
                bitrate = '5000'
            case "1":
                bitrate = '10000'
            case "2":
                bitrate = '20000'
            case "3":
                bitrate = '50000'
            case _:
                bitrate = '-1'  # Moonlight default

        moonlightConfig.save('bitrate', bitrate)

        # codec
        moonlightConfig.save('codec',system.config.get("moonlight_codec", 'auto'))

        # sops (Streaming Optimal Playable Settings)
        moonlightConfig.save('sops', system.config.get("moonlight_sops", 'true').lower())

        # quit remote app on exit
        moonlightConfig.save('quitappafter', system.config.get("moonlight_quitapp", 'false').lower())

        # view only
        moonlightConfig.save('viewonly', system.config.get("moonlight_viewonly", 'false').lower())

        # platform - we only select sdl (best compatibility)
        # required for controllers to work
        moonlightConfig.save('platform', 'sdl')

        ## Directory to store encryption keys
        moonlightConfig.save('keydir', MOONLIGHT_CONFIG_DIR / 'keydir')

        # lan or wan streaming - ideally lan
        moonlightConfig.save('remote', system.config.get("moonlight_remote", 'no'))

        ## Enable 5.1/7.1 surround sound
        if surround := system.config.get('moonlight_surround'):
            moonlightConfig.save('surround', surround)
        else:
            moonlightConfig.save('#surround', '5.1')

        moonlightConfig.write()
