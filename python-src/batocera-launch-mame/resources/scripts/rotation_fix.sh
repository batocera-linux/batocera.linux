#!/bin/bash
# Sometimes with a rotated screen (typically SteamDeck), MAME's video
# driver needs to be reinitialized with the right rotation after exit
case $1 in
    gameStop)
        if [[ "$3" == "mame" ]]; then
            if [[ "$(batocera-resolution getDisplayMode)" == "xorg" ]]; then
                rotation=$(batocera-resolution getRotation)
                [[ -n "$rotation" ]] && batocera-resolution setRotation "$rotation"
            fi
        fi
    ;;
esac
