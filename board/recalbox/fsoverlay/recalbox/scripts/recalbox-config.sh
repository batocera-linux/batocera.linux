#!/bin/bash

if [ ! "$1" ];then
	echo -e "usage : recalbox-config.sh [command] [args]\nWith command in\n\toverscan [enable|disable]\n\toverclock [none|high|turbo|extrem]\n\taudio [hdmi|jack|auto]\n\tcanupdate\n\tupdate\n\twifi [enable|disable] ssid key\n\tstorage [current|list|INTERNAL|ANYEXTERNAL|RAM|DEV UUID]"
	exit 1
fi
configFile="/boot/config.txt"
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

waitWifi() {
  DEVICE=$1
  TIMEOUT=$2

  N=0
  while test $N -lt $TIMEOUT
  do
    wpa_cli -i"$DEVICE" status | grep -qE '^wpa_state=COMPLETED$' && return 0
    sleep 1
    let N++
  done
  echo "`logtime` : wifi timeout" >> $log
  return 1
}

rb_wpa_supplicant() {
    wlan=$1
    TRY1T=$(date +%s)

    # default driver (nl80211)
    if /usr/sbin/wpa_supplicant -i$wlan -c/var/lib/wpa_supplicant.conf
    then
	return
    fi

    # try an other driver in case it failed in the following seconds
    TRY2T=$(date +%s)
    let TRYDELTA=$TRY2T-$TRY1T
    if test $TRYDELTA -lt 5
       then
	   # test an other driver in case the hardware is not migrated to the new driver
	   if /usr/sbin/wpa_supplicant -i$wlan -D wext -c/var/lib/wpa_supplicant.conf
	   then
	       return
	   fi
    fi
}

log=/recalbox/share/system/logs/recalbox.log
wpafile=/var/lib/wpa_supplicant.conf
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

echo "---- recalbox-config.sh ----" >> $log

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

if [[ "$command" == "ethernet" ]]; then
        eth="eth`ifconfig -a | sed -n \"s/eth\(.\).*/\1/p\"`"
        if [[ "$?" != "0" || "$eth" == "eth" ]];then
                echo "`logtime` : no eth interface found" >> $log
                exit 1
        else
                echo "`logtime` : $eth will be used as wired interface"
        fi
        sed -i "s/eth[0-9]\+/$eth/g" /var/network/interfaces # directly modify the file and not the link because sed create a temporary file in the same directory
        if [[ "$mode" == "start" ]]; then
                /sbin/ifdown $eth >> $log
                /sbin/ifup $eth >> $log
                exit $?
        elif [[ "$mode" == "stop" ]]; then
                /sbin/ifdown $eth >> $log
                exit $?
        fi

fi


if [[ "$command" == "wifi" ]]; then
        if [[ ! -f "$wpafile" ]];then
                echo "`logtime` : $wpafile do not exists" >> $log
                exit 1
        fi
        ssid="$3"
        psk="$4"

        wlan="wlan`ifconfig -a | sed -n \"s/wlan\(.\).*/\1/p\"`"
        if [[ "$?" != "0" || "$wlan" == "wlan" ]] ;then
                echo "`logtime` : no wlan interface found" >> $log
                exit 1
        else
                echo "`logtime` : $wlan be used as wifi interface" >> $log
        fi
        sed -i "s/wlan[0-9]\+/$wlan/g" /var/network/interfaces # directly modify the file and not the link because sed create a temporary file in the same directory

        if [[ "$mode" == "enable" ]]; then
                echo "`logtime` : enabling wifi" >> $log
                cat $wpafile | grep network >> $log
                if [ "$?" != "0" ]; then
                        echo "`logtime` : creating network entry in $wpafile" >> $log
                        echo -e "network={\n\tssid=\"\"\n\tpsk=\"\"\n}" >> $wpafile
                fi
                sed -i "s/ssid=\".*\"/ssid=\"`echo $ssid | sed -e 's/[\/&]/\\\\&/g'`\"/g" $wpafile
                sed -i "s/psk=\".*\"/psk=\"`echo $psk | sed -e 's/[\/&]/\\\\&/g'`\"/g" $wpafile
                mode="forcestart"
        fi
        if [[ "$mode" == "disable" ]]; then
                sed -i "s/ssid=\".*\"/ssid=\"\"/g" $wpafile
                sed -i "s/psk=\".*\"/psk=\"\"/g" $wpafile
                ifdown $wlan
                exit $?
        fi
  	if [[ "$mode" =~ "start" ]]; then
                if [[ "$mode" != "forcestart" ]]; then
                        settingsWlan="`$systemsetting -command load -key wifi.enabled`"
                        if [ "$settingsWlan" != "1" ];then
                                exit 1
                        fi
                fi
                echo "`logtime` : starting wifi" >> $log
                killall wpa_supplicant >> $log
                /sbin/ifdown $wlan >> $log
		rb_wpa_supplicant "$wlan" &
                waitWifi $wlan 20
                /sbin/ifup $wlan >> $log
                ifconfig $wlan | grep "inet addr" >> $log
                exit $?
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

storageFile="/boot/recalbox-boot.conf"

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
    if [[ "$mode" == "INTERNAL" || "$mode" == "ANYEXTERNAL" || "$mode" == "RAM" || "$mode" == "DEV" ]]; then
	preBootConfig
	if [[ "$mode" == "INTERNAL" || "$mode" == "ANYEXTERNAL" || "$mode" == "RAM" ]]; then
            if [ `grep sharedevice $storageFile` ]; then
               sed -i "s|sharedevice=.*|sharedevice=$mode|g" $storageFile
            else
               echo "sharedevice=$mode" >> $storageFile
            fi
	fi
	if [[ "$mode" == "DEV" ]]; then
            if [ `grep sharedevice $storageFile` ]; then
               sed -i "s|sharedevice=.*|sharedevice=$mode $extra1|g" $storageFile
            else
               echo "sharedevice=$mode $extra1" >> $storageFile
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
