#!/bin/sh

# SWAYSOCK=<XDG_RUNTIME_DIR>/sway-ipc.<uid>.sock
export SWAYSOCK=${XDG_RUNTIME_DIR}/sway-ipc.0.sock
export WAYLAND_DISPLAY=$(getLocalWaylandDisplay)
