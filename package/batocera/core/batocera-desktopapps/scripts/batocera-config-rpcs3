#!/bin/bash

# when the program is called from a non X environment, handle the mouse
# maybe an other choice is better

if test -z "${DISPLAY}"
then
    export DISPLAY=$(getLocalXDisplay)
fi

emulatorlauncher -system ps3 -rom config -emulator rpcs3
