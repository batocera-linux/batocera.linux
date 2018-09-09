#!/bin/bash

export DISPLAY=:0.0

matchbox-remote -s # show the mouse
XDG_CONFIG_HOME=/recalbox/share/system/configs /usr/PCSX/bin/PCSX2 --gs=/usr/PCSX/bin/plugins/libGSdx.so --pad=/usr/PCSX/bin/plugins/libonepad-legacy.so --cdvd=/usr/PCSX/bin/plugins/libCDVDnull.so --usb=/usr/PCSX/bin/plugins/libUSBnull-0.7.0.so --fw=/usr/PCSX/bin/plugins/libFWnull-0.7.0.so --dev9=/usr/PCSX/bin/plugins/libdev9null-0.5.0.so --spu2=/usr/PCSX/bin/plugins/libspu2x-2.0.0.so
matchbox-remote -h # hide the mouse
