#!/usr/bin/env python

import batoceraFiles
import os
from Emulator import Emulator
from settings.unixSettings import UnixSettings

def generateMoonlightConfig():
    # conf file
    try:
        moonlightConfig = UnixSettings(batoceraFiles.moonlightConfigFile, separator=' ')
    except UnicodeError:
        # remove it and try again
        os.remove(batoceraFiles.moonlightConfigFile)
        moonlightConfig = UnixSettings(batoceraFiles.moonlightConfigFile, separator=' ')

    ## Hostname or IP-address of host to connect to
    ## By default host is autodiscovered using mDNS
    #address = 

    ## Video streaming configuration
    moonlightConfig.save('width', '1280')
    moonlightConfig.save('height', '720')
    moonlightConfig.save('fps', '60')

    ## Bitrate depends by default on resolution and fps
    ## Set to -1 to enable default
    ## 20Mbps (20000) for 1080p (60 fps)
    ## 10Mbps (10000) for 1080p or 60 fps
    ## 5Mbps (5000) for lower resolution or fps
    moonlightConfig.save('bitrate', '-1')

    ## Size of network packets should be lower than MTU
    #packetsize = 1024

    ## Select video codec (auto/h264/h265)
    #codec = auto

    ## Default started application on host
    #app = Steam

    ## Default used mapping for streaming
    ## Searched for in $XDG_DATA_DIRS/moonlight or /usr/share/moonlight and /usr/local/share/moonlight
    ## Mapping can also be user overrided in $XDG_CONFIG_DIR/moonlight or ~/.config/moonlight or current directory
    #mapping = gamecontrollerdb.txt

    ## Enable selected input devices
    ## By default all available input devices should be used
    ## Only evdev devices /dev/input/event* are allowed
    ## To use a different mapping then default another mapping should be declared above the input
    #input = /dev/input/event1

    ## Enable GFE for changing graphical game settings for optimal performance and quality
    moonlightConfig.save('sops', 'true')

    ## Play audio on host instead of streaming to client
    #localaudio = false

    ## Send quit app request to remote after quitting session
    #quitappafter = false

    ## Disable all input processing (view-only mode)
    #viewonly = false

    ## Select audio device to play sound on
    #audio = sysdefault

    ## Select the audio and video decoder to use
    ## default - autodetect
    ## aml - hardware video decoder for ODROID-C1/C2
    ## rk  - hardware video decoder for ODROID-N1 Rockchip
    ## omx - hardware video decoder for Raspberry Pi
    ## imx - hardware video decoder for i.MX6 devices
    ## x11 - software decoder
    ## sdl - software decoder with SDL input and audio
    ## fake - no audio and video
    #platform = default

    ## Directory to store encryption keys
    ## By default keys are stored in $XDG_CACHE_DIR/moonlight or ~/.cache/moonlight
    moonlightConfig.save('keydir', '/userdata/system/configs/moonlight/keydir')

    ## Enable QOS settings to optimize for internet instead of local network
    #remote = false

    ## Enable 5.1 surround sound
    #surround = false

    ## Load additional configuration files
    #config = /path/to/config

    moonlightConfig.write()
