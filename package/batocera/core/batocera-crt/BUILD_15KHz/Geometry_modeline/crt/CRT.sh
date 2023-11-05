#!/bin/bash
####################################################################################
# Script to create a custom monitor with a set of modelines using geometry utility #
#              With this utility you have to manually center a grid.               #
# This centering is used to create that custom monitor so then all modelines used  #
#                 by switchress will be centered to your screen.                   #
####################################################################################

##rollback function
rollback(){
	case $1 in
		1)#only switchres.ini
			cp /etc/switchres.crt /etc/switchres.ini
			echo "[$(date +"%H:%M:%S")]: Rollbacking switchres.ini " | tee -a /userdata/system/logs/custom_crt_monitor.log
		;;
		2)#switchres.ini and mame.ini
			cp /etc/switchres.crt /etc/switchres.ini
			cp /userdata/system/configs/mame/mame.crt /userdata/system/configs/mame/mame.ini
			echo "[$(date +"%H:%M:%S")]: Rollbacking switchres.ini and mame.ini" | tee -a /userdata/system/logs/custom_crt_monitor.log
		;;
	3)#switchres.ini, mame.ini and (custom-es-config or 99-nvidia)
			cp /etc/switchres.crt /etc/switchres.ini
			cp /userdata/system/configs/mame/mame.crt /userdata/system/configs/mame/mame.ini
			if [[ ! -f /userdata/system/99-nvidia.conf ]]; then
				cp /userdata/system/custom-es-config.crt /userdata/system/custom-es-config
			else
				cp /userdata/system/99-nvidia.conf.crt /userdata/system/99-nvidia.conf
			fi
			echo "[$(date +"%H:%M:%S")]: Rollbacking switchres.ini, mame.ini and custom-es-config" | tee -a /userdata/system/logs/custom_crt_monitor.log
		;;
		*)
			echo "[$(date +"%H:%M:%S")]: Error rollbacking " | tee -a /userdata/system/logs/custom_crt_monitor.log
	esac
}

####################################################################################
#                                                                                  #
#          Use original backup files from BUILD_15KHz-BATOCERA.sh script           #
#                                                                                  #
####################################################################################

echo "[$(date +"%H:%M:%S")]: Start script for creating custom crt monitor for switchres" | tee /userdata/system/logs/custom_crt_monitor.log

if [ ! -f "/etc/switchres.ini.bak" ] ; then
	echo "[$(date +"%H:%M:%S")]: Not found /etc/switchres.ini.bak. Run first BUILD_15KHz-BATOCERA script." | tee -a /userdata/system/logs/custom_crt_monitor.log
	exit
else
	# you need to know which monitor has booted in order to geometry utility work correctly and generate correct modelines
	MONITOR=$(grep -m 1 "monitor     " /etc/switchres.ini | awk '{print $NF}')
	if [[ "$MONITOR" == "custom" ]] ; then
		echo "[$(date +"%H:%M:%S")]: Booted monitor = $MONITOR, so we are going to use arcade_15 instead" | tee -a /userdata/system/logs/custom_crt_monitor.log
		MONITOR="arcade_15"
	else
		echo "[$(date +"%H:%M:%S")]: Booted monitor = $MONITOR" | tee -a /userdata/system/logs/custom_crt_monitor.log
	fi
	cp /etc/switchres.ini /etc/switchres.crt
	cp /etc/switchres.ini.bak /etc/switchres.ini
	
fi

if [ ! -f "/userdata/system/configs/mame/mame.ini.bak" ] ; then
	echo "[$(date +"%H:%M:%S")]: Not found /userdata/system/configs/mame/mame.ini.bak. Run first BUILD_15KHz-BATOCERA script." | tee -a /userdata/system/logs/custom_crt_monitor.log
	rollback 1
	exit
else
	cp /userdata/system/configs/mame/mame.ini /userdata/system/configs/mame/mame.crt
	cp /userdata/system/configs/mame/mame.ini.bak /userdata/system/configs/mame/mame.ini
fi

if [ -f /userdata/system/99-nvidia.conf ]; then
	if  [ ! -f "/userdata/system/99-nvidia.conf.bak" ]; then
		echo "[$(date +"%H:%M:%S")]: Not found /userdata/system/99-nvidia.conf.bak. Run first BUILD_15KHz-BATOCERA script." | tee -a /userdata/system/logs/custom_crt_monitor.log
		rollback 2
		exit
	else
		cp /userdata/system/99-nvidia.conf /userdata/system/99-nvidia.conf.crt
		cp /userdata/system/99-nvidia.conf.bak /userdata/system/99-nvidia.conf 
	fi
else
	if [ ! -f "/userdata/system/custom-es-config.bak" ]; then
		echo "[$(date +"%H:%M:%S")]: Not found /userdata/system/custom-es-config.bak. Run first BUILD_15KHz-BATOCERA script." | tee -a /userdata/system/logs/custom_crt_monitor.log
		rollback 2
		exit
	else
		cp /userdata/system/custom-es-config /userdata/system/custom-es-config.crt
		cp /userdata/system/custom-es-config.bak /userdata/system/custom-es-config
	fi
fi


####################################################################################
#                                                                                  #
#                     Use booted monitor to get resolutions                        #
#                                                                                  #
####################################################################################

#MONITOR=$(grep -m 1 "monitor     " /etc/switchres.ini | awk '{print $NF}')
if [[ ! -f /userdata/system/99-nvidia.conf ]]; then
	# AMD/ATI INTEL and Nvidia(NOUVEAU)
	TYPE_OF_CARD="AMD_INTEL_NVIDIA_NOUV"
	if [[ "$MONITOR" == "arcade_15" ]]; then
		RESOLUTIONS=(	"640x480 60" "768x576 50" "1280x480 60" "1280x576 50" "1280x240 60" "240x240 60" "256x192 60" \
						"256x200 60" "256x224 50" "256x240 60" "288x224 50" "304x224 50" "320x200 60" "320x224 60" \
						"320x240 60" "320x256 60" "352x240 60" "360x200 60" "360x240 60" "380x284 60" "384x216 60" \
						"384x240 60" "384x480 60" "400x200 60" "400x224 60" "400x240 60" "416x240 60" "426x240 60" \
						"427x240 60" "428x240 60" "432x240 60" "432x244 60" "456x256 60" "460x200 60" "464x272 50" \
						"480x240 60" "480x270 60" "480x272 50" "512x288 50" "512x480 60" "528x288 50" "640x240 60" \
						"854x480 60" "864x486 60")
	elif [[ "$MONITOR" == "arcade_15ex" ]]; then
		RESOLUTIONS=(	"640x480 60" "768x576 50" "1280x480 60" "1280x576 50" "1280x240 60" "240x240 60" "256x192 60" \
						"256x200 60" "256x224 60" "256x240 60" "288x224 60" "304x224 60" "320x200 60" "320x224 60" \
						"320x240 60" "320x256 60" "352x240 60" "360x200 60" "360x240 60" "380x284 54" "384x216 60" \
						"384x240 60" "384x480 60" "400x200 60" "400x224 60" "400x240 60" "416x240 60" "426x240 60" \
						"427x240 60" "428x240 60" "432x240 60" "432x244 60" "456x256 60" "460x200 60" "464x272 56" \
						"480x240 60" "480x270 56" "480x272 56" "512x288 50" "512x480 60" "528x288 50" "640x240 60" \
						"854x480 60" "864x486 60")
	elif [[ "$MONITOR" == "arcade_15_25" ]]; then
		RESOLUTIONS=(	"640x480 60" "768x576 50" "1280x480" "1280x576 50" "1280x240" "240x240" "256x192" \
						"320x240 60" "320x256 50" "352x240 60" "360x200 60" "360x240 60" "380x284 50" "384x216 60" \
						"256x200 60" "256x224 60" "256x240 60" "288x224 60" "304x224 60" "320x200 60" "320x224 60" \
						"427x240 60" "428x240 60" "432x240 60" "432x244 60" "456x256 55" "460x200 60" "464x272 50" \
						"384x240 60" "384x480 60" "400x200 60" "400x224 60" "400x240 60" "416x240 60" "426x240 60" \
						"480x240 60" "480x270 50" "480x272 50" "512x288 50" "512x480 60" "528x288 50" "640x240 60" \
						"854x480 60" "864x486 60")
	elif [[ "$MONITOR" == "arcade_15_25_31" ]]; then
		RESOLUTIONS=(	"640x480 60" "768x576 50" "1280x480 60" "1280x576 50" "1280x240 60" "256x192 60" "240x240 60" \
						"256x200 60" "256x224 60" "256x240 60" "288x224 60" "304x224 60" "320x200 60" "320x224 60" \
						"320x240 60" "320x256 60" "352x240 60" "360x200 60" "360x240 60" "380x284 50" "384x216 60" \
						"384x240 60" "384x480 60" "400x200 60" "400x224 60" "400x240 60" "416x240 60" "426x240 60" \
						"427x240 60" "428x240 60" "432x240 60" "432x244 60" "456x256 60" "460x200 60" "464x272 55" \
						"480x240 60" "480x270 55" "480x272 55" "512x288 60" "512x480 60" "528x288 50" "640x240 60" \
						"854x480 60" "864x486 60" )
	elif [[ "$MONITOR" == "generic_15" ]]; then
		RESOLUTIONS=(	"640x480 60" "768x576 50" "1280x480 60" "1280x576 50" "1280x240 60" "240x240 60" "256x192 60" \
						"256x200 60" "256x224 50" "256x240 60" "288x224 50" "304x224 50" "320x200 60" "320x224 60" \
						"320x240 60" "320x256 60" "352x240 60" "360x200 60" "360x240 60" "380x284 60" "384x216 60" \
						"384x240 60" "384x480 60" "400x200 60" "400x224 60" "400x240 60" "416x240 60" "426x240 60" \
						"427x240 60" "428x240 60" "432x240 60" "432x244 60" "456x256 60" "460x200 60" "464x272 50" \
						"480x240 60" "480x270 60" "480x272 50" "512x288 50" "512x480 60" "528x288 50" "640x240 60" \
						"854x480 60" "864x486 60")
	elif [[ "$MONITOR" == "arcade_25" ]]; then
		RESOLUTIONS=(	"1024x768 60" "496x384 60" "512x384 60" "960x768 60"  "1280x768 60"  "1368x768 60" )
	elif [[ "$MONITOR" == "arcade_31" ]]; then
		RESOLUTIONS=(	"640x480 60" "854x480 60" "864x486 60" )
	else
		echo "[$(date +"%H:%M:%S")]: There are problems in your monitor definition" | tee -a /userdata/system/logs/custom_crt_monitor.log
		rollback 3
		exit
	fi
else
	#### NVIDIA (NVIDIA-DRIVERS)
	if [[ "$MONITOR" == "arcade_25" ]]; then
		RESOLUTIONS=(	"384x480" "640x480" "640x480" "720x480" "800x600" "1024x576"  "1280x576"  "854x480" "864x486")

	elif [[ "$MONITOR" == "arcade_31" ]]; then
		RESOLUTIONS=( 	"384x480" "640x480" "640x480" "720x480" "800x600" "1024x576"  "1280x576"  "854x480" "864x486")

	elif [[ "$MONITOR" == "arcade_15" ]]; then
		RESOLUTIONS=(	"3600x480 60" "1920x240 60" "1920x256 50" "1920x480 60" "2560x256 60" "2560x448 60" "1280x480 60" \
						"1024x576 50" "768x576 50"  "854x480 60" "864x486 60"  "800x576 50" "720x480 60" "640x480 60")
	elif [[ "$MONITOR" == "generic_15" ]]; then
		RESOLUTIONS=(	"3600x480 60" "1920x240 60" "1920x256 50" "1920x480 60" "2560x256 60" "2560x448 60" "1280x480 60" \
						"1024x576 50" "768x576 50"  "854x480 60" "864x486 60"  "800x576 50" "720x480 60" "640x480 60")
	else
		echo "[$(date +"%H:%M:%S")]: There are problems in your NVIDIA monitor definition" | tee -a /userdata/system/logs/custom_crt_monitor.log
		rollback 3
		exit
	fi
fi

#### FORCED DOTCLOCK_MIN TO 0 TO USE SWITCHRES 
DOTCLOCK_MIN=$(grep -v "^#" /etc/switchres.ini | grep "dotclock_min" | head -1 | awk '{print $2}')
DOTCLOCK_MIN_SWITCHRES=0
sed -i "s/.*dotclock_min        .*/	dotclock_min              $DOTCLOCK_MIN_SWITCHRES/" /etc/switchres.ini

####################################################################################
#                                                                                  #
#                             Geometry utility start                               #
#                                                                                  #
####################################################################################
RES_GEOM=("[Resolution_calibration]")
if [[ "$TYPE_OF_CARD" == "AMD_INTEL_NVIDIA_NOUV" ]]; then
	xrandr -display :0.0 --delmode  [card_display] "[Resolution_avoid]"
fi
echo "[$(date +"%H:%M:%S")]: Look at your CRT in order to center grid" | tee -a /userdata/system/logs/custom_crt_monitor.log
RES_TOT_GEOM=$(echo $RES_GEOM | sed 's/x/ /')
DISPLAY=:0 geometry $RES_TOT_GEOM | tee /userdata/system/logs/temp_crt.txt >> /userdata/system/logs/custom_crt_monitor.log
if [[ "$TYPE_OF_CARD" == "AMD_INTEL_NVIDIA_NOUV" ]]; then
	~/custom-es-config
#	DISPLAY=:0 batocera-resolution setMode [Resolution_avoid]
fi
escape=$(grep -c "Aborted!" /userdata/system/logs/temp_crt.txt)
if [[ "$escape" -ge 1 ]]; then
	echo "[$(date +"%H:%M:%S")]: Aborted geometry utility." | tee -a /userdata/system/logs/custom_crt_monitor.log
	rollback 3
	exit
fi
echo "[$(date +"%H:%M:%S")]: Parse results and write crt_range0 and custom monitor to /etc/switchres.ini. Custom monitor also to /userdata/system/configs/mame/mame.ini"

sed -i 's/Final crt_range:/crt_range0               /g' /userdata/system/logs/temp_crt.txt
sed -i '1,2d' /userdata/system/logs/temp_crt.txt
sed -i 's/.*monitor         .*/monitor                   custom/' /userdata/system/configs/mame/mame.ini
sed -i '/Final geometry/d' /userdata/system/logs/temp_crt.txt
CRT_0="$(cat /userdata/system/logs/temp_crt.txt)"
sed -i "s/^crt_range0.*/$CRT_0/" /userdata/system/configs/mame/mame.ini
sed -i 's/.*monitor         .*/	monitor                   custom/' /etc/switchres.ini
sed -i '/Final geometry/d' /userdata/system/logs/temp_crt.txt
sed -i 's/crt_range0/        crt_range0/g' /userdata/system/logs/temp_crt.txt
sed -i "s/.*crt_range0   .*/	$CRT_0/" /etc/switchres.ini

####################################################################################
#                                                                                  #
#                           Custom-es-config modelines                             #
#                                                                                  #
####################################################################################

echo "[$(date +"%H:%M:%S")]: Write modelines to custom-es-config or 99-nvidia.conf" | tee -a /userdata/system/logs/custom_crt_monitor.log

for RES in "${RESOLUTIONS[@]}"
do
	RESOLUTION_TOT=$(echo $RES | sed 's/x/ /')
	RESOLUTION=$(echo $RES | cut -d' ' -f1)
	FREQUENCY=$(echo $RES | cut -d' ' -f2)
	FORCED_RESOLUTION="$RESOLUTION@$FREQUENCY"
	switchres $RESOLUTION_TOT -f $FORCED_RESOLUTION -m custom -c | tee /userdata/system/logs/temp_mode.txt >> /userdata/system/logs/custom_crt_monitor.log
	sed -i '/Calculating best video mode/d' /userdata/system/logs/temp_mode.txt
	sed -i 's/^.*"//' /userdata/system/logs/temp_mode.txt
	if [[ "$TYPE_OF_CARD" == "AMD_INTEL_NVIDIA_NOUV" ]]; then
		sed -i 's|^|xrandr -display :0.0 --newmode "'"$RESOLUTION"'" |' /userdata/system/logs/temp_mode.txt
	else
		sed -i 's|^|"'"$RESOLUTION"'" |' /userdata/system/logs/temp_mode.txt
	fi
	TERM="$RESOLUTION"
	MODE_CONTENT="$(cat /userdata/system/logs/temp_mode.txt)"
	if [[ "$TYPE_OF_CARD" == "AMD_INTEL_NVIDIA_NOUV" ]]; then
		sed -i '/^#/!s/xrandr -display :0\.0 --newmode "'"$TERM"'" .*/'"$MODE_CONTENT"'/' /userdata/system/custom-es-config
	else
		sed -i "/\"$TERM\"/c\\       Modeline $MODE_CONTENT" /userdata/system/99-nvidia.conf
	fi
	sed -i '1d' /userdata/system/logs/temp_mode.txt
done

####################################################################################
#                                                                                  #
#                         Cleanup, save overlay and reboot                         #
#                                                                                  #
####################################################################################
### PUT THE GOOD DOTCLOCK_MIN IN SWITCHRES.INI
echo "[$(date +"%H:%M:%S")]: Write dotclock_min ($DOTCLOCK_MIN) in /etc/switchres.ini" | tee -a /userdata/system/logs/custom_crt_monitor.log
sed -i "s/.*dotclock_min        .*/	dotclock_min              $DOTCLOCK_MIN/" /etc/switchres.ini

echo "[$(date +"%H:%M:%S")]: Cleanup, save overlay and reboot" | tee -a /userdata/system/logs/custom_crt_monitor.log
mv /userdata/system/logs/temp_crt.txt /userdata/system/logs/crt_range_0_mod.log
rm /userdata/system/logs/temp_mode.txt

batocera-save-overlay
echo "[$(date +"%H:%M:%S")]: Reboot" | tee -a /userdata/system/logs/custom_crt_monitor.log
reboot
