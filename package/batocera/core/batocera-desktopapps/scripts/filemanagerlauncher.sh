#!/bin/bash

export XDG_MENU_PREFIX=batocera-
export XDG_CONFIG_DIRS=/etc/xdg

DISPLAY=:0.0 matchbox-remote -s # show the mouse
DISPLAY=:0.0 pcmanfm /recalbox/share
DISPLAY=:0.0 matchbox-remote -h # hide the mouse
