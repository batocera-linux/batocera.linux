#!/bin/bash

es_settings="/root/.emulationstation/es_settings.cfg"
config_script=/recalbox/scripts/recalbox-config.sh
log=/root/recalbox.log
echo "starting new log" > $log
settingsLang=`cat "$es_settings" | sed -n 's/.*name="Lang" value="\(.*\)".*/\1/p'`
if [ "$settingsLang" == "" ];then
	settingsLang="en_US"
fi

keyboardmap=`echo "$settingsLang" | cut -c1-2`
loadkeys $keyboardmap

settingsAudio=`cat "$es_settings" | sed -n 's/.*name="AudioOutputDevice" value="\(.*\)".*/\1/p'`
if [ "$settingsAudio" == "" ];then
	settingsAudio="auto"
fi
eval $config_script "audio" "$settingsAudio" >> $log

settingsGPIOControls=`cat "$es_settings" | sed -n 's/.*name="GpioControllers" value="\(.*\)".*/\1/p'`
if [ "$settingsGPIOControls" == "true" ];then
	eval $config_script "gpiocontrollers" "enable" >> $log
fi

settingsVolume=`cat "$es_settings" | sed -n 's/.*name="SystemVolume" value="\(.*\)".*/\1/p'`
if [ "$settingsVolume" != "" ];then
	eval $config_script "volume" "$settingsVolume" >> $log
fi


command="HOME=/root LANG=\"${settingsLang}.UTF-8\" SDL_VIDEO_GL_DRIVER=/usr/lib/libGLESv2.so SDL_NOMOUSE=1 /usr/bin/emulationstation"

echo "Starting emulationstation with command : " >> $log
echo "$command" >> $log

eval $command
