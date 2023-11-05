#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[1;34m'
NOCOLOR='\033[0m'
clear
echo "[$(date +"%H:%M:%S")]: BUILD_15KHz_Batocera START" > /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo "##                                                                   ##"
echo "##                15KHz BATOCERA V32-V36 CONFIGURATION               ##"
echo "##                                                                   ##"
echo "## RION(15KHz master) MYZAR(Nvidia) ZFEbHVUE(main coder and Tester)  ##"
echo "##                                                                   ##"
echo "##                            19/11/2022                             ##"
echo "##                                                                   ##"
echo "##          BEFORE USING THE SCRIPT READ THE FOLLOWING TEXT          ##"
echo "##                                                                   ##"
echo "##              !! USE THIS SCRIPT ON YOUR OWN RISK !!               ##"
echo "##                                                                   ##"
echo "##        AUTHORS OF THIS SCRIPT WILL NOT BE HELD RESPONSIBLE        ##"
echo "##                     FOR ANY DAMMAGES YOU GET                      ##"
echo "##                                                                   ##"
echo "##        YOU MUST HAVE READ THE 15KHz CRT BATOCERA WIKI PAGE        ##"
echo "##        https://wiki.batocera.org/batocera-and-crt?s[]=crt         ##"
echo "##                                                                   ##"
echo "##                 THIS SCRIPT WORKS ON A LCD SCREEN                 ##"
echo "##           (ALSO IN 15KHz CRT IF YOU ARE ALREADY IN 15)            ##"
echo "##                                                                   ##"
echo "##                                                                   ##"
echo "##         YOU NEED TO HAVE RIGHT CONNECTION FOR 15KHz CRT           ##"
echo "##   AND SOME PROTECTIONS FOR YOUR MONITOR AGAINST BAD FREQUENCIES   ##"
echo "##                                                                   ##"
echo "##                   THE SCRIPT IS OPEN SOURCE                       ##"
echo "##           YOU CAN MODIFY IT / IMPROVE IT / REPORT BUGS            ##"
echo "##                                                                   ##"
echo "##          IF YOU ARE OK WITH THESE CONDITIONS TYPE ENTER           ##"
echo "##                              AND ...                              ##"
echo "##                    HAVE LOTS OF RETRO FUN !!!                     ##"
echo "##                                                                   ##"
echo "## GREETING TO ALL RETRO DEVELOPERS !! (EMULATOR/DISTRIB/FRONTEND...)##"
echo "##                     AND ALL RETRO GAMERS !!                       ##"
echo "##                                                                   ##"
echo "##                                                                   ##"
echo "##                       ==  Cards Tested  ==                        ##"
echo "##                                                                   ##"
echo "##   AMD/ATI:                                                        ##"
echo "##   R7 350x with DVI-I and Display-Port                             ##"
echo "##   R9 280x with DVI-I and Display-Port                             ##"
echo "##                                                                   ##"
echo "##   Intel: display-port and VGA (Optiplex 790/7010                  ##"
echo "##        (VGA works somewhat on)                                    ##"
echo "##                                                                   ##"
echo "##  Nvidia:                                                          ##"
echo "##  8400GS(Tesla)  DVI-I/HDMI/VGA (NOUVEAU)                          ##"
echo "##  Quadro K600(Kelper) DVI-I/(Diplay-Port)  (Nvidia-Driver/Nouveau) ##"
echo "##  GTX980(Maxwell) DVI-I/HDMI/(Diplay-Port) (Nvidia-Driver/Nouveau) ##"
echo "##  GTX1050ti(Pascal) HDMI/(Diplay-Port)     (Nvidia-Driver/Nouveau) ##"
echo "##  GTX1650(turing) (HDMI/Display-Port) Bad 15KHz with only 240p     ##"
echo "##  All display-Port give only 240p with Bad 15KHz                   ##"
echo "##                                                                   ##"
echo "#######################################################################"
echo ""
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO START "
read 
clear

version_Batocera=$(batocera-es-swissknife  --version)

echo "Version batocera = $version_Batocera" >> /userdata/system/logs/BUILD_15KHz_Batocera.log
case $version_Batocera in
	30*)
		echo "Version 30"
		Version_of_batocera="v30"
		version=0
		;;
	31*)
		echo "Version 31"
		Version_of_batocera="v31"
		version=1
		;;
	32*)
		echo "Version 32"
		Version_of_batocera="v32"
		version=2
		;;
	33*)
		echo "Version 33"
		Version_of_batocera="v33"
		version=3
		;;
	34*)
		echo "Version 34"
		Version_of_batocera="v34"
		version=4
		;;
	35*)
		echo "Version 35"
		Version_of_batocera="v35"
		version=5
		;;
	36*)
		echo "Version 36"
		Version_of_batocera="v36"
		version=6
		;;
	37*)
		echo "Version 37"
		Version_of_batocera="v37"
		version=7
		;;
  	38*)
		echo "Version 38 dev"
		Version_of_batocera="v38"
		version=8
		;;
  	39*)
		echo "Version 39 dev"
		Version_of_batocera="v39"
		version=9
		;;
	*)
		echo "unknown version"
		exit 1
		;;
esac

echo "#######################################################################"
echo "##                         CARDS INFORMATION                         ##"
echo "#######################################################################"
j=0
for p in /sys/class/drm/card? ; do
	id=$(basename `readlink -f $p/device`)
	temp=$(lspci -mms $id | cut -d '"' -f4,6)
	name_card[$j]="$temp"
	j=`expr $j + 1`
done
echo ""
for var in "${!name_card[@]}" ; do echo "	$((var+1)) : ${name_card[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
if [[ "$var" -gt 0 ]] ; then
	echo ""
	echo "#######################################################################"
	echo "##                                                                   ##"
	echo "##                Make your choice for graphic card                  ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "##                                                                   ##"
	echo "#######################################################################"
	echo -n "                                  "
	read card_choice
	while [[ ! ${card_choice} =~ ^[1-$((var+1))]$ ]] && [[ "$card_choice" != "" ]] ; do
		echo -n "Select option 1 to $((var+1)):" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		read card_choice
	done
	selected_card=${name_card[$card_choice-1]}
else
	selected_card=${temp}
fi

###############################################################
##    TYPE OF GRAPHIC CARD
###############################################################
Drivers_Nvidia_CHOICE="NONE"

case $selected_card in
	*[Nn][Vv][Ii][Dd][Ii][Aa]*)
		TYPE_OF_CARD="NVIDIA"
		echo ""
		echo "#######################################################################"
		echo -e "##                     YOUR VIDEO CARD IS ${GREEN}NVIDIA${NOCOLOR}                     ##"
		echo "#######################################################################"
		echo ""
		echo "#######################################################################"
		echo "##               Do you want Nvidia_drivers or NOUVEAU               ##"
		echo "#######################################################################"
		declare -a Nvidia_drivers_type=( "Nvidia_Drivers" "NOUVEAU" )
		for var in "${!Nvidia_drivers_type[@]}" ; do echo "			$((var+1)) : ${Nvidia_drivers_type[$var]}"; done
		echo "#######################################################################"
		echo "##                         Make your choice                          ##"
		echo "#######################################################################"
		echo -n "                                  "
		read choice_Drivers_Nvidia
		while [[ ! ${choice_Drivers_Nvidia} =~ ^[1-$((var+1))]$ ]] && [[ "$choice_Drivers_Nvidia" = "" ]] ; do
			echo -n "Select option 1 to $((var+1)):"
			read choice_Drivers_Nvidia
		done
		Drivers_Nvidia_CHOICE=${Nvidia_drivers_type[$choice_Drivers_Nvidia-1]}
		echo -e "                    your choice is :  ${GREEN}$Drivers_Nvidia_CHOICE${NOCOLOR}"
		if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
			echo ""
			echo "#######################################################################"
			echo "##                  Nvidia drivers version selector                  ##"
			echo "#######################################################################"
			declare -a Name_Nvidia_drivers_version=( "true" "legacy" "legacy390" "legacy340" )
			for var in "${!Name_Nvidia_drivers_version[@]}" ; do echo "			$((var+1)) : ${Name_Nvidia_drivers_version[$var]}"; done
			echo "#######################################################################"
			echo "##                         Make your choice                          ##"
			echo "#######################################################################"
			echo -n "                                  "
			read choice_Name_Drivers_Nvidia
			while [[ ! ${choice_Name_Drivers_Nvidia} =~ ^[1-$((var+1))]$ ]] && [[ "$choice_Name_Drivers_Nvidia" = "" ]] ; do
				echo -n "Select option 1 to $((var+1)):"
				read choice_Name_Drivers_Nvidia
			done
			Drivers_Name_Nvidia_CHOICE=${Name_Nvidia_drivers_version[$choice_Name_Drivers_Nvidia-1]}
			echo -e "                    your choice is :  ${GREEN}$Drivers_Name_Nvidia_CHOICE${NOCOLOR}"
	
		fi
	;;
	*[Ii][Nn][Tt][Ee][Ll]*)
		TYPE_OF_CARD="INTEL"
		echo ""
		echo "#######################################################################"
		echo -e "##                     YOUR VIDEO CARD IS ${GREEN}INTEL${NOCOLOR}                      ##"
		echo "#######################################################################"
	;;
	*[Aa][Mm][Dd]* | *[Aa][Tt][Ii]*)
		TYPE_OF_CARD="AMD/ATI"
		echo ""
		echo "#######################################################################"
		echo -e "##                    YOUR VIDEO CARD IS ${GREEN}AMD/ATI${NOCOLOR}                     ##"
		echo "#######################################################################"
		if [[ "$selected_card" =~ "R9" ]] && [[ "$selected_card" =~ "380" ]]; then
			R9_380="YES"
			echo ""
			echo "#######################################################################"
			echo -e "##                    You have an ${GREEN}ATI R9 380/380x${NOCOLOR}                    ##"
			echo "#######################################################################"
			if grep -q "amdgpu.dc=0" "/boot/EFI/syslinux.cfg" && grep -q "amdgpu.dc=0" "/boot/EFI/BOOT/syslinux.cfg" && grep -q "amdgpu.dc=0" "/boot/boot/syslinux.cfg" && grep -q "amdgpu.dc=0" "/boot/boot/syslinux/syslinux.cfg" ; then
				echo ""
				echo "#######################################################################"
				echo -e "##                   ${GREEN}This card is ready for 15KHz${NOCOLOR}                    ##"
				echo "#######################################################################"
				echo ""
				read
			else
				echo "#######################################################################"
				echo -e "##                 ${RED}This card isn't ready for 15KHz${NOCOLOR}                   ##"
				echo "##                   Need to update syslinux.cfg                     ##"
				echo "#######################################################################"
				echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO UPDATE syslinux.cfg "
				term_R9_380_amdgpu="mitigations=off amdgpu.dc=0 "
				read
				mount -o remount, rw /boot
				sed -e "s/mitigations=off/$term_R9_380_amdgpu/g"  /userdata/system/BUILD_15KHz/Boot_configs/syslinux.cfg.default > /boot/EFI/syslinux.cfg
				chmod 755 /boot/EFI/syslinux.cfg
				#############################################################################
				## Copy syslinux for EFI and legacy boot
				#############################################################################
				cp /boot/EFI/syslinux.cfg /boot/EFI/BOOT/
				cp /boot/EFI/syslinux.cfg /boot/boot
				cp /boot/EFI/syslinux.cfg /boot/boot/syslinux
				echo "#######################################################################"
				echo "##           ENTER to reboot and make you card 15KHz ready           ##"
				echo "#######################################################################"
				echo -n -e "                    PRESS ${BLUE}ENTER${NOCOLOR} TO REBOOT "
				read
				reboot
				exit
			fi
		else
			R9_380="NO"
			echo ""
			echo "#######################################################################"
			echo -e "##                  ${GREEN}This card is ready for 15KHz${NOCOLOR}                     ##"
			echo "#######################################################################"
			echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
			read
		fi
	;;
	*)
		echo "!!!! BE CAREFULL YOUR CARD IS UNKNOWN !!!!"
		exit 1
	;;
esac
echo "	Selected card = $selected_card" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log

#####################################################################################################################################################
#####################################################################################################################################################
echo "#######################################################################"
echo "##                       Detected card outputs                       ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo ""
j=0; declare -a OutputVideo; for i in `ls /sys/class/drm |grep -E -i "^card.-.*" |sed -e 's/card.-//'`; do OutputVideo[$j]="$i"; j=`expr $j + 1`; done
valid_card=$(basename $(dirname $(grep -E -l "^connected" /sys/class/drm/*/status))|sed -e "s,card0-,,")
for var in "${!OutputVideo[@]}" ; do echo "			$((var+1)) : ${OutputVideo[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##                                                                   ##"
echo -e "##                 your connected output: ${GREEN}$valid_card${NOCOLOR}                     ##"
echo "##                                                                   ##"
echo "##                 Make your choice for 15KHz output                 ##"
echo "##                 or press ENTER for connected one                  ##"
echo "##                                                                   ##"
echo "#######################################################################"
echo -n "                                  "
read video_output_choice
while [[ ! ${video_output_choice} =~ ^[1-$((var+1))]$ ]] && [[ "$video_output_choice" != "" ]] ; do
	echo -n "Select option 1 to $((var+1)):" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	read video_output_choice
done
video_output=${OutputVideo[$video_output_choice-1]}
echo -e "                    your choice is :${GREEN}  $video_output${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log


########################################################################################
#####################              15KHz/25KHz/31KHz                  ##################
########################################################################################
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
read
clear
echo ""
echo "#######################################################################"
echo "##            15KHz, 25KHz OR 31KHz CRT screen selection             ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo ""
declare -a CRT_Frequency=( "15KHz" "25KHz" "31KHz" )
for var in "${!CRT_Frequency[@]}" ; do echo "			$((var+1)) : ${CRT_Frequency[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##               Make your choice the frequency screen               ##"
echo "#######################################################################"
echo -n "                                  "
read CRT_Frequency_choice
while [[ ! ${CRT_Frequency_choice} =~ ^[1-$((var+1))]$ ]] ; do
	echo -n "Select option 1 to $((var+1)):" 
	read CRT_Frequency_choice
done
CRT_Freq=${CRT_Frequency[$CRT_Frequency_choice-1]}
echo -e "                    your choice is :${GREEN}  $CRT_Freq${NOCOLOR}"

########################################################################################
#####################               GENERAL  MONITOR                  ##################
########################################################################################
echo ""
echo "#######################################################################"
echo "##                     Monitor type selector                         ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo ""
if [ "$CRT_Freq" == "15KHz" ]; then
	if [ "$TYPE_OF_CARD" == "INTEL" ]; then
		if [[ "$video_output" == *"VGA"* ]]; then
			declare -a type_of_monitor=( "arcade_15_SR480" "generic_15_SR480" )
			elif [[ "$video_output" == *"DP"* ]]; then
				declare -a type_of_monitor=( "arcade_15" "arcade_15_25_31" "arcade_15ex" "generic_15" "ntsc" "pal")
			elif [[ "$video_output" == *"HDMI"* ]]; then
				declare -a type_of_monitor=( "arcade_15_SR480" "generic_15_SR480" )
		fi
	elif [ "$TYPE_OF_CARD" == "NVIDIA" ]; then
		if [[ "$video_output" == *"DVI"* ]]; then
			declare -a type_of_monitor=( "arcade_15_SR480" "generic_15_SR480" )
		elif [[ "$video_output" == *"VGA"* ]]; then
			declare -a type_of_monitor=( "arcade_15_SR480" "generic_15_SR480" "arcade_15_SR240" "generic_15_SR240" )
			elif [[ "$video_output" == *"DP"* ]]; then
				declare -a type_of_monitor=( "arcade_15_SR240" "generic_15_SR240" )
			elif [[ "$video_output" == *"HDMI"* ]]; then
				declare -a type_of_monitor=( "arcade_15_SR480" "generic_15_SR480" )
			else
				declare -a type_of_monitor=( "arcade_15" "arcade_15_25_31" "arcade_15ex" "generic_15" "ntsc" "pal")
		fi	
	elif [ "$TYPE_OF_CARD" == "AMD/ATI" ]; then
		declare -a type_of_monitor=( "arcade_15" "arcade_15_25_31" "arcade_15ex" "generic_15" "ntsc" "pal") 
	fi
	for var in "${!type_of_monitor[@]}" ; do echo "			$((var+1)) : ${type_of_monitor[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
	echo ""
	echo "#######################################################################"
	echo "##                 Make your choice for monitor type                 ##"
	echo "#######################################################################"
	echo -n "                                  "
	read monitor_choice
	while [[ ! ${monitor_choice} =~ ^[1-$((var+1))]$ ]] ; do
		echo -n "Select option 1 to $((var+1)):"
		read monitor_choice
	done
	monitor_firmware=${type_of_monitor[$monitor_choice-1]}
	echo -e "                    your choice is :${GREEN}  $monitor_firmware${NOCOLOR}"
elif [ "$CRT_Freq" == "25KHz" ]; then
	monitor_firmware="arcade_25"
else
	monitor_firmware="arcade_31"
fi
monitor_name=$monitor_firmware
 echo "monitor firmware = $monitor_firmware" >> /userdata/system/logs/BUILD_15KHz_Batocera.log
#monitor_firmware+=".bin"


########################################################################################
#####################                MAME MONITOR                 ######################
########################################################################################
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
read
clear
if [ "$CRT_Freq" == "15KHz" ]; then
	echo ""
	echo "#######################################################################"
	echo "##             Configure a specific monitor for M.A.M.E              ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "#######################################################################"
	echo ""
	declare -a Mame_monitor_choice=( "YES" "NO" ) 
	for var in "${!Mame_monitor_choice[@]}" ; do echo "			$((var+1)) : ${Mame_monitor_choice[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
	echo ""
	echo "#######################################################################"
	echo "##                         Make your choice                          ##"
	echo "#######################################################################"
	echo -n "                                  "
	read choice_MAME_monitor
	while [[ ! ${choice_MAME_monitor} =~ ^[1-$((var+1))]$ ]] ; do
		echo -n "Select option 1 to $((var+1)):"
		read choice_MAME_monitor
	done
	if [ -z "$choice_MAME_monitor" ] ; then 
		echo -e "                    your choice is :${GREEN} Bypass this configuration${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		monitor_name_MAME=$monitor_firmware
	else
		monitor_MAME_CHOICE=${Mame_monitor_choice[$choice_MAME_monitor-1]}
		echo -e "                    your choice is :${GREEN}  $monitor_MAME_CHOICE${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		if [ "$monitor_MAME_CHOICE" == "YES" ]; then
			echo ""
			echo "#######################################################################"
			echo "##                       M.A.M.E monitor type                        ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
			echo "#######################################################################"
			echo ""
			if [ "$TYPE_OF_CARD" == "INTEL" ] ||  [ "$TYPE_OF_CARD" == "NVIDIA" ]; then 
				declare -a type_of_monitor=( "arcade_15" "arcade_15_SR480" "arcade_15_SR240" "arcade_15_25_31" \
											 "arcade_15ex" "generic_15" "generic_15_SR480" "generic_15_SR240" "ntsc" "pal" )
			else
				declare -a type_of_monitor=( "arcade_15" "arcade_15_25_31" \
												 "arcade_15ex" "generic_15" "ntsc" "pal" )
			fi
			for var in "${!type_of_monitor[@]}" ; do echo "			$((var+1)) : ${type_of_monitor[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
			echo ""
			echo "#######################################################################"
			echo "##   Make your choice for your monitor for playing Groovy M.A.M.E.   ##" 
			echo "#######################################################################"
			echo -n "                                  "
			read monitor_choice_MAME
				while [[ ! $monitor_choice_MAME =~ ^[0-9]+$ || "$monitor_choice_MAME" -lt 1 || "$monitor_choice_MAME" -gt $var+1 ]] ; do 
					echo -n "Select option 1 to $((var+1)):"
					read monitor_choice_MAME
				done
			monitor_firmware_MAME=${type_of_monitor[$monitor_choice_MAME-1]}
			echo -e "                    your choice is :${GREEN}  $monitor_firmware_MAME${NOCOLOR}"
			monitor_name_MAME=$monitor_firmware_MAME
		else
			monitor_name_MAME=$monitor_firmware
		fi
	fi

elif [ "$CRT_Freq" == "25KHz" ]; then
	monitor_name_MAME="arcade_25"
else
	monitor_name_MAME="arcade_31"
fi
echo "monitor mame = $monitor_name_MAME"  >> /userdata/system/logs/BUILD_15KHz_Batocera.log

########################################################################################
#####################              BOOT RESOLUTION        ##############################
########################################################################################
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
read
clear
echo ""
echo "#######################################################################"
echo "##                      Boot Resolution                              ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo ""
if [ "$CRT_Freq" == "15KHz" ]; then
	if [ "$TYPE_OF_CARD" == "INTEL" ] ; then
		if [[ "$video_output" == *"VGA"* ]]; then
			declare -a boot_resolution=( "1280x480ieS" "1280x240ieS" )
		elif [[ "$video_output" == *"DP"* ]]; then
			if [[ $monitor_name == "ntsc" ]]; then
				declare -a boot_resolution=( "720x480ieS" "640x480ieS" )
			else
				declare -a boot_resolution=( "768x576ieS" "640x480ieS" )
			fi
		elif [[ "$video_output" == *"HDMI"* ]]; then
			declare -a boot_resolution=( "1280x480ieS" "1280x240ieS" )
		fi
	elif [ "$TYPE_OF_CARD" == "NVIDIA" ] ; then
		if [[ "$video_output" == *"DVI"* ]]; then
			declare -a boot_resolution=( "1280x480ieS" "1280x240ieS" )
		elif [[ "$video_output" == *"VGA"* ]]; then
			declare -a boot_resolution=( "1280x480ieS" "1280x240ieS" )
		elif [[ "$video_output" == *"DP"* ]]; then
			declare -a boot_resolution=("1280x240ieS" )
		elif  [[ "$video_output" == *"HDMI"* ]]; then
			declare -a boot_resolution=( "1280x480ieS" "1280x240ieS" )
		fi
	else
		if [[ $monitor_name == "ntsc" ]]; then
			declare -a boot_resolution=( "720x480ieS" "640x480ieS" "648x478ieS")
		else
			declare -a boot_resolution=( "768x576ieS" "640x480ieS" "648x478ieS" )
		fi
	fi
	for var in "${!boot_resolution[@]}" ; do echo "			$((var+1)) : ${boot_resolution[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
	echo ""
	echo "#######################################################################"
	echo "##             Make your choice for the boot resolution              ##"
	echo "#######################################################################"
	echo -n "                                  "
	read boot_resolution_choice
	while [[ ! ${boot_resolution_choice} =~ ^[1-$((var+1))]$ ]] ; do
		echo -n "Select option 1 to $((var+1)):"
		read boot_resolution_choice
	done
	boot_resolution=${boot_resolution[$boot_resolution_choice-1]}
	echo -e "                    your choice is :${GREEN}  $boot_resolution${NOCOLOR}"
elif [ "$CRT_Freq" == "25KHz" ]; then
	boot_resolution="e"
else
	boot_resolution="e"
fi

echo "Boot resolution = $boot_resolution" >> /userdata/system/logs/BUILD_15KHz_Batocera.log

################################################################################################################################
#####################              ES RESOLUTION          ######################################################################
################################################################################################################################

if [ "$CRT_Freq" == "15KHz" ]; then
	if ([ "$Drivers_Nvidia_CHOICE" == "NONE" ] || [ "$Drivers_Nvidia_CHOICE" == "NOUVEAU" ]); then
		echo ""
		echo "#######################################################################"
		echo "##                    EmulationStation Resolution                    ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		echo "#######################################################################"
		echo ""
		if [ "$TYPE_OF_CARD" == "INTEL" ]; then
			if [[ "$video_output" == *"VGA"* ]]; then
				declare -a ES_resolution=( "1280x576_50iHz" "1280x480_60iHz" )
				declare -a ES_resolution_V33=( "1280x576_50" "1280x480_60" )
			elif [[ "$video_output" == *"DP"* ]]; then	
				if [[ $monitor_name == "ntsc" ]]; then
					declare -a ES_resolution=( "720x480_60iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "720x480" "640x480" )
				else
					declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "768x576" "640x480" )
				fi
			elif [[ "$video_output" == *"HDMI"* ]]; then
				if [[ $monitor_name == "ntsc" ]]; then
					declare -a ES_resolution=( "720x480_60iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "720x480" "640x480" )
				else
					declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "768x576" "640x480" )
				fi
			fi
		elif [ "$TYPE_OF_CARD" == "NVIDIA" ] ; then
			if [[ "$video_output" == *"DVI"* ]]; then
				if [[ $monitor_name == "ntsc" ]]; then
					declare -a ES_resolution=( "720x480_60iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "720x480" "640x480" )
				else
					declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "768x576" "640x480" )
				fi
			elif [[ "$video_output" == *"VGA"* ]]; then
				if [[ $monitor_name == "ntsc" ]]; then
					declare -a ES_resolution=( "720x480_60iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "720x480" "640x480" )
				else
					declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" )
					declare -a ES_resolution_V33=( "768x576" "640x480" )
				fi
			elif [[ "$video_output" == *"DP"* ]]; then
				declare -a ES_resolution=( "1280x240_60iHz" )
				declare -a ES_resolution_V33=( "1280x240" )	
			elif [[ "$video_output" == *"HDMI"* ]]; then
				if [[ $monitor_name == "ntsc" ]]; then
					declare -a ES_resolution=( "720x480_60iHz" "640x480_60iHz" "1280x576_50iHz" "1280x480_60iHz" "1280x240_60iHz") 
					declare -a ES_resolution_V33=( "720x480" "640x480" "1280x576_50" "1280x480_60" "1280x240_60")
				else
					declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" "1280x576_50iHz" "1280x480_60iHz" "1280x240_60iHz") 
					declare -a ES_resolution_V33=( "768x576" "640x480" "1280x576_50" "1280x480_60" "1280x240_60")
				fi
			fi
		else
			if [[ $monitor_name == "ntsc" ]]; then
				declare -a ES_resolution=( "720x480_60iHz" "640x480_60iHz" )	
				declare -a ES_resolution_V33=( "720x480" "640x480" )
			else
				declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" )
				declare -a ES_resolution_V33=( "768x576" "640x480" )
			fi
		fi
		for var in "${!ES_resolution[@]}" ; do echo "			$((var+1)) : ${ES_resolution[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
		echo ""
		echo "#######################################################################"
		echo "##       Make your choice for the EmulationStation Resolution        ##"
		echo "#######################################################################"
		echo -n "                                  "
		read es_resolution_choice
		while [[ ! ${es_resolution_choice} =~ ^[1-$((var+1))]$ ]] ; do
			echo -n "Select option 1 to $((var+1)):"
			read es_resolution_choice
		done
		ES_resolution=${ES_resolution[$es_resolution_choice-1]}
		ES_resolution_V33=${ES_resolution_V33[$es_resolution_choice-1]}
		echo -e "                    Your choice is :  ${GREEN}$ES_resolution${NOCOLOR}"
	else
		echo ""
		echo "#######################################################################"
		echo "##                    EmulationStation Resolution                    ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		echo "##                      NVIDIA (Nvidia Drivers)                      ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		echo "#######################################################################"
		echo ""
		if [[ "$video_output" == *"DVI"* ]]; then
			declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz" )
			declare -a ES_resolution_V33=( "768x576" "640x480" )
		elif [[ "$video_output" == *"VGA"* ]]; then
			declare -a ES_resolution=( "1280x576_50iHz" "1280x480_60iHz" "1280x240_60iHz")
			declare -a ES_resolution_V33=( "640x480" "1280x576_50" "1280x480_60" "1280x240_60")
		elif [[ "$video_output" == *"DP"* ]]; then
			declare -a ES_resolution=( "1920x240_60iHz" "1920x256_50iHz")
			declare -a ES_resolution_V33=( "1920x240" "1920x256" )
		elif [[ "$video_output" == *"HDMI"* ]]; then
			declare -a ES_resolution=( "768x576_50iHz" "640x480_60iHz"  "1280x480_60iHz" "1280x240_60iHz")
			declare -a ES_resolution_V33=( "768x576" "640x480" "1280x480_60" "1280x240_60")
		fi
		for var in "${!ES_resolution[@]}" ; do echo "			$((var+1)) : ${ES_resolution[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
		echo ""
		echo "#######################################################################"
		echo "##       Make your choice for the EmulationStation Resolution        ##"
		echo "#######################################################################"
		echo -n "                                  "
		read es_resolution_choice
		while [[ ! ${es_resolution_choice} =~ ^[1-$((var+1))]$ ]] ; do
			echo -n "Select option 1 to $((var+1)):"
			read es_resolution_choice
		done
		ES_resolution=${ES_resolution[$es_resolution_choice-1]}
		ES_resolution_V33=${ES_resolution_V33[$es_resolution_choice-1]}
		echo -e "                    Your choice is :  ${GREEN}$ES_resolution${NOCOLOR}"
		

	fi
elif [ "$CRT_Freq" == "25KHz" ]; then
	ES_resolution="1024x768_60iHz"
	ES_resolution_V33="1024x768"
else
	ES_resolution="640x480_60iHz"
	ES_resolution_V33="640x480"
fi
echo "ES_resolution = $ES_resolution" >> /userdata/system/logs/BUILD_15KHz_Batocera.log

################################################################################################################################
#######################################                  ROTATION                   ############################################
################################################################################################################################
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
read
clear
echo ""
echo "#######################################################################"
echo "##                          ROTATING SCREEN                          ##"
echo "##                                                                   ##"
echo "##              FORM THE ACTUAL POSITION OF YOUR MONITOR             ##"
echo "##                    WHAT IS THE SENS OF ROTATION                   ##"
echo "##               TO PASS TO HORIZONTAL OR TO VERTICAL                ##"
echo "##                                                                   ##"
echo "##   IF YOU WANT TO PLAY HORIZONTAL OR VERTICAL GAMES ON YOUR        ##"
echo "##   MONITOR WITHOUT ROTATION PUT : NONE                             ##"
echo "##                                                                   ##"
echo "##                          REMEMBER                                 ##"
echo "##                                                                   ##"
echo "##   FOR MAME(Groovymame) IT WORKS FOR ALL HORIZONTAL AND VERTICAL   ##"
echo "##                        GAMES FOR ALL CONFIGURATIONS SCREEN SETUP  ##"
echo "##                                                                   ##"
echo "##   FOR FBNEO:           HORIZONTAL SCREEN:                         ##"
echo "##                        HORIZONTAL GAMES  (NO ROTATION)            ##"
echo "##                        VERTICAL  GAMES   (WITH ROTATION)          ##"
echo "##                        VERTICAL  SCREEN:                          ##"
echo "##                        HORIZONTAL GAMES  (WITH ROTATION)          ##"
echo "##                        VERTICAL  GAMES   (NO ROTATION)            ##"
echo "##                                                                   ##"
echo "##   FOR LIBRETRO:        IT WORKS FOR ALL HORIZONTAL GAMES FOR      ##"
echo "##                        ROTATING SCREEN WITH BUG IN TATE           ##"
echo "##                                                                   ##"
echo "##   FOR STANDALONE:      IT WORKS FOR HORIZONTAL GAMES FOR          ##"
echo "##                        ROTATING SCREEN                            ##"
echo "##                        THERE ARE SOME BUG FOR SOME EMULATORS      ##"
echo "##                        IN TATE (WINDOWS/...)                      ##"
echo "##                                                                   ##"
echo "##   FOR FPINBALL         IT WORKS FOR IN HORIZONTALE AND VERTICALE  ##"
echo "##                        SCREEN                                     ##"
echo "##                                                                   ##"
echo "## ALL THESE THINGS ARE TO PLAY CLASSIC HORIZONTAL GAMES ON VERTICAL ##"
echo "## SCREEN WITH OR WITHOUT ROTATION WITH CLASSIC EMULATORS. REMENBER  ##"
echo "## BY DEFAULT THEY RUN ON HORIZONTAL SCREEN (WITH NO ROTATION)       ##"
echo "##                                                                   ##"
echo "## ONLY GROOVYMAME CAN PLAY HORIZONTAL OR VERTICAL GAMES ON ANY      ##"
echo "## SCREEN POSITION BECAUSE GROOVYMAME CAN DETECT IF THE GAMES ARE    ##"
echo "## HORITONTAL OR VERTCIAL AT THE START OF THE GAME                   ##"
echo "##                                                                   ##"
echo "#######################################################################"
echo ""
declare -a Screen_rotating=( "None" "Clockwise" "Counter-Clockwise" )
for var in "${!Screen_rotating[@]}" ; do echo "			$((var+1)) : ${Screen_rotating[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##       Make your choice for the sens of your rotation screen       ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo -n "                                  "
read Screen_rotating_choice
	while [[ ! ${Screen_rotating_choice} =~ ^[1-$((var+1))]$ ]] ; do
		echo -n "Select option 1 to $((var+1)):"
		read Screen_rotating_choice
	done
Rotating_screen=${Screen_rotating[$Screen_rotating_choice-1]}

echo -e "                    Your choice is : ${GREEN} $Rotating_screen${NOCOLOR}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo ""
echo "#######################################################################"
echo "##                  EmulationStation ORIENTATION                     ##"
echo "##            MONITOR SETUP (FROM HORIZONTAL POSITION)               ##"
echo "##                                                                   ##"
echo "## HORIZONTAL                     MONITOR  = NORMAL   (0°)           ##"
echo "## VERTICAL   (Counter-Clockwise) MONITOR  = TATE90   (90°)          ##"
echo "## HORIZONTAL (Inverted)          MONITOR  = INVERTED (180°)         ##"
echo "## VERTICAL   (Clockwise)         MONITOR =  TATE270  (-90° or 270°) ##"
echo "##                                                                   ##"
echo "#######################################################################"
echo ""
declare -a ES_orientation=( "NORMAL" "TATE90" "INVERTED" "TATE270" )

if ([ "$TYPE_OF_CARD" == "NVIDIA" ]&&[ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]); then
	declare -a display_rotation=( "normal" "normal" "normal" "normal" )
	declare -a display_mame_rotation=( "normal" "left" "normal" "right" )
	case $Rotating_screen in
		None)
			declare -a display_libretro_rotation=( "normal" "right" "normal" "right" )
			declare -a display_standalone_rotation=( "normal" "normal" "normal" "normal" )
			declare -a display_fbneo_rotation=( "normal" "right" "normal" "right" )
		;;
		Clockwise)
			declare -a display_libretro_rotation=( "normal" "left" "normal" "right")
			declare -a display_standalone_rotation=( "normal" "left" "normal" "left" )
			declare -a display_fbneo_rotation=( "normal" "right" "normal" "right" )

		;;
		Counter-Clockwise)
			declare -a display_libretro_rotation=( "normal" "right" "normal"  "right" )
			declare -a display_standalone_rotation=( "normal" "right" "normal" "right" )
			declare -a display_fbneo_rotation=( "normal" "right" "normal" "right" )
		;;
		*)
			echo "problems of choice of rotation"
		;;
	esac
else
	declare -a display_rotation=( "normal" "right" "inverted" "left" )
	declare -a display_mame_rotation=( "normal" "normal" "inverted" "normal" )
	case $Rotating_screen in
		None)
			declare -a display_libretro_rotation=( "normal" "right" "inverted" "left" )
			declare -a display_standalone_rotation=( "normal" "right" "inverted" "left" )
			declare -a display_fbneo_rotation=( "normal" "inverted" "inverted" "normal" )
		;;
		Clockwise)
			declare -a display_libretro_rotation=( "normal" "normal" "inverted" "inverted" )
			declare -a display_standalone_rotation=( "normal" "normal" "inverted" "inverted" )
			declare -a display_fbneo_rotation=( "normal" "inverted" "inverted" "normal" )
		;;
		Counter-Clockwise)
			declare -a display_libretro_rotation=( "normal" "inverted" "inverted" "normal" )
			declare -a display_standalone_rotation=( "normal" "inverted" "inverted" "normal" )
			declare -a display_fbneo_rotation=( "normal" "inverted" "inverted" "normal" )
		;;
		*)
			echo "problems of choice of rotation"
		;;
	esac
fi
for var in "${!ES_orientation[@]}" ; do echo "			$((var+1)) : ${ES_orientation[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##       Make your choice for the EmulationStation ORIENTATION       ##"
echo "#######################################################################"
echo -n "                                  "
read es_rotation_choice
while [[ ! ${es_rotation_choice} =~ ^[1-$((var+1))]$ ]] ; do
	echo -n "Select option 1 to $((var+1)):"
	read es_rotation_choice
done
ES_rotation=${ES_orientation[$es_rotation_choice-1]}
display_rotate=${display_rotation[$es_rotation_choice-1]}
display_mame_rotate=${display_mame_rotation[$es_rotation_choice-1]}
display_libretro_rotate=${display_libretro_rotation[$es_rotation_choice-1]}
display_standalone_rotate=${display_standalone_rotation[$es_rotation_choice-1]}
display_fbneo_rotate=${display_fbneo_rotation[$es_rotation_choice-1]}

echo -e "                    Your choice is :  ${GREEN}$ES_rotation${NOCOLOR}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log

################################################################################################################################
##########################################      Super-resolutions       ########################################################
################################################################################################################################

super_width_vertical=1920
interlace_vertical=0
dotclock_min_vertical=25

super_width_horizont=1920
interlace_horizont=0
dotclock_min_horizont=25

if [ "$TYPE_OF_CARD" == "AMD/ATI" ]; then
	echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
	read
	clear
	echo "#######################################################################"
	echo "##                                                                   ##"
	echo "##          Which graphig card drivers you want to use ?             ##"
	echo "##                                                                   ##"
	echo "##              If you get a black screen after reboot               ##"
	echo "##                    then choose another driver                     ##"
	echo "##                                                                   ##"
	echo "##         Please note, RX and R cards older than the R7 240         ##"
	echo "##        just do not support the amdgpu drivers, period, and        ##"
	echo "##           doing this while using them will result in a            ##"
	echo "##                     black screen after reboot                     ##"
	echo "##                                                                   ##"
	echo "#######################################################################"
	echo ""
	declare -a driver_ATI=( "AMDGPU" "RADEON" )
	for var in "${!driver_ATI[@]}" ; do echo "			$((var+1)) : ${driver_ATI[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
	echo ""
	echo "#######################################################################"
	echo "##               Make your choice for your video card                ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "#######################################################################"
	echo -n "                                  "
	read type_of_drivers
	while [[ ! ${type_of_drivers} =~ ^[1-$((var+1))]$ ]] ; do
		echo -n "Select option 1 to $((var+1)):"
		read type_of_drivers
	done
	drivers_type=${driver_ATI[$type_of_drivers-1]}
	echo -e "                    Your choice is :   ${GREEN}$drivers_type${NOCOLOR}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo ""

	dotclock_min=0	
	dotclock_min_mame=$dotclock_min
	super_width=2560
	super_width_mame=2560 

	if [ "$drivers_type" == "AMDGPU" ]; then
		if [ "$R9_380" == "YES" ]; then
			drivers_amd="amdgpu.dc=0"
		else
			drivers_amd="radeon.si_support=0 amdgpu.si_support=1 radeon.cik_support=0 amdgpu.cik_support=1"
		fi
	else
		if [ "$R9_380" == "YES" ]; then
			drivers_amd="radeon.si_support=1 amdgpu.si_support=0 radeon.cik_support=1 amdgpu.cik_support=0"
		else
			drivers_amd=""
		fi
	fi
	if [[ "$video_output" == *"DP"* ]]; then
		term_dp="DP"
		term_displayport="DisplayPort"
		video_display=${video_output/$term_dp/$term_displayport}
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_modeline=$term_displayport-$((nbr-1))
	elif [[ $video_output == *"DVI"* ]]; then
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_display=$video_output
	if [ "$drivers_type" == "AMDGPU" ]; then
		term_DVI=DVI-I
		if [ "$R9_380" == "YES" ]; then
			video_modeline=$term_DVI-$((nbr))
		else
			video_modeline=$term_DVI-$((nbr-1))
		fi
else
	term_DVI=DVI
	if [ "$R9_380" == "YES" ]; then
		video_modeline=$term_DVI-$((nbr))
	else
		video_modeline=$term_DVI-$((nbr-1))
	fi
fi
elif [[ "$video_output" == *"VGA"* ]]; then
	term_VGA=VGA
	nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
	video_display=$video_output
	video_modeline=$term_VGA-$((nbr-1))
fi
elif [ "$TYPE_OF_CARD" == "INTEL" ]; then
	drivers_amd=""
	if [[ "$video_output" == *"DP"* ]]; then
		term_dp="DP"
		term_displayport="DisplayPort"
		video_display=$video_output 
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_modeline=$term_dp-$((nbr))   
		dotclock_min=0
		dotclock_min_mame=$dotclock_min
		super_width=1920
		super_width_mame=$super_width
	elif [[ "$video_output" == *"VGA"* ]]; then
		term_VGA="VGA"
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_display=$video_output
		video_modeline=$term_VGA-$((nbr))
		dotclock_min=25.0
		dotclock_min_mame=$dotclock_min
		super_width=1920
		super_width_mame=$super_width
	fi
elif [ "$TYPE_OF_CARD" == "NVIDIA" ]; then
	drivers_amd=""
	if [[ "$video_output" == *"DP"* ]]; then
		term_dp="DP"
		term_displayport="DisplayPort"
		video_display=$video_output 
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
			if [ "$Drivers_Name_Nvidia_CHOICE" == "legacy" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy390" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy340" ]; then
				video_modeline=$term_dp-$((nbr)) 
				dotclock_min=0
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			else
				video_modeline=$term_dp-$((nbr-1)) 
				dotclock_min=0
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			fi
		else	
			video_modeline=$term_dp-$((nbr)) 
			dotclock_min=0
			super_width=3840
			super_width_mame=$super_width
		fi
	elif [[ "$video_output" == *"DVI"* ]]; then
		term_DVI=DVI-I
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_display=$video_output
		if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
			if [ "$Drivers_Name_Nvidia_CHOICE" == "legacy" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy390" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy340" ]; then
				video_modeline=$term_DVI-$((nbr-1))
				dotclock_min=25
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			else
				video_modeline=$term_DVI-$((nbr-1))
				dotclock_min=0
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			fi
		else
			video_modeline=$term_DVI-$((nbr))
			dotclock_min=0
			dotclock_min_mame=$dotclock_min
			super_width=3840
			super_width_mame=$super_width
		fi
	elif [[ "$video_output" == *"HDMI"* ]] ; then
		term_HDMI=HDMI
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_display=$video_output
		if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
			if [ "$Drivers_Name_Nvidia_CHOICE" == "legacy" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy390" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy340" ]; then	
				video_modeline=$term_HDMI-$((nbr-1))
				dotclock_min=25.0
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			else
				video_modeline=$term_HDMI-$((nbr-1))
			 	dotclock_min=25.0
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			fi
		else
			video_modeline=$term_HDMI-$((nbr))
			dotclock_min=25.0
			dotclock_min_mame=$dotclock_min
			super_width=3840
			super_width_mame=$super_width
		fi
	elif [[ "$video_output" == *"VGA"* ]] ; then
		term_VGA=VGA
		nbr=$(sed 's/[^[:digit:]]//g' <<< "${video_output}")
		video_display=$video_output
		if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
			if [ "$Drivers_Name_Nvidia_CHOICE" == "legacy" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy390" ]||[ "$Drivers_Name_Nvidia_CHOICE" == "legacy340" ]; then	
				video_modeline=$term_VGA-$((nbr-1))
				dotclock_min=25.0
				dotclock_min_mame=$dotclock_min
				super_width=3840
				super_width_mame=$super_width
			else
				video_modeline=$term_VGA-$((nbr-1))
				dotclock_min=25.0
				dotclock_min_mame=$dotclock_min
				super_widthe=3840
				super_width_mame=$super_width
			fi
		else
			video_modeline=$term_VGA-$((nbr))
			dotclock_min=0.0
			dotclock_min_mame=$dotclock_min
			super_width=3840
			super_width_mame=$super_width
		fi
	fi
fi

if [ "$CRT_Freq" == "31KHz" ]; then
	dotclock_min=25.0
	dotclock_min_mame=$dotclock_min
fi

#######################################################################
###                 Start of ADVANCED CONFIGURATION                ####
#######################################################################
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
read
clear
echo "#######################################################################"
echo "##                                                                   ##"
echo "##                      ADVANCED CONFIGURATION                       ##"
echo "##                                                                   ##"
echo "##                     Experimental options for:                     ##"
echo "##                        * minimum dotclock                         ##"
echo "##                        * super-resolution                         ##" 
echo "##                                                                   ##"
echo "##       (If you don't know what this means, just press ENTER)       ##"
echo "##                                                                   ##"
echo "#######################################################################" 
echo ""
declare -a Default_DT_SR_choice=( "YES" "NO" ) 
for var in "${!Default_DT_SR_choice[@]}" ; do echo "			$((var+1)) : ${Default_DT_SR_choice[$var]}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##                 Go into advanced configuration ?                  ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "#######################################################################"
echo -n "                                  "
read choice_DT_SR
while [[ ! ${choice_DT_SR} =~ ^[1-$((var+1))]$ ]] && [[ "$choice_DT_SR" != "" ]] ; do
	echo -n "Select option 1 to $((var+1)) or ENTER to bypass this configuration:"
	read choice_DT_SR
done
if [[ -z "$choice_DT_SR" || $choice_DT_SR = "2" ]] ; then 
	echo "                    your choice is : Don't mess with it, sorry ;)."  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
else 
	DT_SR_Choice=${Default_DT_SR_choice[$choice_DT_SR-1]}
echo -e "                    your choice is :${GREEN} $DT_SR_Choice ${NOCOLOR}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
fi

if [ "$DT_SR_Choice" == "YES" ] ; then
	echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO CONTINUE "
	read
	clear
	echo ""
	echo "#######################################################################"
	echo "##                                                                   ##"
	echo "##                      ADVANCED CONFIGURATION       1/3             ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "##                                                                   ##"
	echo "##            Tinker only if you know what you are doing             ##"
	echo "##                 or if you have problems launching                 ##"
	echo "##                  some cores like nes or pcengine                  ##"
	echo "##                          (Black Screen)                           ##"
	echo "##                                                                   ##"
	echo "##              ==     minimum dotclock selector     ==              ##"
	echo "##                                                                   ##"
	echo "##         If you don't know about it or if you want to let          ##"
	echo "##        batocera configure automatically your dotclock_min         ##"
	echo "##                            press ENTER                            ##"
	echo "##                                                                   ##"
	echo "#######################################################################"
	echo ""
	declare -a dcm_selector=( "Low - 0" "Mild - 6" "Medium - 12" "High - 25" "CUSTOM")
	for var in "${!dcm_selector[@]}" ; do echo "			$((var+1)) : ${dcm_selector[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
	echo ""
	echo "#######################################################################" 
	echo "##               Make your choice for minimum dotclock               ##"
	echo "#######################################################################"
	echo -n "                                  "
	read dcm
	while [[ ! ${dcm} =~ ^[1-$((var+1))]$ ]] && [[ "$dcm" != "" ]] ; do
		echo -n "Select option 1 to $((var+1)) or ENTER to bypass this configuration:"
		read dcm
	done
	if [ -z "$dcm" ] ; then 
		echo -e "                    your choice is :${GREEN} Batocera default minimum dotclock${NOCOLOR}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	else 
		echo -e "                    your choice is :${GREEN}  ${dcm_selector[$dcm-1]}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		case $dcm in
			1) 	dotclock_min=0;;
			2) 	dotclock_min=6;;
			3) 	dotclock_min=12;;
			4) 	dotclock_min=25;;
			5) 	echo "#######################################################################"
				echo "##       Select your custom main dotclock_min: between 0 to 25       ##"
				echo "#######################################################################"
				echo -n "                                  "
				read dotclock_min
				while [[ ! $dotclock_min =~ ^[0-9]+$ || "$dotclock_min" -lt 0 || "$dotclock_min" -gt 25 ]]; do
					echo -n "Enter number between 0 and 25 for dotclock_min: "
					read dotclock_min
				done
				echo -e "                    CUSTOM dotclock_min value = ${GREEN}${dotclock_min}${NOCOLOR}"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
			;;
		esac
	fi
	# Check if it was chosen to configurate a particular monitor for M.A.M.E.
	if [ "$monitor_MAME_CHOICE" = "YES" ] ; then
		echo ""
		echo "#######################################################################"
		echo "##                                                                   ##"
		echo "##                      ADVANCED CONFIGURATION       1b/3            ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		echo "##                                                                   ##"
		echo "##                         M.A.M.E. MONITOR                          ##"
		echo "##            Tinker only if you know what you are doing             ##"
		echo "##                 or if you have problems launching                 ##"
		echo "##                           M.A.M.E.                                ##"
		echo "##                        (Black Screen)                             ##"
		echo "##                                                                   ##"
		echo "##         ==     M.A.M.E. minimum dotclock selector     ==          ##"
		echo "##                                                                   ##"
		echo "##         If you don't know about it or if you want to let          ##"
		echo "##                 same dotclock_min as main monitor                 ##"
		echo "##                            press ENTER                            ##"
		echo "##                                                                   ##"
		echo "#######################################################################" 
		echo ""
		declare -a dcm_m_selector=( "Low - 0" "Mild - 6" "Medium - 12" "High - 25" "CUSTOM")
		for var in "${!dcm_m_selector[@]}" ; do echo "			$((var+1)) : ${dcm_m_selector[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
		echo""
		echo "#######################################################################" 
		echo "##            Make your choice for MAME minimum dotclock             ##"
		echo "#######################################################################"
		echo -n "                                  "
		read dcm_m
		while [[ ! ${dcm_m} =~ ^[1-$((var+1))]$ ]] && [[ "$dcm_m" != "" ]] ; do
			echo -n "Select option 1 to $((var+1)) or ENTER to bypass this configuration:"
			read dcm_m
		done
		if [ -z "$dcm_m" ] ; then 
			echo -e "                    your choice is :${GREEN} Same as main monitor ($dotclock_min)${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
			dotclock_min_mame=$dotclock_min
		else
			echo -e "                    your choice is :${GREEN}  ${dcm_selector[$dcm_m-1]}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
			case $dcm_m in
				1)	dotclock_min_mame=0;;
				2)	dotclock_min_mame=6;;
				3)	dotclock_min_mame=12;;
				4)	dotclock_min_mame=25;;
				5) 	echo "#######################################################################"
					echo "##       Select your MAME custom dotclock_min: between 0 to 25       ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
					echo "#######################################################################"
					echo -n "                                  "
					read dotclock_min_mame
					while [[ ! $dotclock_min_mame =~ ^[0-9]+$ || "$dotclock_min_mame" -lt 0 || "$dotclock_min_mame" -gt 25 ]] ; do
						echo -n "Enter number between 0 and 25 for dotclock_min_mame: "
						read dotclock_min_mame
					done
					echo -e "                    CUSTOM dotclock_min_mame value = ${GREEN}${dotclock_min_mame}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
					;;
			esac
		fi
	fi
	#########################################################################
	##                    super-resolution CONFIG                          ##
	#########################################################################
	echo ""
	echo "#######################################################################"
	echo "##                                                                   ##"
	echo "##                      ADVANCED CONFIGURATION       2/3             ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "##                                                                   ##"
	echo "##                  ==     Super-resolution     ==                   ##"
	echo "##                                                                   ##"
	echo "##        This option sets the value for vertical resolution         ##"
	echo "##             You can set a default maker tested value              ##"
	echo "##        or you can test your own custom one (experimental)         ##"
	echo "##                                                                   ##"
	echo "##                  If you don't know about it or                    ##"
	echo "##                 if you want to let the script                     ##"
	echo "##        set default super-resolution for your graphics card        ##"
	echo "##                            press ENTER                            ##"
	echo "##                                                                   ##"
	echo "#######################################################################"
	echo ""
	declare -a sr_selector=( "1920 - Intel default" "2560 - amd/ati default" "3840 - nvidia default" "CUSTOM (experimental)")
	for var in "${!sr_selector[@]}" ; do echo "			$((var+1)) : ${sr_selector[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
	echo ""
	echo "#######################################################################"
	echo "##             Make your choice for super-resolution                 ##"
	echo "#######################################################################"
	echo -n "                                  "
	read sr_choice
	while [[ ! ${sr_choice} =~ ^[1-$((var+1))]$ ]] && [[ "$sr_choice" != "" ]] ; do
		echo -n "Select option 1 to $((var+1)) or ENTER to bypass this configuration:"
		read sr_choice
	done
	if [ -z "$sr_choice" ] ; then 
		echo -e "                    your choice is :${GREEN} default super-resolution${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	else
		echo -e "                    your choice is :${GREEN}  ${sr_selector[$sr_choice-1]}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		case $sr_choice in
			1)	super_width=1920;;
			2)	super_width=2560;;
			3)	super_width=3840;;
			4)	echo "#######################################################################"
				echo "##                Select your custom super_resolution                ##"
				echo "#######################################################################"
				echo -n "                                  "
				read super_width
				while [[ ! $super_width =~ ^[0-9]+$ || "$super_width" -lt 0 ]] ; do
					echo -n "Enter valid number greater than 0 for custom super-resolution:"
					read super_width
				done
				echo -e "                    CUSTOM super-resolution value = ${GREEN}${super_width}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
				;;
		esac
	fi
	if [ "$monitor_MAME_CHOICE" = "YES" ] ; then
		echo ""
		echo "#######################################################################"
		echo "##                                                                   ##"
		echo "##                      ADVANCED CONFIGURATION       2b/3            ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		echo "##                                                                   ##"
		echo "##                ==     MAME Super-resolution     ==                ##"
		echo "##                                                                   ##"
		echo "##        This option sets the value for vertical resolution         ##"
		echo "##             You can set a default maker tested value              ##"
		echo "##        or you can test your own custom one (experimental)         ##"
		echo "##                                                                   ##"
		echo "##                 If you don't know about it or                     ##"
		echo "##                 if you want to let the script                     ##"
		echo "##     set default MAME super-resolution for your graphics card      ##"
		echo "##                            press ENTER                            ##"
		echo "##                                                                   ##"
		echo "#######################################################################"
		echo ""
		declare -a sr_m_selector=( "1920 - Intel default" "2560 - amd/ati default" "3840 - nvidia default" "Same as main monitor" "CUSTOM (experimental)")
		for var in "${!sr_m_selector[@]}" ; do echo "			$((var+1)) : ${sr_m_selector[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
		echo ""
		echo "#######################################################################"
		echo "##          Make your choice for MAME super-resolution               ##"
		echo "#######################################################################"
		echo -n "                                  "
		read sr_m_choice
		while [[ ! ${sr_m_choice} =~ ^[1-$((var+1))]$ ]] && [[ "$sr_m_choice" != "" ]] ; do
			echo -n "Select option 1 to $((var+1)) or ENTER to bypass this configuration:"
			read sr_m_choice
		done
		if [ -z "$sr_m_choice" ] ; then 
			echo -e "                    your choice is :${GREEN} MAME default super-resolution${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
		else
			echo -e "                    your choice is :${GREEN}  ${sr_m_selector[$sr_m_choice-1]}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
			case $sr_m_choice in
				1)	super_width_mame=1920;;
				2)	super_width_mame=2560;;
				3)	super_width_mame=3840;;
				4)	super_width_mame=$super_width;;
				5)	echo "#######################################################################"
					echo "##             Select your custom MAME super_resolution              ##"
					echo "#######################################################################"
					echo -n "                                  "
					read super_width_mame
					while [[ ! $super_width_mame =~ ^[0-9]+$ || "$super_width_mame" -lt 0 ]] ; do
						echo -n "Enter valid number greater than 0 for custom super-resolution"
						read super_width_mame
					done
					echo -e "                    CUSTOM MAME super-resolution value = ${GREEN}${super_width_mame}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
					;;
			esac
		fi
	fi
fi
#######################################################################
###                 Start of usb polling rate config               ####
#######################################################################
echo ""
echo "#######################################################################"
echo "##                                                                   ##"
echo "##                      ADVANCED CONFIGURATION       3/3             ##" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "##                                                                   ##"
echo "##            Tinker only if you know what you are doing.            ##"
echo "##              This configuration can reduce input lag              ##"
echo "##                                                                   ##"
echo "##                        USB FAST POLLING                           ##"
echo "##                                                                   ##"
echo "##         If you don't know about it or if you want to let          ##"
echo "##      batocera configure automatically your USB POLLING RATE       ##"
echo "##                           press ENTER                             ##"
echo "##                                                                   ##"
echo "#######################################################################" 
echo ""
declare -a usb_selector=( "Activate(reduce input lag)" "Keep default" )
for var in "${!usb_selector[@]}" ; do echo "			$((var+1)) : ${usb_selector[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################" 
echo "##               Make your choice for USB POLLING RATE               ##"
echo "#######################################################################"
echo -n "                                  "
read p_rate
	while [[ ! ${p_rate} =~ ^[1-$((var+1))]$ ]] && [[ "$p_rate" != "" ]] ; do
		echo -n "Select option 1 to $((var+1)) or ENTER to bypass this configuration:"
		read p_rate
	done
if [ -z "$p_rate" ] ; then 
	echo -e "                    your choice is :${GREEN} Batocera default usb polling rate${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	polling_rate="usbhid.jspoll=0 xpad.cpoll=0"
elif [ "x$p_rate" != "x0" ] ; then
	echo -e "                    your choice is :${GREEN}  ${usb_selector[$p_rate-1]}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	case $p_rate in
		1) polling_rate="usbhid.jspoll=1 xpad.cpoll=1";;
		*) polling_rate="usbhid.jspoll=0 xpad.cpoll=0";;
	esac
fi

#############################################################################
## Make the boot writable
#############################################################################
echo "mount -o remount, rw /boot" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
mount -o remount, rw /boot

#############################################################################
# first time using the script save the batocera-boot.conf batocera-boot.conf.bak
#############################################################################

if [ ! -f "/boot/batocera-boot.conf.bak" ];then
	cp /boot/batocera-boot.conf /boot/batocera-boot.conf.bak
fi

cp /boot/batocera-boot.conf  /boot/batocera-boot.conf.tmp

#############################################################################
# choose #nvidia-driver (NOUVEAU) or nvidia-driver=true (nvidia driver)
#############################################################################
if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
	if   [ "$Drivers_Name_Nvidia_CHOICE" == "true" ]; then
		sed -e 's/.*nvidia-driver=.*/nvidia-driver=true/' -e 's/.*amdgpu=.*/#amdgpu=true/' -e 's/.*splash.screen.enabled=.*/splash.screen.enabled=0/'	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
	elif [ "$Drivers_Name_Nvidia_CHOICE" == "legacy" ]; then
		sed -e 's/.*nvidia-driver=.*/nvidia-driver=legacy/'  -e 's/.*amdgpu=.*/#amdgpu=true/' -e 's/.*splash.screen.enabled=.*/splash.screen.enabled=0/'	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
	elif [ "$Drivers_Name_Nvidia_CHOICE" == "legacy390" ]; then
		sed -e 's/.*nvidia-driver=.*/nvidia-driver=legacy390/' -e 's/.*amdgpu=.*/#amdgpu=true/' -e 's/.*splash.screen.enabled=.*/splash.screen.enabled=0/'	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
        elif [ "$Drivers_Name_Nvidia_CHOICE" == "legacy340" ]; then
		sed -e 's/.*nvidia-driver=.*/nvidia-driver=legacy340/' -e 's/.*amdgpu=.*/#amdgpu=true/' -e 's/.*splash.screen.enabled=.*/splash.screen.enabled=0/'	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
	else
		echo "problems of Nvidia driver name"
	fi	
else
	if [ "$Drivers_Nvidia_CHOICE" == "NOUVEAU" ]&&([ "$Version_of_batocera" == "v36" ]||[ "$Version_of_batocera" == "v37" ]||[ "$Version_of_batocera" == "v38" ]||[ "$Version_of_batocera" == "v39" ]); then
		sed -e 's/.*nvidia-driver=.*/nvidia-driver=false/' -e 's/.*amdgpu=.*/#amdgpu=true/' -e  's/.*splash.screen.enabled=.*/#splash.screen.enabled=0/'	 	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
	else
		if [ "$TYPE_OF_CARD" == "AMD/ATI" ]&&([ "$Version_of_batocera" == "v37" ]||[ "$Version_of_batocera" == "v38" ]||[ "$Version_of_batocera" == "v39" ]); then
			if [ "$drivers_type" == "AMDGPU" ]; then
				sed -e 's/.*nvidia-driver=.*/#nvidia-driver=true/' -e 's/.*amdgpu=.*/amdgpu=true/' -e 's/.*splash.screen.enabled=.*/#splash.screen.enabled=0/'	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
			else
				sed -e 's/.*nvidia-driver=.*/#nvidia-driver=true/' -e 's/.*amdgpu=.*/amdgpu=false/' -e 's/.*splash.screen.enabled=.*/#splash.screen.enabled=0/'	/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
			fi
		else
			sed -e 's/.*nvidia-driver=.*/#nvidia-driver=true/' -e 's/.*amdgpu=.*/#amdgpu=true/' -e 's/.*splash.screen.enabled=.*/#splash.screen.enabled=0/'		/boot/batocera-boot.conf > /boot/batocera-boot.conf.tmp
		fi
	fi
fi



cp /boot/batocera-boot.conf.tmp  /boot/batocera-boot.conf
rm /boot/batocera-boot.conf.tmp 

chmod 755 /boot/batocera-boot.conf

#############################################################################
## Copy of the right syslinux for your write device
#############################################################################
# first time using the script save the syslinux.cfg in syslinux.cfg

if [ ! -f "/boot/EFI/syslinux.cfg.bak" ];then
	cp /boot/EFI/syslinux.cfg /boot/EFI/syslinux.cfg.bak
fi

###  Condition to be reviewed

sed -e "s/\[amdgpu_drivers\]/$drivers_amd/g" -e "s/\[card_output\]/$video_output/g" \
	-e "s/\[monitor\]/$monitor_firmware.bin/g" -e "s/\[card_display\]/$video_display/g" \
	-e "s/\[usb_polling\]/$polling_rate/g" \
	-e "s/\[boot_resolution\]/$boot_resolution/g"  /userdata/system/BUILD_15KHz/Boot_configs/syslinux.cfg-generic-Batocera \
	>  /boot/EFI/syslinux.cfg

chmod 755 /boot/EFI/syslinux.cfg

#############################################################################
## Copy syslinux for EFI and legacy boot
#############################################################################

cp /boot/EFI/syslinux.cfg /boot/EFI/BOOT/
cp /boot/EFI/syslinux.cfg /boot/boot/
cp /boot/EFI/syslinux.cfg /boot/boot/syslinux/

#######################################################################################

if [[ "$video_output" == *"DP"* ]]; then
	cp /userdata/system/BUILD_15KHz/etc_configs/Monitors_config/10-monitor.conf-DP /etc/X11/xorg.conf.d/10-monitor.conf
	chmod 644 /etc/X11/xorg.conf.d/10-monitor.conf
elif [[ "$video_output" == *"DVI"* ]]||[[ "$video_output" == *"VGA"* ]]||[[ "$video_output" == *"HDMI"* ]]; then
	cp /userdata/system/BUILD_15KHz/etc_configs/Monitors_config/10-monitor.conf-DVI /etc/X11/xorg.conf.d/10-monitor.conf
	chmod 644 /etc/X11/xorg.conf.d/10-monitor.conf
else
	echo "####################################################"
	echo "###   UNDER CONSTRUCTION                         ###"
	echo "####################################################"
	exit 1
fi

# first time using the script save the 20-amdgpu.conf  in 20-amdgpu.conf.bak
if [ ! -f "/etc/X11/xorg.conf.d/20-amdgpu.conf.bak" ];then
	cp /etc/X11/xorg.conf.d/20-amdgpu.conf /etc/X11/xorg.conf.d/20-amdgpu.conf.bak
fi

cp /userdata/system/BUILD_15KHz//etc_configs/Monitors_config/20-amdgpu.conf /etc/X11/xorg.conf.d/20-amdgpu.conf
chmod 644 /etc/X11/xorg.conf.d/20-amdgpu.conf  

# first time using the script save the 20-radeon.conf  in 20-radeon.conf.bak
if [ ! -f "/etc/X11/xorg.conf.d/20-radeon.conf.bak" ];then
	cp /etc/X11/xorg.conf.d/20-radeon.conf /etc/X11/xorg.conf.d/20-radeon.conf.bak
fi 

cp /userdata/system/BUILD_15KHz/etc_configs/Monitors_config/20-radeon.conf /etc/X11/xorg.conf.d/20-radeon.conf
chmod 644 /etc/X11/xorg.conf.d/20-radeon.conf

#######################################################################################
## Put EDID (Extended Display Identification Data) metadata formats for display devices 
#######################################################################################

cp -rf /userdata/system/BUILD_15KHz/Firmware_configs/edid /lib/firmware/

#######################################################################################
## Batocera-resolution and EmulationStation-standalone
## Disable EmulationStation from forcing 60 Hz in Emulationstation-standalone
#######################################################################################
# first time using the script save the batocera-resolution in batocera-resolution.bak
if [ ! -f "/usr/bin/batocera-resolution.bak" ];then
	cp /usr/bin/batocera-resolution /usr/bin/batocera-resolution.bak
fi 

if [ ! -f "/usr/bin/emulationstation-standalone.bak" ];then
	cp /usr/bin/emulationstation-standalone /usr/bin/emulationstation-standalone.bak
fi

if [ ! -f "/usr/bin/retroarch.bak" ];then
	cp /usr/bin/retroarch /usr/bin/retroarch.bak
fi 

## Only for Batocera >= V32
case $Version_of_batocera in
	v32)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v32 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v32 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
#		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
#		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
#		cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v32 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
#		sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v32 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v32 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
	;;
	v33)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v33 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution 
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v33 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone	
#		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
#		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
#		cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v33 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
#		sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g"  -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v33 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v33 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
	;;
	v34)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v34 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v34 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
#		cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v34 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
#		sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g"  -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v34 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v34 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
	;;
	v35)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v35 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v35 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
#		cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v35 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
#		sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g"  -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v35 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v35 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
		if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then
			# comaeback to v35 version
			cp /userdata/system/BUILD_15KHz/UsrBin_configs/Nvidia/batocera-nvidia-v35 /usr/bin/batocera-nvidia
			chmod 755 /usr/bin/batocera-nvidia
			cp /userdata/system/BUILD_15KHz/etc_configs/Nvidia/S05nvidia-v35  /etc/init.d/S05nvidia
			chmod 755 /etc/init.d/S05nvidia
		else
			# correction from V36 (dmanlfc)
			cp /userdata/system/BUILD_15KHz/UsrBin_configs/Nvidia/batocera-nvidia.patch /usr/bin/batocera-nvidia
			chmod 755 /usr/bin/batocera-nvidia
			cp /userdata/system/BUILD_15KHz/etc_configs/Nvidia/S05nvidia.patch  /etc/init.d/S05nvidia
			chmod 755 /etc/init.d/S05nvidia
		fi
		#for JammaSD from V37
		cp /userdata/system/BUILD_15KHz/etc_configs/98-keyboards-exotics.rules  /etc/udev/rules.d/98-keyboards-exotics.rules  
		chmod 644  /etc/udev/rules.d/98-keyboards-exotics.rules 
		cp /userdata/system/BUILD_15KHz/etc_configs/99-jammasd.rules  /etc/udev/rules.d/99-jammasd.rules  
		chmod 644  /etc/udev/rules.d/98-keyboards-exotics.rules 
		cp /userdata/system/BUILD_15KHz/etc_configs/99-joysticks-exotics.rules  /etc/udev/rules.d/99-joysticks-exotics.rules  
		chmod 644  /etc/udev/rules.d/99-joysticks-exotics.rules  	
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/jammASDSplit /usr/bin/jammASDSplit 
		chmod 755 /usr/bin/jammASDSplit 
	;;
	v36)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v36 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution 
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v36 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
		#cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v36 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
		#sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
		if [ ! -f "/etc/init.d/S31emulationstation.bak" ];then
			cp /etc/init.d/S31emulationstation  /etc/init.d/S31emulationstation.bak
		fi
		cp /userdata/system/BUILD_15KHz/etc_configs/S31emulationstation-generic /etc/init.d/S31emulationstation 
		chmod 755 /etc/init.d/S31emulationstation 
		
		#for JammaSD from V37
		cp /userdata/system/BUILD_15KHz/etc_configs/98-keyboards-exotics.rules  /etc/udev/rules.d/98-keyboards-exotics.rules  
		chmod 644  /etc/udev/rules.d/98-keyboards-exotics.rules 
		cp /userdata/system/BUILD_15KHz/etc_configs/99-jammasd.rules  /etc/udev/rules.d/99-jammasd.rules  
		chmod 644  /etc/udev/rules.d/98-keyboards-exotics.rules 
		cp /userdata/system/BUILD_15KHz/etc_configs/99-joysticks-exotics.rules  /etc/udev/rules.d/99-joysticks-exotics.rules  
		chmod 644  /etc/udev/rules.d/99-joysticks-exotics.rules  	
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/jammASDSplit /usr/bin/jammASDSplit 
		chmod 755 /usr/bin/jammASDSplit 
	;;
	v37)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v36 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution 
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v36 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
#		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
#		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
		#cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v36 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
		#sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
	;;
 	v38)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v36 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution 
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v36 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
#		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
#		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
		#cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v36 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
		#sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
	;;
 	v39)
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/batocera-resolution-v36 /usr/bin/batocera-resolution
		chmod 755 /usr/bin/batocera-resolution 
		cp /userdata/system/BUILD_15KHz/UsrBin_configs/emulationstation-standalone-v36 /usr/bin/emulationstation-standalone
		chmod 755 /usr/bin/emulationstation-standalone
#		cp /userdata/system/BUILD_15KHz/UsrBin_configs/retroarch-generic /usr/bin/retroarch
#		chmod 755 /usr/bin/retroarch
		###############################################################################################################################################
		#cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v36 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py
		###############################################################################################################################################
		#sed -e "s/\[monitor-name\]/$monitor_name/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width\]/$super_width/g" -e "s/\[dotclock_min_value\]/$dotclock_min/g"  /userdata/system/BUILD_15KHz/etc_configs/switchres.ini-generic-v36 > /etc/switchres.ini
		chmod 755 /etc/switchres.ini
	;;
	*)
		echo "PROBLEM OF VERSION"
		exit 1;
	;;
esac

cp /etc/switchres.ini /etc/switchres.ini.bak

#######################################################################################
## Remove Beta name from splash screen if using a beta.
#######################################################################################
if [ -f "/usr/share/batocera/splash/splash.srt" ];then
	mv /usr/share/batocera/splash/splash.srt /usr/share/batocera/splash/splash.srt.bak
fi
#######################################################################################
## make splash screen rotation if using tate mode (right or left).
#######################################################################################
if [ ! -f "/usr/share/batocera/splash/boot-logo.png.bak" ]; then
	cp /usr/share/batocera/splash/boot-logo.png /usr/share/batocera/splash/boot-logo.png.bak
fi
cp /userdata/system/BUILD_15KHz/Boot_logos/boot-logo.png /usr/share/batocera/splash/boot-logo.png 
if [ "$display_rotate" == "right" ];then

	cp /userdata/system/BUILD_15KHz/Boot_logos/boot-logo_90.png /usr/share/batocera/splash/boot-logo.png 
fi
if [ "$display_rotate" == "inverted" ];then

	cp /userdata/system/BUILD_15KHz/Boot_logos/boot-logo_180.png /usr/share/batocera/splash/boot-logo.png 
fi
if  [ "$display_rotate" == "left" ]; then
	cp /userdata/system/BUILD_15KHz/Boot_logos/boot-logo_270.png /usr/share/batocera/splash/boot-logo.png  
fi
#######################################################################################
#######################################################################################
##         USB Arcade Encoders (multiple choices) for Arcade cabinet 
#######################################################################################
#######################################################################################

echo ""
echo "#######################################################################"
echo "##     USB Arcade Encoder(s) :  Multiple choices are possible        ##"
echo "#######################################################################"
declare -a Encoder_inputs=\($(ls -1 /dev/input/by-id/| tr "\012" " "| sed -e's, ," ",g' -e 's,^,",' -e 's," "$,",')\)
for var in "${!Encoder_inputs[@]}" ; do echo "			$((var+1)) : ${Encoder_inputs[$var]}"; done
echo "                        0 : Exit for USB Arcade Encoder(s)                   "
echo "#######################################################################"  
echo "##                                                                   ##"
echo "##            Make your choice(s) for one two or more                ##"
echo "##  for several encoders put virgule or space between your choices   ##"
echo "##                                                                   ##"
echo "##  If you don't have an Arcade Encoder(s) or if you want to let     ##"
echo "##       batocera configure automatically your Arcade Encoder(s)     ##"
echo "##                                                                   ##"	
echo "##               IT IS RECOMMANDED TO PRESS 0 OR ENTER               ##"
echo "##                                                                   ##"
echo "#######################################################################"
echo -n "                                  "
read Encoder_choice

if [ "x$Encoder_choice" != "x0" ] ; then
var_choix="`echo $Encoder_choice | sed -e 's/,/ /g'`"
for i in $var_choix; do echo -e "                    your choice is : ${Encoder_inputs[$i-1]}" ; touch /usr/share/batocera/datainit/system/configs/xarcade2jstick/${Encoder_inputs[$((i-1))]};done
else 
	echo "No USB Arcade encoder(s) has been choosen"
fi

#######################################################################################
# Select the calibration resolution for your CRT   via Geometry / Switchres
#######################################################################################

echo "#######################################################################"
echo "##    Configure a specific resolution for your geometry calibation   ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "##    if you choose no the default resolution will be 640x480@60Hz   ##" 
echo "#######################################################################"
echo ""
declare -a Calibration_Geometry_choice=( "YES" "NO" ) 
for var in "${!Calibration_Geometry_choice[@]}" ; do echo "			$((var+1)) : ${Calibration_Geometry_choice[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##                         Make your choice                          ##"
echo "#######################################################################"
echo -n "                                  "
read choice_Calibration_geometry
while [[ ! ${choice_Calibration_geometry} =~ ^[1-$((var+1))]$ ]] ; do
	echo -n "Select option 1 to $((var+1)):"
	read choice_Calibration_geometry
done
if [  "$choice_Calibration_geometry" == "2" ] ; then 
	echo -e "                    your choice is :${GREEN} Bypass this configuration${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	Resolution_Geometry="640x480 60"
	Resolution_Avoid=$(echo $Resolution_Geometry | cut -d' ' -f1)
else
	echo "#######################################################################"
	echo "##      Select your custom horizontal resolution for calibration     ##"
	echo "#######################################################################"
	echo -n "                                  "
	read  horizontal_calibration_resolution
	while [[ ! $horizontal_calibration_resolution =~ ^[0-9]+$ || "$horizontal_calibration_resolution" -lt 0 ]] ; do
		echo -n "Enter valid number greater than 0 for horizontal_calibration_resolution"
		read horizontal_calibration_resolution
	done
	echo
 	echo -e "                    CUSTOM horizontal_calibration_resolution  = ${GREEN}${horizontal_calibration_resolution}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "#######################################################################"
	echo "##      Select your custom vertical resolution for calibration      ##"
	echo "#######################################################################"
	echo -n "                                  "
	read  vertical_calibration_resolution
	while [[ ! $vertical_calibration_resolution =~ ^[0-9]+$ || "$vertical_calibration_resolution" -lt 0 ]] ; do
		echo -n "Enter valid number greater than 0 for vertical_calibration_resolution"
		read vertical_calibration_resolution
	done
	echo
 	echo -e "                    CUSTOM vertical_calibration_resolutione = ${GREEN}${vertical_calibration_resolution}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log

	echo "#######################################################################"
	echo "##      Select your custom frequency for calibration                 ##"
	echo "#######################################################################"
	echo -n "                                  "
	read  calibration_frequency 
	while [[ ! $calibration_frequency =~ ^[0-9]+$ || "$calibration_frequency" -lt 0 ]] ; do
		echo -n "Enter valid number greater than 0 for calibration_frequency "
		read calibration_frequency 
	done
 	echo -e "                    CUSTOM calibration_frequency  = ${GREEN}${calibration_frequency}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log

	Resolution=($horizontal_calibration_resolution"x"$vertical_calibration_resolution" "$calibration_frequency)
	Resolution_Geometry="$Resolution"
	Resolution_Avoid=$(echo $Resolution_Geometry | cut -d' ' -f1)
fi

#######################################################################################
# Select the calibration resolution for your GunCon II
# #######################################################################################

echo "####################################################################################"
echo "##         Configure a specific resolution the calibration of your GunCon2        ##"  | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
echo "##                                                                                ##"
echo "##                YES for Nvidia with Dotclok_min=25.0 (try 640x480@60Hz)         ##"
echo "##                NO  AMD/ATI or Nvidia(Maxwell) Default is (320x240@60Hz)        ##"
echo "##                                                                                ##"
echo "##  EXPERIMENTAL : FOR AMD/ATI/NVIDIA YOU CAN USE OWN RESOLUTION AND SEE WHAT     ##"
echo "##  IS BETTER AND REPORT US YOUR EXPERIENCE IN GAMES. YOU CAN TRY 640x480@60Hz    ##"
echo "##  OR WHAT YOU WANT LIKE 768X576@50Hz. FOR THAT TYPE YES                         ##"
echo "##                                                                                ##"
echo "####################################################################################"
echo ""
declare -a Calibration_Guncon2_choice=( "YES" "NO" )
for var in "${!Calibration_Guncon2_choice[@]}" ; do echo "			$((var+1)) : ${Calibration_Guncon2_choice[$var]}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log; done
echo ""
echo "#######################################################################"
echo "##                         Make your choice                          ##"
echo "#######################################################################"
echo -n "                                  "
read choice_Calibration_Guncon2
while [[ ! ${choice_Calibration_Guncon2} =~ ^[1-$((var+1))]$ ]] ; do
	echo -n "Select option 1 to $((var+1)):"
	read choice_Calibration_Guncon2
done
if [  "$choice_Calibration_Guncon2" == "2" ] ; then
	echo -e "                    your choice is :${GREEN} Bypass with 320x240@60Hz${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	Guncon2_x=320
	Guncon2_y=240
	Guncon2_freq=60
	Guncon2_res=($Guncon2_x"x"$Guncon2_y)
	
	Resolution_Avoid=$(echo $Resolution_Geometry | cut -d' ' -f1)
else
	echo "###############################################################################"
	echo "##      Select your custom horizontal resolution for Guncon2 calibration     ##"
	echo "###############################################################################"
	echo -n "                                  "
	read  Guncon2_x
	while [[ ! $Guncon2_x =~ ^[0-9]+$ || "$Guncon2_x" -lt 0 ]] ; do
		echo -n "Enter valid number greater than 0 for Guncon2_x"
		read Guncon2_x
	done
	echo
 	echo -e "                    CUSTOM Guncon2_x Horizontal resolution  = ${GREEN}${Guncon2_x}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log
	echo "###############################################################################"
	echo "##      Select your custom vertical resolution for Guncon2 calibration       ##"
	echo "###############################################################################"

	echo -n "                                  "
	read  Guncon2_y
	while [[ ! $Guncon2_y =~ ^[0-9]+$ || "$Guncon2_y" -lt 0 ]] ; do
		echo -n "Enter valid number greater than 0 for Guncon2_y"
		read Guncon2_y
	done
	echo
 	echo -e "                    CUSTOM Guncon2_y Horizontal resolution  = ${GREEN}${Guncon2_y}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log

	echo "###############################################################################"
	echo "##      Select your custom frequency resolution for Guncon2 calibration      ##"
	echo "###############################################################################"

	echo -n "                                  "
	read  Guncon2_freq
	while [[ ! $Guncon2_freq =~ ^[0-9]+$ || "Guncon2_freq" -lt 0 ]] ; do
		echo -n "Enter valid number greater than 0 for calibration_frequency "
		read Guncon2_freq
	done
 	echo -e "                    CUSTOM frequency resolution  = ${GREEN}${calibration_frequency}${NOCOLOR}" | tee -a /userdata/system/logs/BUILD_15KHz_Batocera.log

	Guncon2_res=($Guncon2_x"x"$Guncon2_y)

fi


echo ""
echo "#######################################################################"
echo "##                                                                   ##"
echo "##             BEFORE YOU PRESS ENTER READ THE FOLLOWING TEXT        ##"   
echo "##                                                                   ##"
echo "##      REMEMBER AUTHORS OF THIS SCRIPT WILL BE NOT RESPONSIBLE      ##"
echo "##                      FOR ANY DAMAGES TO YOUR CRT                  ##"
echo "##                                                                   ##"
echo "##                     DO A SHUTDOWN OF YOUR SYSTEM                  ##"
echo "##         BE SURE YOU PUT THE RIGHT CABLE AND CONNECTION FOR 15KHz  ##"
echo "##       BE SURE YOU HAVE SOME PROTECTIONS FOR YOUR MONITOR          ##"
echo "##                                                                   ##"
echo "##    RESTART YOUR BATOCERA SYSTEM AND HAVE FUN IN 15KHz EXPERIENCE  ##"
echo "##                                                                   ##"
echo "#######################################################################"
echo ""
echo -n -e "                       PRESS ${BLUE}ENTER${NOCOLOR} TO FINISH "
read 

#######################################################################################
# Create CRT.sh for adjusting modeline for your CRT   via Geometry / Switchres
#######################################################################################
echo "Create CRT.sh for adjusting modeline for your CRT   via Geometry / Switchres" >> /userdata/system/logs/BUILD_15KHz_Batocera.log
cp -a /userdata/system/BUILD_15KHz/Geometry_modeline/crt/ /userdata/roms/
sed -e "s/\[Resolution_calibration\]/$Resolution_Geometry/g" -e "s/\[card_display\]/$video_modeline/g" -e "s/\[Resolution_avoid\]/$Resolution_Avoid/g" /userdata/system/BUILD_15KHz/Geometry_modeline/crt/CRT.sh > /userdata/roms/crt/CRT.sh
cp /userdata/system/BUILD_15KHz/Geometry_modeline/es_systems_crt.cfg /userdata/system/configs/emulationstation/es_systems_crt.cfg
cp /userdata/system/BUILD_15KHz/Geometry_modeline/CRT.png /usr/share/emulationstation/themes/es-theme-carbon/art/consoles/CRT.png
cp /userdata/system/BUILD_15KHz/Geometry_modeline/CRT.svg /usr/share/emulationstation/themes/es-theme-carbon/art/logos/CRT.svg
cp /userdata/system/BUILD_15KHz/Geometry_modeline/CRT.sh.keys /usr/share/evmapy/
chmod 755 /userdata/roms/crt/CRT.sh
chmod 755 /usr/share/evmapy/CRT.sh.keys


#######################################################################################
# Create GunCon2 LUA plugin for GroovyMame for V36, V37 and V38
#######################################################################################
## if the folder doesn't exist, it will be created now
if [ ! -d "/usr/bin/mame/plugins/gunlight" ];then
	mkdir /usr/bin/mame/plugins/gunlight
fi
if [ "$Version_of_batocera" == "v36" ]||[ "$Version_of_batocera" == "v37" ]||[ "$Version_of_batocera" == "v38" ]||[ "$Version_of_batocera" == "v39" ]; then
	cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/gunlight_menu.lua /usr/bin/mame/plugins/gunlight/gunlight_menu.lua
	cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/gunlight_save.lua /usr/bin/mame/plugins/gunlight/gunlight_save.lua
	cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/init.lua /usr/bin/mame/plugins/gunlight/init.lua
	cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/plugin.json /usr/bin/mame/plugins/gunlight/plugin.json
	chmod 644 /usr/bin/mame/plugins/gunlight/gunlight_menu.lua
	chmod 644 /usr/bin/mame/plugins/gunlight/gunlight_save.lua
	chmod 644 /usr/bin/mame/plugins/gunlight/init.lua
	chmod 644 /usr/bin/mame/plugins/gunlight/plugin.json
fi

#######################################################################################
# Create GunCon2 shader for V36, V37 and v38
#######################################################################################
## if the folder doesn't exist, it will be created now
if [ ! -d "/usr/share/batocera/shaders/configs/lightgun-shader" ];then
	mkdir /usr/share/batocera/shaders/configs/lightgun-shader
fi
if [ "$Version_of_batocera" == "v36" ]||[ "$Version_of_batocera" == "v37" ]||[ "$Version_of_batocera" == "v38" ]||[ "$Version_of_batocera" == "v39" ]; then
	cp /userdata/system/BUILD_15KHz/GunCon2/shader/lightgun-shader/rendering-defaults.yml /usr/share/batocera/shaders/configs/lightgun-shader/rendering-defaults.yml
	chmod 644 /usr/share/batocera/shaders/configs/lightgun-shader/rendering-defaults.yml
	cp /userdata/system/BUILD_15KHz/GunCon2/shader/misc/image-adjustment_lgun.slangp /usr/share/batocera/shaders/misc/image-adjustment_lgun.slangp
	cp /userdata/system/BUILD_15KHz/GunCon2/shader/misc/shaders/image-adjustment_lgun.slang /usr/share/batocera/shaders/misc/shaders/image-adjustment_lgun.slang
	chmod 644 /usr/share/batocera/shaders/misc/image-adjustment_lgun.slangp
	chmod 644 /usr/share/batocera/shaders/misc/shaders/image-adjustment_lgun.slang
fi

if [ "$Version_of_batocera" == "v36" ]||[ "$Version_of_batocera" == "v37" ]||[ "$Version_of_batocera" == "v38" ]||[ "$Version_of_batocera" == "v39" ]; then

	if [ ! -f "/etc/udev/rules.d/99-guncon.rules.bak" ];then                                                           
		cp /etc/udev/rules.d/99-guncon.rules /etc/udev/rules.d/99-guncon.rules.bak                       
	fi
 
	cp /userdata/system/BUILD_15KHz/GunCon2/99-guncon.rules-generic /etc/udev/rules.d/99-guncon.rules

        if [ ! -f "/usr/bin/guncon2_calibrate.sh.bak" ];then                                                           
		cp /usr/bin/guncon2_calibrate.sh /usr/bin/guncon2_calibrate.sh.bak                      
	fi

	sed -e "s/\[guncon2_x\]/$Guncon2_x/g" -e "s/\[guncon2_y\]/$Guncon2_y/g" -e "s/\[guncon2_f\]/$Guncon2_freq/g" -e "s/\[guncon2_res\]/$Guncon2_res/g" \
		/userdata/system/BUILD_15KHz/GunCon2/guncon2_calibrate.sh-generic  > /usr/bin/guncon2_calibrate.sh
        chmod 755 /usr/bin/guncon2_calibrate.sh


	if [ ! -f "/usr/bin/calibrate.py.bak" ];then                                                           
		cp /usr/bin/calibrate.py /usr/bin/calibrate.py.bak                      
	fi
	if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then	
		sed -e "s/\[guncon2_x\]/$Guncon2_x/g" -e "s/\[guncon2_y\]/$Guncon2_y/g"  -e "s/\[guncon2_res\]/$Guncon2_res/g" \
		       	/userdata/system/BUILD_15KHz/GunCon2/calibrate.py-generic   > /usr/bin/calibrate.py
	else
		sed -e "s/\[guncon2_y\]/$Guncon2_x/g" -e "s/\[guncon2_x\]/$Guncon2_y/g"  -e "s/\[guncon2_res\]/$Guncon2_res/g" \
		       	/userdata/system/BUILD_15KHz/GunCon2/calibrate.py-generic   > /usr/bin/calibrate.py
	fi
	chmod 755 /usr/bin/calibrate.py
fi

#######################################################################################
## Save in compilation in batocera image
#######################################################################################
batocera-save-overlay
#######################################################################################
## Put the custom file for the 15KHz modelines for ES and Games 
#######################################################################################
if [ "$Drivers_Nvidia_CHOICE" == "Nvidia_Drivers" ]; then

	if [  -f "/userdata/system/99-nvidia.conf" ]; then
		cp /userdata/system/99-nvidia.conf /userdata/system/99-nvidia.conf.bak
	fi 

	# MYZAR's WORK and TESTS : THX DUDE !!
	if [ "$CRT_Freq" == "15KHz" ]; then
		cp /userdata/system/BUILD_15KHz/System_configs/Nvidia/99-nvidia.conf-generic_15  /userdata/system/99-nvidia.conf
	elif [ "$CRT_Freq" == "25KHz" ]; then
		cp /userdata/system/BUILD_15KHz/System_configs/Nvidia/99-nvidia.conf-generic_25  /userdata/system/99-nvidia.conf
	else
		cp /userdata/system/BUILD_15KHz/System_configs/Nvidia/99-nvidia.conf-generic_31  /userdata/system/99-nvidia.conf
	fi
	chmod 644 /userdata/system/99-nvidia.conf

	cp /userdata/system/99-nvidia.conf /userdata/system/99-nvidia.conf.bak

	if [ "$ES_resolution" == "640x480_60iHz" ]; then
		es_res_60iHz=""
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 640 480 --screenoffset 00 00"
			es_arg="--screensize 640 480 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 480 640 --screenoffset 00 00"
			es_arg="--screensize 480 640 --screenoffset 00 00"
		fi
	elif [[ "$ES_resolution" == "1024x768_60iHz" ]]; then
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 1024 768 --screenoffset 00 00"
			es_arg="--screensize 1024 768 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 768 1024 --screenoffset 00 00"
			es_arg="--screensize 768 1024 --screenoffset 00 00"
		fi
	elif [[ "$ES_resolution" == "768x576_50iHz" ]]; then
		es_res_60iHz="#"
		es_res_50iHz=""
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 768 576 --screenoffset 00 00"
			es_arg="--screensize 768 576 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 576 768 --screenoffset 00 00"
			es_arg="--screensize 576 768 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "1920x240_60iHz" ]; then 
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz=""
		es_SR_res_50iHz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 1920 240 --screenoffset 00 00"
			es_arg="--screensize 1920 240 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 240 1920 --screenoffset 00 00"
			es_arg="--screensize 240 1920 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "1920x256_50iHz" ]; then
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz=""
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 1920 256 --screenoffset 00 00"
			es_arg="--screensize 1920 256 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 256 1920 --screenoffset 00 00"
			es_arg="--screensize 256 1920 --screenoffset 00 00"
		fi
	else
		echo "#### NO RESOLUTION HERE"
	fi

	if [ "$CRT_Freq" == "15KHz" ]; then
		sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1920x240\]/$es_SR_res_60iHz/g" -e "s/\[1920x256\]/$es_SR_res_50iHz/g" /userdata/system/BUILD_15KHz/System_configs/Nvidia/custom-es-config-Nvidia-generic_15 > /userdata/system/custom-es-config
	elif [ "$CRT_Freq" == "25KHz" ]; then
		sed -e "s/\[card_display\]/$video_modeline/g" /userdata/system/BUILD_15KHz/System_configs/Nvidia/custom-es-config-Nvidia-generic_25 > /userdata/system/custom-es-config
	else
		sed -e "s/\[card_display\]/$video_modeline/g" /userdata/system/BUILD_15KHz/System_configs/Nvidia/custom-es-config-Nvidia-generic_31 > /userdata/system/custom-es-config
	fi
	chmod 755 /userdata/system/custom-es-config

else

	if [ -f "/userdata/system/99-nvidia.conf" ]; then
		cp /userdata/system/99-nvidia.conf /userdata/system/99-nvidia.conf.bak
		rm /userdata/system/99-nvidia.conf 
	fi

	if [ "$ES_resolution" == "640x480_60iHz" ]; then
		es_res_60iHz=""
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		es_SR_res_60Hz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 640 480 --screenoffset 00 00"
			es_arg="--screensize 640 480 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 480 640 --screenoffset 00 00"
			es_arg="--screensize 480 640 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "720x480_60iHz" ]; then
		es_res_60iHz="#"
        	es_res_50iHz="#"
		es_res_60_iHz=""
		es_SR_res_60iHz="#"
        	es_SR_res_50iHz="#"
		es_SR_res_60Hz="#"
 		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
        		es_customsargs="es.customsargs=--screensize 720 480 --screenoffset 00 00"
			es_arg="--screensize 720 480 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 480 720 --screenoffset 00 00"
			es_arg="--screensize 480 720 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "768x576_50iHz" ]; then
		es_res_60iHz="#"
		es_res_50iHz=""
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		es_SR_res_60Hz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 768 576 --screenoffset 00 00"
			es_arg="--screensize 768 576 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 576 768 --screenoffset 00 00"
			es_arg="--screensize 576 768 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "1024x768_60iHz" ]; then
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		es_SR_res_60Hz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
		es_customsargs="es.customsargs=--screensize 1024 768 --screenoffset 00 00"
			es_arg="--screensize 1024 768 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 768 1024 --screenoffset 00 00"
			es_arg="--screensize 768 1024 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "1280x480_60iHz" ]; then
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz=""
		es_SR_res_50iHz="#"
		es_SR_res_60Hz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 1280 480 --screenoffset 00 00"
			es_arg="--screensize 1280 480 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 480 1280 --screenoffset 00 00"
			es_arg="--screensize 480 1280 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "1280x576_50iHz" ]; then
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz=""
		es_SR_res_60Hz="#"
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 1280 576 --screenoffset 00 00"
			es_arg="--screensize 1280 576 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 576 1280 --screenoffset 00 00"
			es_arg="--screensize 576 1280 --screenoffset 00 00"
		fi
	elif [ "$ES_resolution" == "1280x240_60iHz" ]; then
		es_res_60iHz="#"
		es_res_50iHz="#"
		es_SR_res_60iHz="#"
		es_SR_res_50iHz="#"
		es_SR_res_60Hz=""
		if [ "$ES_rotation" == "NORMAL" ] || [ "$ES_rotation" == "INVERTED" ]; then
			es_customsargs="es.customsargs=--screensize 1280 240 --screenoffset 00 00"
			es_arg="--screensize 1280 240 --screenoffset 00 00"
		else
			es_customsargs="es.customsargs=--screensize 240 1280 --screenoffset 00 00"
			es_arg="--screensize 240 1280 -screenoffset 00 00"
		fi
	else
		echo "#### NO RESOLUTION HERE"
	fi

	if [ "$TYPE_OF_CARD" == "AMD/ATI" ] && [[ "$video_output" == *"DP"* ]]; then
		DP_Modeline=""
		DVI_Modeline="#"
	else
		DP_Modeline="#"
		DVI_Modeline=""
	fi

	case $monitor_name in
		arcade_15)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_15 > /userdata/system/custom-es-config
		;;
		arcade_15_SR240)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_15 > /userdata/system/custom-es-config
		;;
		arcade_15_SR480)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_15 > /userdata/system/custom-es-config

		;;
		arcade_15_25)
		;;
		arcade_15_25_31)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_15_25_31 > /userdata/system/custom-es-config
		;;
		arcade_15_31)
		;;
		arcade_15ex)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_15ex > /userdata/system/custom-es-config
		;;
		arcade_25)
			sed -e "s/\[card_display\]/$video_modeline/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_25 > /userdata/system/custom-es-config
		;;
		arcade_31)
			sed -e "s/\[card_display\]/$video_modeline/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-arcade_31 > /userdata/system/custom-es-config
		;;
		d9200)
		;;
		d9400)
		;;
		d9800)
		;;
		generic_15)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-generic_15 > /userdata/system/custom-es-config
		;;
		generic_15_SR240)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-generic_15 > /userdata/system/custom-es-config

		;;
		generic_15_SR480)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[DVI-I\]/$DVI_Modeline/g" -e "s/\[DP\]/$DP_Modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-generic_15 > /userdata/system/custom-es-config
		;;
		h9110)
		;;
		k7000)
		;;
		k7131)
		;;
		m2929)
		;;
		m3129)
		;;
		ms2930)
		;;
		ms929)
		;;
		ntsc)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[720x480\]/$es_res_60_iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-ntsc > /userdata/system/custom-es-config
		;;
		pal)
			sed -e "s/\[card_display\]/$video_modeline/g" -e "s/\[640x480\]/$es_res_60iHz/g" -e "s/\[768x576\]/$es_res_50iHz/g" -e "s/\[1280x480\]/$es_SR_res_60iHz/g" -e "s/\[1280x576\]/$es_SR_res_50iHz/g" -e "s/\[1280x240\]/$es_SR_res_60Hz/g" /userdata/system/BUILD_15KHz/System_configs/Custom-es-config_v34/custom-es-config-pal > /userdata/system/custom-es-config
		;;
		pc_31_120)
		;;
		pc_70_120)
		;;
		polo)
		;;
		pstar)
		;;
		r666b)
		;;
		vesa_1024)
		;;
		vesa_480)
		;;
		vesa_600)
		;;
		vesa_768)
		;;
		*)
		;;
	esac
	chmod 755 /userdata/system/custom-es-config
fi

cp /userdata/system/custom-es-config /userdata/system/custom-es-config.bak

#######################################################################################
# Create a first_script.sh for exiting of Emulationstation
#######################################################################################
## if the folder doesn't exist, it will be create now
if [ ! -d "/userdata/system/scripts" ];then
	mkdir /userdata/system/scripts
fi
sed -e "s/\[display_mame_rotation\]/$display_mame_rotate/g" -e "s/\[display_fbneo_rotation\]/$display_fbneo_rotate/g" -e "s/\[display_libretro_rotation\]/$display_libretro_rotate/g" \
	-e "s/\[display_standalone_rotation\]/$display_standalone_rotate/g" -e "s/\[display_ES_rotation\]/$display_rotate/g" \
	-e "s/\[card_display\]/$video_modeline/g" -e "s/\[es_resolution\]/$ES_resolution_V33/g" /userdata/system/BUILD_15KHz/System_configs/First_script/first_script.sh-generic-v33 > /userdata/system/scripts/first_script.sh
chmod 755 /userdata/system/scripts/first_script.sh

#######################################################################################
# Create 1_GunCon2.sh and GunCon2_Calibration.sh for V36, V37 and v38
#######################################################################################
if [ "$Version_of_batocera" == "v36" ]||[ "$Version_of_batocera" == "v37" ]||[ "$Version_of_batocera" == "v38" ]||[ "$Version_of_batocera" == "v39" ]; then
	sed -e "s/\[card_display\]/$video_modeline/g" /userdata/system/BUILD_15KHz/System_configs/First_script/1_GunCon2.sh-generic > /userdata/system/scripts/1_GunCon2.sh
	chmod 755 /userdata/system/scripts/1_GunCon2.sh
	sed -e "s/\[card_display\]/$video_modeline/g" /userdata/system/BUILD_15KHz/GunCon2/GunCon2_Calibration.sh-generic > /userdata/roms/crt/GunCon2_Calibration.sh
	chmod 755 /userdata/roms/crt/GunCon2_Calibration.sh
fi


#######################################################################################
## Copy of batocera.conf for Libretro cores for use with Switchres
#######################################################################################
# first time using the script save the batocera.conf in batocera.conf.bak
if [ ! -f "/userdata/system/batocera.conf.bak" ];then
	cp /userdata/system/batocera.conf /userdata/system/batocera.conf.bak
fi

# avoid append on each script launch
LINE_NO=$(sed -n '/## ES Settings, See wiki page on how to center EmulationStation/{=;q;}' /userdata/system/batocera.conf.bak)

if [ -z "$LINE_NO" ]; then 
	cp /userdata/system/batocera.conf.bak /userdata/system/batocera.conf 
else 
	truncate -s 0 batocera.conf
	sed -n "1,$(( LINE_NO - 1 )) p; $LINE_NO q" /userdata/system/batocera.conf.bak > /userdata/system/batocera.conf
fi

#######################################################################################
## how to center EmulationStation
#######################################################################################

echo "## ES Settings, See wiki page on how to center EmulationStation" >> /userdata/system/batocera.conf
echo $es_customsargs >> /userdata/system/batocera.conf

#######################################################################################"
## CRT GLOBAL CONFIG FOR RETROARCH
#######################################################################################"
echo "###################################################" >> /userdata/system/batocera.conf
echo "#	CRT CONFIG RETROARCH" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "global.retroarch.menu_driver=rgui" >> /userdata/system/batocera.conf
echo "global.retroarch.menu_show_advanced_settings=true" >> /userdata/system/batocera.conf
echo "global.retroarch.menu_enable_widgets=false" >> /userdata/system/batocera.conf
echo "global.retroarch.crt_switch_resolution = \"4\"" >> /userdata/system/batocera.conf
if [ "$dotclock_min" == "25.0" ]; then
	echo "global.retroarch.crt_switch_resolution_super = \"$super_width\"" >> /userdata/system/batocera.conf
else
	echo "global.retroarch.crt_switch_resolution_super = \"0\"" >> /userdata/system/batocera.conf
fi
echo "global.retroarch.crt_switch_hires_menu = \"true\""  >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "#	DISABLE DEFAULT SHADER, BILINEAR FILTERING & VRR"  >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "global.shaderset=none" >> /userdata/system/batocera.conf
echo "global.smooth=0" >> /userdata/system/batocera.conf
echo "global.retroarch.vrr_runloop_enable=0" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "#	DISABLE GLOBAL NOTIFICATIONS IN RETROARCH" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "##  Disable Retroarch Notifications for setting refresh rate" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_refresh_rate = \"false\"" >> /userdata/system/batocera.conf
echo "## Change Notifications Size. Default is 32 (way to big) but 10 looks better on a CRT " >> /userdata/system/batocera.conf
echo "global.retroarch.video_font_size = 10" >> /userdata/system/batocera.conf
echo "### Disable Everything with notifications" >> /userdata/system/batocera.conf
echo "global.retroarch.settings_show_onscreen_display = \"false\"" >> /userdata/system/batocera.conf
#########################################################################################################
##  SOME GLOBAL RETROARCH NOTIFICATIONS CAN BE AVOID WITH REPLACING TRUE BY FALSE    
#########################################################################################################
echo "## global notifications can be avoid with replacing \"true\" by \"false\"" >> /userdata/system/batocera.conf 
echo "global.retroarch.notification_show_autoconfig = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_cheats_applied = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_config_override_load = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_fast_forward = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_netplay_extra = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_patch_applied = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_remap_load = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_screenshot = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.notification_show_set_initial_disk = \"true\"" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "##  GUNCON2 SHADER SAVE FIX" >> /userdata/system/batocera.conf     
echo "###################################################" >> /userdata/system/batocera.conf
echo "global.retroarch.video_shader_preset_save_reference_enable = \"true\"" >> /userdata/system/batocera.conf
echo "global.retroarch.video_shader_enable = \"true\"" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "##  GLOBAL EMULATOR SETTINGS" >> /userdata/system/batocera.conf     
echo "###################################################" >> /userdata/system/batocera.conf
echo "global.bezel=none" >> /userdata/system/batocera.conf
echo "global.bezel.resize_tattoo=0" >> /userdata/system/batocera.conf
echo "global.bezel.tattoo=0" >> /userdata/system/batocera.conf
echo "global.bezel_stretch=0" >> /userdata/system/batocera.conf
echo "global.hud=none" >> /userdata/system/batocera.conf
#######################################################################################
##  Rotation of EmulationStation
#######################################################################################

term_rotation="display.rotate="
term_es_rotation=$term_rotation$((es_rotation_choice-1))
echo "# ES ROTATION  MODE" >> /userdata/system/batocera.conf
echo $term_es_rotation >> /userdata/system/batocera.conf

#######################################################################################
## Mame initialisation Batocera not for RetroLX at this time
#######################################################################################
cd /usr/bin/mame
./mame -cc
case $Version_of_batocera in
	v32)
		if [ ! -d "/userdata/system/.mame" ]; then
			mkdir /userdata/system/.mame
		fi
		mv /usr/bin/mame/*.ini /userdata/system/.mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-32 > /userdata/system/.mame/mame.ini
		chmod 644 /userdata/system/.mame/mame.ini
		cp /userdata/system/BUILD_15KHz//Mame_configs/ui.ini-switchres /userdata/system/.mame/ui.ini
		chmod 644 /userdata/system/.mame/ui.ini
		;;
	v33)	
		if [ ! -d "/userdata/system/configs/mame" ]; then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ]; then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/ini
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-33 > /userdata/system/configs/mame/ini/mame.ini chmod 644 /userdata/system/configs/mame/ini/mame.ini
		cp /userdata/system/BUILD_15KHz//Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ini/ui.ini
		chmod 644 /userdata/system/configs/mame/ini/ui.ini
	;;
	v34)
		if [ ! -d "/userdata/system/configs/mame" ]; then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ]; then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-v34 > /userdata/system/configs/mame/mame.ini
		chmod 644 /userdata/system/configs/mame/mame.ini
		cp /userdata/system/BUILD_15KHz/Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ui.ini
		chmod 644 /userdata/system/configs/mame/ui.ini
	;;
	v35)
		if [ ! -d "/userdata/system/configs/mame" ];then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ];then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-v35 > /userdata/system/configs/mame/mame.ini
		chmod 644 /userdata/system/configs/mame/mame.ini
		cp /userdata/system/BUILD_15KHz/Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ui.ini
		chmod 644 /userdata/system/configs/mame/ui.ini
	;;
	v36)
		if [ ! -d "/userdata/system/configs/mame" ];then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ];then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-v36 > /userdata/system/configs/mame/mame.ini
		chmod 644 /userdata/system/configs/mame/mame.ini
		cp /userdata/system/BUILD_15KHz/Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ui.ini
		chmod 644 /userdata/system/configs/mame/ui.ini

  		cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/plugin.ini /userdata/system/configs/mame/plugin.ini
		chmod 644 /userdata/system/configs/mame/plugin.ini  
	;;
	v37)
		if [ ! -d "/userdata/system/configs/mame" ];then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ];then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-v36 > /userdata/system/configs/mame/mame.ini
		chmod 644 /userdata/system/configs/mame/mame.ini
		cp /userdata/system/BUILD_15KHz/Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ui.ini
		chmod 644 /userdata/system/configs/mame/ui.ini

  		cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/plugin.ini /userdata/system/configs/mame/plugin.ini
		chmod 644 /userdata/system/configs/mame/plugin.ini  
	;;
 	v38)
		if [ ! -d "/userdata/system/configs/mame" ];then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ];then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-v36 > /userdata/system/configs/mame/mame.ini
		chmod 644 /userdata/system/configs/mame/mame.ini
		cp /userdata/system/BUILD_15KHz/Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ui.ini
		chmod 644 /userdata/system/configs/mame/ui.ini
  
 		cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/plugin.ini /userdata/system/configs/mame/plugin.ini
		chmod 644 /userdata/system/configs/mame/plugin.ini
	;;
 	v39)
		if [ ! -d "/userdata/system/configs/mame" ];then
			mkdir /userdata/system/configs/mame
			mkdir /userdata/system/configs/mame/ini
		elif [ ! -d "/userdata/system/configs/mame/ini" ];then
			mkdir /userdata/system/configs/mame/ini
		fi
		mv /usr/bin/mame/*.ini /userdata/system/configs/mame/
		sed -e "s/\[monitor-name\]/$monitor_name_MAME/g" -e "s/\[super_width_mame\]/$super_width_mame/g" -e "s/\[dotclock_min_mame\]/$dotclock_min_mame/g" \
			/userdata/system/BUILD_15KHz//Mame_configs/mame.ini-switchres-generic-v36 > /userdata/system/configs/mame/mame.ini
		chmod 644 /userdata/system/configs/mame/mame.ini
		cp /userdata/system/BUILD_15KHz/Mame_configs/ui.ini-switchres /userdata/system/configs/mame/ui.ini
		chmod 644 /userdata/system/configs/mame/ui.ini
  
 		cp /userdata/system/BUILD_15KHz/GunCon2/gunlight/plugin.ini /userdata/system/configs/mame/plugin.ini
		chmod 644 /userdata/system/configs/mame/plugin.ini
	;;
	*)
		echo "Problem of version"
	;;
esac

cp /userdata/system/configs/mame/mame.ini       /userdata/system/configs/mame/mame.ini.bak 

#######################################################################################
## UPGRADE Mame  Batocera  create an folder for new binary of MAME (GroovyMame)
####################################################################################### 
if [ ! -d "/userdata/system//mame" ];then
	mkdir /userdata/system/mame
fi
####################################################################################### 
echo "###################################################" >> /userdata/system/batocera.conf
echo "##  CRT SYSTEM SETTINGS" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "CRT.emulator=sh" >> /userdata/system/batocera.conf
echo "CRT.core=sh" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "##  GROOVYMAME EMULATOR SETTINGS" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "mame.bezel=none" >> /userdata/system/batocera.conf
echo "mame.bezel_stretch=0" >> /userdata/system/batocera.conf
echo "mame.core=mame" >> /userdata/system/batocera.conf
echo "mame.emulator=mame" >> /userdata/system/batocera.conf
echo "mame.bezel.tattoo=0" >> /userdata/system/batocera.conf
echo "mame.bgfxshaders=None" >> /userdata/system/batocera.conf
echo "mame.hud=none" >> /userdata/system/batocera.conf
echo "mame.switchres=1" >> /userdata/system/batocera.conf

echo "###################################################" >> /userdata/system/batocera.conf
echo "##  NEOGEO SYSTEM SETTINGS" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
echo "neogeo.bezel=none" >> /userdata/system/batocera.conf
echo "neogeo.bezel_stretch=0" >> /userdata/system/batocera.conf
echo "neogeo.core=mame" >> /userdata/system/batocera.conf
echo "neogeo.emulator=mame" >> /userdata/system/batocera.conf
echo "neogeo.bezel.tattoo=0" >> /userdata/system/batocera.conf
echo "neogeo.bgfxshaders=None" >> /userdata/system/batocera.conf
echo "neogeo.hud=none" >> /userdata/system/batocera.conf
echo "neogeo.switchres=1" >> /userdata/system/batocera.conf

echo "###################################################" >> /userdata/system/batocera.conf
echo "##  GROOVYMAME TATE SETTINGS" >> /userdata/system/batocera.conf
echo "###################################################" >> /userdata/system/batocera.conf
 
if [ -d "/userdata/system/configs/mame/ini" ];then
	if [ -f "/userdata/system/configs/mame/ini/horizont.ini" ];then
		rm /userdata/system/configs/mame/ini/horizont.ini
	fi
if [ -f "/userdata/system/configs/mame/ini/vertical.ini" ];then
		rm /userdata/system/configs/mame/ini/vertical.ini
	fi
fi

if [ $es_rotation_choice -eq 1 ]; then
	echo "mame.rotation=none" >> /userdata/system/batocera.conf
	case $Rotating_screen in 
		None)
			sed -e "s/\[super_width_vertical\]/$super_width_vertical/g" -e "s/\[interlace_vertical\]/$interlace_vertical/g" -e "s/\[dotclock_min_vertical\]/$dotclock_min_vertical/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/vertical_normal.ini > /userdata/system/configs/mame/ini/vertical.ini
		;;
		Clockwise)
			sed -e "s/\[super_width_vertical\]/$super_width_vertical/g" -e "s/\[interlace_vertical\]/$interlace_vertical/g" -e "s/\[dotclock_min_vertical\]/$dotclock_min_vertical/g" \
				  /userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/vertical_clockwise.ini > /userdata/system/configs/mame/ini/vertical.ini
		;;
		Counter-Clockwise)
			sed -e "s/\[super_width_vertical\]/$super_width_vertical/g" -e "s/\[interlace_vertical\]/$interlace_vertical/g" -e "s/\[dotclock_min_vertical\]/$dotclock_min_vertical/g" \
				 /userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/vertical_counter-clockwise.ini > /userdata/system/configs/mame/ini/vertical.ini
		;;
		*)
			echo "Problems of rotation_choice"
		;;
	esac
	echo "fbneo.video_allow_rotate=off" >> /userdata/system/batocera.conf
fi

if [ $es_rotation_choice -eq 2 ]; then
	echo "mame.rotation=autoror" >> /userdata/system/batocera.conf
	case $Rotating_screen in 
		None)	
			sed -e "s/\[super_width_horizont\]/$super_width_horizont/g" -e "s/\[interlace_horizont\]/$interlace_horizont/g" -e "s/\[dotclock_min_horizont\]/$dotclock_min_horizont/g" \
					/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/horizont_inverted.ini > /userdata/system/configs/mame/ini/horizont.ini
		;;
		Clockwise)
			sed -e "s/\[super_width_horizont\]/$super_width_horizont/g" -e "s/\[interlace_horizont\]/$interlace_horizont/g" -e "s/\[dotclock_min_horizont\]/$dotclock_min_horizont/g" \
					/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/horizont_counter-clockwise.ini > /userdata/system/configs/mame/ini/horizont.ini
		;;
		Counter-Clockwise)
			sed -e "s/\[super_width_horizont\]/$super_width_horizont/g" -e "s/\[interlace_horizont\]/$interlace_horizont/g" -e "s/\[dotclock_min_horizont\]/$dotclock_min_horizont/g" \
					/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/horizont_clockwise.ini > /userdata/system/configs/mame/ini/horizont.ini
		;;
		*)
			echo "Problems of rotation_choice"
		;;
	esac
	echo "fbneo.video_allow_rotate=off" >> /userdata/system/batocera.conf
fi

if [ $es_rotation_choice -eq 3 ]; then
	echo "mame.rotation=none" >> /userdata/system/batocera.conf
	case $Rotating_screen in 
		None)
			sed -e "s/\[super_width_vertical\]/$super_width_vertical/g" -e "s/\[interlace_vertical\]/$interlace_vertical/g" -e "s/\[dotclock_min_vertical\]/$dotclock_min_vertical/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/vertical_inverted.ini > /userdata/system/configs/mame/ini/vertical.ini
		;;
		Clockwise)
			sed -e "s/\[super_width_vertical\]/$super_width_vertical/g" -e "s/\[interlace_vertical\]/$interlace_vertical/g" -e "s/\[dotclock_min_vertical\]/$dotclock_min_vertical/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/vertical_clockwise.ini > /userdata/system/configs/mame/ini/vertical.ini
		;;
		Counter-Clockwise)
			sed -e "s/\[super_width_vertical\]/$super_width_vertical/g" -e "s/\[interlace_vertical\]/$interlace_vertical/g" -e "s/\[dotclock_min_vertical\]/$dotclock_min_vertical/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/vertical_counter-clockwise.ini > /userdata/system/configs/mame/ini/vertical.ini      
		;;
		*)
			echo "Problems of rotation_choice"
		;;
	esac
	echo "fbneo.video_allow_rotate=off" >> /userdata/system/batocera.conf
fi

if [ $es_rotation_choice -eq 4 ]; then
	echo "mame.rotation=autorol" >> /userdata/system/batocera.conf
	case $Rotating_screen in 
		None)
			sed -e "s/\[super_width_horizont\]/$super_width_horizont/g" -e "s/\[interlace_horizont\]/$interlace_horizont/g" -e "s/\[dotclock_min_horizont\]/$dotclock_min_horizont/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/horizont_normal.ini > /userdata/system/configs/mame/ini/horizont.ini
		;;
		Clockwise)
			sed -e "s/\[super_width_horizont\]/$super_width_horizont/g" -e "s/\[interlace_horizont\]/$interlace_horizont/g" -e "s/\[dotclock_min_horizont\]/$dotclock_min_horizont/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/horizont_clockwise.ini > /userdata/system/configs/mame/ini/horizont.ini
		;;
		Counter-Clockwise)
			sed -e "s/\[super_width_horizont\]/$super_width_horizont/g" -e "s/\[interlace_horizont\]/$interlace_horizont/g" -e "s/\[dotclock_min_horizont\]/$dotclock_min_horizont/g" \
				/userdata/system/BUILD_15KHz/Mame_configs/Mame_TATE/horizont_counter-clockwise.ini > /userdata/system/configs/mame/ini/horizont.ini
			;;
			*)
				echo "Problems of rotation_choice"
			;;
		esac
	echo "fbneo.video_allow_rotate=off" >> /userdata/system/batocera.conf
fi
chmod 755 /userdata/system/batocera.conf
