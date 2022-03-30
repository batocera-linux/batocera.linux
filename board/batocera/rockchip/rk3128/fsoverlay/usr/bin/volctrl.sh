#!/bin/bash
#
# This code comes from mcerveny's comment on:
# https://github.com/Ruka-CFW/rk3128-cfw/issues/51#issuecomment-915533431
#

if [ `cat /sys/class/drm/card0-HDMI-A-1/status` == "disconnected" ]; then
	name='Master Playback Volume'
else
	name='HDMI Playback Volume'
fi

value=$(amixer cget name="$name" | sed -n 's/^  :.*values=\([[0-9]*\).*/\1/p')

if [[ "$1" == "up" ]]; then
	let value=value+9
	if [[ $value -gt 99 ]]; then value=99; fi
else
	let value=value-9
	if [[ $value -lt 0 ]]; then value=0; fi
fi

amixer cset name="$name" $value
alsactl store -f /userdata/asound.state
