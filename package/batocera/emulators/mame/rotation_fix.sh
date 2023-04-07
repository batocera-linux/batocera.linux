#!/bin/bash
# Sometimes with a rotated screen (typically SteamDeck), MAME's video
# driver needs to be reinitialized with the right rotation after exit
case $1 in
    	gameStop)
		if [[ "$3" == "mame" ]]; then
			rotation=$(batocera-resolution getRotation)
		       	! [ -z "$rotation" ] && batocera-resolution setRotation "$rotation"
		fi
	;;
esac

