#!/bin/bash

if test -z "${DISPLAY}"
then
    export DISPLAY=:0.0
fi

# hum pw 0.2 and 0.3 are hardcoded, not nice
LD_LIBRARY_PATH=/lib32:/usr/wine/lutris/lib/wine LIBGL_DRIVERS_PATH=/lib32/dri SPA_PLUGIN_DIR="/usr/lib/spa-0.2:/lib32/spa-0.2" PIPEWIRE_MODULE_DIR="/usr/lib/pipewire-0.3:/lib32/pipewire-0.3" WINEPREFIX=/userdata/saves/fpinball /usr/wine/lutris/bin/wine "/usr/fpinball/Future Pinball.exe"

exit 0
