#!/bin/bash

if [ ! "$1" ];then
	echo -e "usage : recalbox-config.sh [command] [args]\nWith command in\n\toverscan [enable|disable]\n\toverclock [none|high|turbo|extrem]\n\taudio [hdmi|jack|auto]\n\tcanupdate\n\tupdate\n\twifi [enable|disable] ssid key\n\tstorage [current|list|INTERNAL|ANYEXTERNAL|RAM|DEV UUID]\n\tsetRootPassword [password]\n\tgetRootPassword"
	exit 1
fi
configFile="/boot/config.txt"
storageFile="/boot/recalbox-boot.conf"
command="$1"
mode="$2"
extra1="$3"
extra2="$4"
arch=`cat /recalbox/recalbox.arch`

recalboxupdateurl="http://archive.recalbox.com/4"

preBootConfig() {
    mount -o remount,rw /boot
}

postBootConfig() {
    mount -o remount,ro /boot
}

log=/recalbox/share/system/logs/recalbox.log
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

echo "---- recalbox-config.sh ----" >> $log

if [ "$command" == "getRootPassword" ]; then
    # security disabled, force the default one without changing boot configuration
    securityenabled="`$systemsetting  -command load -key system.security.enabled`"
    if [ "$securityenabled" != "1" ];then
	echo "recalboxroot"
	exit 0
    fi
    
    ENCPASSWD=$(grep -E '^[ \t]*rootshadowpassword[ \t]*=' "${storageFile}" | sed -e s+'^[ \t]*rootshadowpassword[ \t]*='++)
    if test -z "${ENCPASSWD}"
    then
	exit 1
    fi
    if ! /recalbox/scripts/recalbox-encode.sh decode "${ENCPASSWD}"
    then
	exit 1
    fi
    exit 0
fi

if [ "$command" == "setRootPassword" ]; then
    PASSWD=${2}

    # security disabled, don't change
    securityenabled="`$systemsetting  -command load -key system.security.enabled`"
    if [ "$securityenabled" != "1" ];then
	exit 0
    fi
    
    # if no password if provided, generate one
    if test -z "${PASSWD}"
    then
	PASSWD=$(tr -cd _A-Z-a-z-0-9 < /dev/urandom | fold -w8 | head -n1)
    fi
    PASSWDENC=$(/recalbox/scripts/recalbox-encode.sh encode "${PASSWD}")
    
    preBootConfig
    if grep -qE '^[ \t]*rootshadowpassword[ \t]*=' "${storageFile}"
    then
	# update it
	if ! sed -i -e s@'^[ \t]*rootshadowpassword[ \t]*=.*$'@"rootshadowpassword=${PASSWDENC}"@ "${storageFile}"
	then
	    postBootConfig
	    exit 1
	fi
	postBootConfig
	exit 0
    else
	# create it
	if ! echo "rootshadowpassword=${PASSWDENC}" >> "${storageFile}"
	then
	    postBootConfig
	    exit 1
	fi
	postBootConfig
	exit 0
    fi    
fi

if [ "$command" == "overscan" ]; then
if [ -f "$configFile" ];then
        preBootConfig
        cat "$configFile" | grep "disable_overscan"
	overscanPresent=$?

	if [ "$overscanPresent" != "0" ];then
		echo "disable_overscan=1" >> "$configFile"
	fi
	cat "$configFile" | grep "overscan_scale"
	overscanScalePresent=$?

	if [ "$overscanScalePresent" != "0" ];then
		echo "overscan_scale=1" >> "$configFile"
	fi

	if [ "$mode" == "enable" ];then
		echo "`logtime` : enabling overscan" >> $log
		sed -i "s/#\?disable_overscan=.*/disable_overscan=0/g" "$configFile"
		sed -i "s/#\?overscan_scale=.*/overscan_scale=1/g" "$configFile"
	elif [ "$mode" == "disable" ];then
                echo "`logtime` : disabling overscan" >> $log
                sed -i "s/#\?disable_overscan=.*/disable_overscan=1/g" "$configFile"
                sed -i "s/#\?overscan_scale=.*/overscan_scale=0/g" "$configFile"
	else
                postBootConfig
		exit 1
	fi
	postBootConfig
	exit 0
else
	exit 2
fi
fi

if [ "$command" == "overclock" ]; then

declare -A arm_freq
arm_freq["rpi2-extrem"]=1100
arm_freq["rpi2-turbo"]=1050
arm_freq["rpi2-high"]=1050
arm_freq["extrem"]=1100
arm_freq["turbo"]=1000
arm_freq["high"]=950
arm_freq["none"]=700
arm_freq["none-rpi2"]=900

declare -A core_freq
core_freq["rpi2-extrem"]=550
core_freq["rpi2-turbo"]=525
core_freq["rpi2-high"]=525
core_freq["extrem"]=550
core_freq["turbo"]=500
core_freq["high"]=250
core_freq["none"]=250
core_freq["none-rpi2"]=250

declare -A sdram_freq
sdram_freq["rpi2-extrem"]=480
sdram_freq["rpi2-turbo"]=480
sdram_freq["rpi2-high"]=450
sdram_freq["extrem"]=600
sdram_freq["turbo"]=600
sdram_freq["high"]=450
sdram_freq["none"]=400
sdram_freq["none-rpi2"]=450

declare -A force_turbo
force_turbo["rpi2-extrem"]=1
force_turbo["rpi2-turbo"]=0
force_turbo["rpi2-high"]=0
force_turbo["extrem"]=1
force_turbo["turbo"]=0
force_turbo["high"]=0
force_turbo["none"]=0
force_turbo["none-rpi2"]=0

declare -A over_voltage
over_voltage["rpi2-extrem"]=4
over_voltage["rpi2-turbo"]=4
over_voltage["rpi2-high"]=4
over_voltage["extrem"]=8
over_voltage["turbo"]=6
over_voltage["high"]=6
over_voltage["none"]=0
over_voltage["none-rpi2"]=0

declare -A over_voltage_sdram
over_voltage_sdram["rpi2-extrem"]=4
over_voltage_sdram["rpi2-turbo"]=2
over_voltage_sdram["rpi2-high"]=2
over_voltage_sdram["extrem"]=6
over_voltage_sdram["turbo"]=0
over_voltage_sdram["high"]=0
over_voltage_sdram["none"]=0
over_voltage_sdram["none-rpi2"]=0

declare -A gpu_freq
gpu_freq["rpi2-extrem"]=366
gpu_freq["rpi2-turbo"]=350
gpu_freq["rpi2-high"]=350
gpu_freq["extrem"]=250
gpu_freq["turbo"]=250
gpu_freq["high"]=250
gpu_freq["none"]=250
gpu_freq["none-rpi2"]=250

if [ -f "$configFile" ];then
        preBootConfig
        if [[ "$mode" == "none" ]]; then
          for entry in arm_freq core_freq sdram_freq force_turbo over_voltage over_voltage_sdram gpu_freq; do
	    sed -i "/^${entry}/d" "$configFile"
          done
        else
	cat "$configFile" | grep "arm_freq"
	if [ "$?" != "0" ];then
		echo "arm_freq=" >> "$configFile"
	fi
	cat "$configFile" | grep "core_freq"
	if [ "$?" != "0" ];then
		echo "core_freq=" >> "$configFile"
	fi
	cat "$configFile" | grep "sdram_freq"
	if [ "$?" != "0" ];then
		echo "sdram_freq=" >> "$configFile"
	fi
	cat "$configFile" | grep "force_turbo"
	if [ "$?" != "0" ];then
		echo "force_turbo=" >> "$configFile"
	fi
	cat "$configFile" | grep "over_voltage"
	if [ "$?" != "0" ];then
		echo "over_voltage=" >> "$configFile"
	fi
	cat "$configFile" | grep "over_voltage_sdram"
	if [ "$?" != "0" ];then
		echo "over_voltage_sdram=" >> "$configFile"
	fi
	cat "$configFile" | grep "gpu_freq"
	if [ "$?" != "0" ];then
		echo "gpu_freq=" >> "$configFile"
	fi

	sed -i "s/#\?arm_freq=.*/arm_freq=${arm_freq[$mode]}/g" "$configFile"
	sed -i "s/#\?core_freq=.*/core_freq=${core_freq[$mode]}/g" "$configFile"
	sed -i "s/#\?sdram_freq=.*/sdram_freq=${sdram_freq[$mode]}/g" "$configFile"
	sed -i "s/#\?force_turbo=.*/force_turbo=${force_turbo[$mode]}/g" "$configFile"
	sed -i "s/#\?over_voltage=.*/over_voltage=${over_voltage[$mode]}/g" "$configFile"
	sed -i "s/#\?over_voltage_sdram=.*/over_voltage_sdram=${over_voltage_sdram[$mode]}/g" "$configFile"
	sed -i "s/#\?gpu_freq=.*/gpu_freq=${gpu_freq[$mode]}/g" "$configFile"
        fi
        echo "`logtime` : enabled overclock mode : $mode" >> $log

	postBootConfig
	
	exit 0
else
	exit 2
fi

fi

if [ "$command" == "audio" ];then
	cmdVal="0"
	if [ "$mode" == "hdmi" ];then
		cmdVal="2"
	elif [ "$mode" == "jack" ];then
		cmdVal="1"
	fi
        echo "`logtime` : setting audio output mode : $mode" >> $log
	amixer cset numid=3 $cmdVal || exit 1
	exit 0
fi

if [ "$command" == "volume" ];then
	if [ "$mode" != "" ];then
        	echo "`logtime` : setting audio volume : $mode" >> $log
		amixer set PCM -- ${mode}% || exit 1
		exit 0
	fi
	exit 12
fi

if [ "$command" == "gpiocontrollers" ];then
	command="module"
	mode="load"
	extra1="mk_arcade_joystick_rpi"
	extra2="map=1,2"
fi

if [ "$command" == "module" ];then
	modulename="$extra1"
	map="$extra2"
	# remove in all cases
	rmmod /lib/modules/`uname -r`/extra/${modulename}.ko >> $log

        if [ "$mode" == "load" ];then
	        echo "`logtime` : loading module $modulename args = $map" >> $log
		insmod /lib/modules/`uname -r`/extra/${modulename}.ko $map >> $log
		[ "$?" ] || exit 1
        fi
	exit 0
fi

if [ "$command" == "canupdate" ];then
	updatetype="`$systemsetting  -command load -key updates.type`"
	if test "${updatetype}" != "stable" -a "${updatetype}" != "unstable" -a "${updatetype}" != "beta"
	then
		# force a default value in case the value is removed or miswritten
		updatetype="stable"
	fi
	available=`wget -qO- ${recalboxupdateurl}/${arch}/${updatetype}/last/recalbox.version`
	if [[ "$?" != "0" ]];then
		exit 2
	fi
	installed=`cat /recalbox/recalbox.version`
	if [[ "$available" != "$installed" ]]; then
		echo "update available"
		exit 0
	fi
	echo "no update available"
	exit 12
fi

if [ "$command" == "update" ];then
	/recalbox/scripts/recalbox-upgrade.sh
	exit $?
fi

if [[ "$command" == "wifi" ]]; then
        ssid="$3"
        psk="$4"

        if [[ "$mode" == "enable" ]]; then
            echo "`logtime` : configure wifi" >> $log
	    mkdir -p "/var/lib/connman" || exit 1
	    cat > "/var/lib/connman/recalbox.config" <<EOF
[global]
Name=recalbox

[service_recalbox_default]
Type=wifi
Name=${ssid}
EOF
	    if test "${psk}" != ""
	    then
		echo "Passphrase=${psk}" >> "/var/lib/connman/recalbox.config"
	    fi

	    connmanctl enable wifi || exit 1
	    connmanctl scan   wifi || exit 1
            exit 0
        fi
  	if [[ "$mode" =~ "start" ]]; then
            if [[ "$mode" != "forcestart" ]]; then
                settingsWlan="`$systemsetting -command load -key wifi.enabled`"
                if [ "$settingsWlan" != "1" ];then
                    exit 1
                fi
            fi
	    connmanctl enable wifi || exit 1
	    connmanctl scan   wifi || exit 1
	    exit 0
        fi
        if [[ "$mode" == "disable" ]]; then
	    connmanctl disable wifi
            exit $?
        fi
	if [[ "$mode" == "list" ]]; then
	    WAVAILABLE=$(connmanctl services | cut -b 5- | sed -e s+'^\([^ ]*\).*$'+'\1'+ | grep -vE '^Wired$|^<hidden>$')
	    if test -n "${ssid}"
	    then
		echo "${WAVAILABLE}" | grep -qE '^'"${ssid}"'$' || echo "${ssid}"
	    fi
	    echo "${WAVAILABLE}"
            exit 0
	fi
fi
if [[ "$command" == "hcitoolscan" ]]; then
	killall hidd >> /dev/null
	killall hcitool >> /dev/null
	hcitool scan | tail -n +2
	exit 0
fi

if [[ "$command" == "hiddpair" ]]; then
	name="$extra1"
	mac1="$mode"
	mac=`echo $mac1 | grep -oEi "([0-9A-F]{2}[:-]){5}([0-9A-F]{2})" | tr '[:upper:]' '[:lower:]'`
	if [ "$?" != "0" ]; then 
		exit 1
	fi
	echo "pairing $name $mac" >>  $log
	echo $name | grep "8Bitdo\|other" >> $log
        if [ "$?" == "0" ]; then
                echo "8Bitdo detected" >> $log
                cat "/run/udev/rules.d/99-8bitdo.rules" | grep "$mac" >> /dev/null
                if [ "$?" != "0" ]; then
                        echo "adding rule for $mac" >> $log
                        echo "SUBSYSTEM==\"input\", ATTRS{uniq}==\"$mac\", MODE=\"0666\", ENV{ID_INPUT_JOYSTICK}=\"1\"" >> "/run/udev/rules.d/99-8bitdo.rules"
                fi
        fi
        hidd --connect $mac
        connected=$?
        deviceFile=/var/lib/bluetooth/known_devices
        if [ $connected ]; then
                cat $deviceFile | grep $mac1
                if [[ $? == "0" ]]; then
                        echo "bluetooth : $mac1 already in $deviceFile" >> $log
                else
                        echo "bluetooth : adding $mac1 in $deviceFile" >> $log
                        echo "$mac1" >> "$deviceFile"
                fi

		# backup files on the share directory
		rm -rf /recalbox/share/system/bluetooth
		if mkdir -p /recalbox/share/system/bluetooth
		then
		    ls /var/lib/bluetooth |
			while read X
			do
			    UX=$(echo "${X}" | sed -e s+":"+"@"+g)
			    cp -r "/var/lib/bluetooth/${X}" "/recalbox/share/system/bluetooth/${UX}"
			done
		fi
        fi
        exit $connected
fi

if [[ "$command" == "storage" ]]; then
    if [[ "$mode" == "current" ]]; then
	if test -e $storageFile
	then
            SHAREDEVICE=`cat ${storageFile} | grep "sharedevice=" | head -n1 | cut -d'=' -f2`
            [[ "$?" -ne "0" || "$SHAREDEVICE" == "" ]] && SHAREDEVICE=INTERNAL
	    echo "$SHAREDEVICE"
	else
	    echo "INTERNAL"
	fi
	exit 0
    fi
    if [[ "$mode" == "list" ]]; then
	echo "INTERNAL"
	echo "ANYEXTERNAL"
	echo "RAM"
	(blkid | grep -vE '^/dev/mmcblk' | grep ': LABEL="'
	 blkid | grep -vE '^/dev/mmcblk' | grep -v ': LABEL="' | sed -e s+':'+': LABEL="NO_NAME"'+
	) | sed -e s+'^[^:]*: LABEL="\([^"]*\)" UUID="\([^"]*\)" TYPE="[^"]*"$'+'DEV \2 \1'+
	exit 0
    fi
    if [[ "${mode}" == "INTERNAL" || "${mode}" == "ANYEXTERNAL" || "${mode}" == "RAM" || "${mode}" == "DEV" ]]; then
	preBootConfig
	if [[ "${mode}" == "INTERNAL" || "${mode}" == "ANYEXTERNAL" || "${mode}" == "RAM" ]]; then
            if grep -qE "^sharedevice=" "${storageFile}"
	    then
               sed -i "s|sharedevice=.*|sharedevice=${mode}|g" "${storageFile}"
            else
               echo "sharedevice=${mode}" >> "${storageFile}"
            fi
	fi
	if [[ "${mode}" == "DEV" ]]; then
            if grep -qE "^sharedevice=" "${storageFile}"
	    then
               sed -i "s|sharedevice=.*|sharedevice=${mode} $extra1|g" "${storageFile}"
            else
               echo "sharedevice=${mode} ${extra1}" >> "${storageFile}"
            fi
	fi
	postBootConfig
	exit 0
    fi
fi

if [[ "$command" == "forgetBT" ]]; then
   killall -9 hidd
   killall -9 hcitool
   rm -rf /var/lib/bluetooth/*
   exit 0
fi

exit 10
