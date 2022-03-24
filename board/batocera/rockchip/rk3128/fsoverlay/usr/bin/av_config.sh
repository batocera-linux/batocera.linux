#!/bin/bash

source /usr/bin/av_helper.sh

usage()
{
	echo "usage: ${0##*/}"
	echo "Options:"
	echo -e "\t--list-connectors"
	echo -e "\t\tList drm connector information"
	echo -e "\t--set-connector <id>|<name>|internal|external [<mode>]"
	echo -e "\t\tSet drm connector and mode"
	echo -e "\t--get-connector-prop <id>|<name>|internal|external [<prop>+]"
	echo -e "\t\tGet drm connector properties"
	echo -e "\t\tA property could be ID/NAME/TYPE/ENABLED/STATUS/MODE/MODES"
	echo -e "\t--list-playbacks"
	echo -e "\t\tList alsa playback information"
	echo -e "\t--set-playback <id>|<name>|hdmi|usb|internal"
	echo -e "\t\tSet alsa playback"
	echo -e "\t--get-playback-prop <id>|<name>|hdmi|usb|internal [<prop>+]"
	echo -e "\t\tGet alsa playback properties"
	echo -e "\t\tA property could be ID/NAME/TYPE/DESC"

	exit -1
}

OPTION=$1

case $OPTION in
	--list-connectors)
		drm_init_connectors
		drm_list_connectors
		;;
	--set-connector)
		[ $# -lt 2 ] && usage

		drm_init_connectors

		OPTION_ID=$2
		OPTION_MODE=$3
		ID=$(drm_id_from_option $OPTION_ID connected)

		if [ -z "$ID" ];then
			echo Cannot find available connector $VAL
			usage
		fi

		if [ -n "$OPTION_MODE" ];then
			MODE=$(drm_get_properties $ID MODES| \
				grep -iwo $OPTION_MODE)
			if [ -z "$MODE" ];then
				echo Cannot find mode for $OPTION_MODE
				usage
			fi
		fi

		drm_set_connector $ID $MODE
		;;
	--get-connector-prop)
		[ $# -lt 2 ] && usage

		drm_init_connectors

		OPTION_ID=$2
		ID=$(drm_id_from_option $OPTION_ID)

		if [ -z "$ID" ];then
			echo Cannot find available connector $VAL
			usage
		fi

		shift
		shift
		typeset -u PROP
		for PROP in $@;do
			VAL=$(drm_get_properties $ID $PROP)
			[ -z "$VAL" ] && VAL="unknown"
			echo $VAL
		done
		;;
	--list-playbacks)
		alsa_init_playbacks
		alsa_list_playbacks
		;;
	--set-playback)
		[ $# -lt 2 ] && usage

		alsa_init_playbacks

		OPTION_ID=$2
		ID=$(alsa_id_from_option $OPTION_ID)

		if [ -z "$ID" ];then
			echo Cannot find available playback $OPTION_ID
			usage
		fi

		NAME=$(alsa_get_properties $ID NAME)
		alsa_set_playback $NAME
		;;
	--get-playback-prop)
		[ $# -lt 2 ] && usage

		alsa_init_playbacks

		OPTION_ID=$2
		ID=$(alsa_id_from_option $OPTION_ID)

		if [ -z "$ID" ];then
			echo Cannot find available playback $OPTION_ID
			usage
		fi

		NAME=$(alsa_get_properties $ID NAME)

		shift
		shift
		typeset -u PROP
		for PROP in $@;do
			VAL=$(alsa_get_properties $ID $PROP)
			[ -z "$VAL" ] && VAL="unknown"
			echo $VAL
		done
		;;
	--help|-h|*)
		usage
		;;
esac
