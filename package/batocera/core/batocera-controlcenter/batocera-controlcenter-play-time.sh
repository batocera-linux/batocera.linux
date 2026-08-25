#!/bin/bash

# A helper for batocera-controlcenter to get the running time of the batocera-launch process

PID="$(pgrep -x -n batocera-launch)"

if [[ -n "$PID" ]]; then
    PLAYING_TIME="$(ps -o etime= -p "$PID" | tr -d '[:blank:]')"

    if [[ -n "$PLAYING_TIME" ]]; then
        echo "Playing for $PLAYING_TIME"
    fi
fi
