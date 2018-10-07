#!/bin/bash

# when the program is called from a non X environment, handle the mouse
# maybe an other choice is better

if test -z "${DISPLAY}"
then
    export DISPLAY=:0.0
    HANDLEMOUSE=1
    matchbox-remote -s # show the mouse
fi

ARCH=$(cat /recalbox/recalbox.arch)

if test "${ARCH}" != "x86"
then
    export LD_LIBRARY_PATH="/lib32"
    export LIBGL_DRIVERS_PATH="/lib32/dri"
fi

XDG_CONFIG_HOME=/recalbox/share/system/configs /usr/PCSX/bin/PCSX2 --gs=/usr/PCSX/bin/plugins/libGSdx.so --pad=/usr/PCSX/bin/plugins/libonepad-legacy.so --cdvd=/usr/PCSX/bin/plugins/libCDVDnull.so --usb=/usr/PCSX/bin/plugins/libUSBnull-0.7.0.so --fw=/usr/PCSX/bin/plugins/libFWnull-0.7.0.so --dev9=/usr/PCSX/bin/plugins/libdev9null-0.5.0.so --spu2=/usr/PCSX/bin/plugins/libspu2x-2.0.0.so

if test "${HANDLEMOUSE}" = "1"
then
    matchbox-remote -h # hide the mouse
fi
