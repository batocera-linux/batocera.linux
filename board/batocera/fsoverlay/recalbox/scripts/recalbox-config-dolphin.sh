#!/bin/bash

export DISPLAY=:0.0

matchbox-remote -s # show the mouse
XDG_CONFIG_HOME=/recalbox/share/system/configs XDG_DATA_HOME=/recalbox/share/saves /usr/bin/dolphin-emu-wx
matchbox-remote -h # hide the mouse
