#!/bin/sh -x

case $SWITCH_STATE in
    2)
        echo "New headset"
        amixer cset name='Playback Path' 'HP'
	# disable speaker
        echo d > /sys/codec-spk-ctl/spk-ctl
        ;;

    0)
        echo "No headset"
        if [ `cat /sys/class/drm/card0-HDMI-A-1/status` == "connected" ]; then
          amixer cset name='Playback Path' 'OFF'
	  # disable speaker
          echo d > /sys/codec-spk-ctl/spk-ctl

        else
          amixer cset name='Playback Path' 'SPK'
          # enable speaker
          echo e > /sys/codec-spk-ctl/spk-ctl
  	fi
        ;;

    *)
        echo "Unexpected state: $SWITCH_STATE"
esac

exit 0
