#!/bin/bash

if [ ! "$1" ];then
	echo -e "usage : recalbox-config.sh [command] [args]\nWith command in\n\toverscan [enable|disable]\n\toverclock [none|high|turbo|extrem]\n\taudio [hdmi|jack|auto]\n\tcanupdate\n\tupdate\n\twifi [enable|disable] ssid key"
	exit 1
fi
configFile="/boot/config.txt"
command="$1"
mode="$2"
extra1="$3"
extra2="$4"
version=`cat /recalbox/recalbox.arch`

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
  return 1
}

log=/recalbox/share/system/logs/recalbox.log
wpafile=/var/lib/wpa_supplicant.conf
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

echo "---- recalbox-config.sh ----" >> $log

if [ "$command" == "overscan" ]; then
if [ -f "$configFile" ];then
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
		exit 1
	fi
	exit 0
else
	exit 2
fi
fi

if [ "$command" == "overclock" ]; then

declare -A arm_freq
arm_freq["rpi2"]=1050
arm_freq["extrem"]=1100
arm_freq["turbo"]=1000
arm_freq["high"]=950
arm_freq["none"]=700
arm_freq["none-rpi2"]=900

declare -A core_freq
core_freq["rpi2"]=525
core_freq["extrem"]=550
core_freq["turbo"]=500
core_freq["high"]=250
core_freq["none"]=250
core_freq["none-rpi2"]=250

declare -A sdram_freq
sdram_freq["rpi2"]=480
sdram_freq["extrem"]=600
sdram_freq["turbo"]=600
sdram_freq["high"]=450
sdram_freq["none"]=400
sdram_freq["none-rpi2"]=450

declare -A force_turbo
force_turbo["rpi2"]=0
force_turbo["extrem"]=1
force_turbo["turbo"]=0
force_turbo["high"]=0
force_turbo["none"]=0
force_turbo["none-rpi2"]=0

declare -A over_voltage
over_voltage["rpi2"]=4
over_voltage["extrem"]=8
over_voltage["turbo"]=6
over_voltage["high"]=6
over_voltage["none"]=0
over_voltage["none-rpi2"]=0

declare -A over_voltage_sdram
over_voltage_sdram["rpi2"]=2
over_voltage_sdram["extrem"]=6
over_voltage_sdram["turbo"]=0
over_voltage_sdram["high"]=0
over_voltage_sdram["none"]=0
over_voltage_sdram["none-rpi2"]=0

declare -A gpu_freq
gpu_freq["rpi2"]=350
gpu_freq["extrem"]=250
gpu_freq["turbo"]=250
gpu_freq["high"]=250
gpu_freq["none"]=250
gpu_freq["none-rpi2"]=250

if [ -f "$configFile" ];then
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
        echo "`logtime` : enabled overclock mode : $mode" >> $log

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
	available=`wget -qO- http://archive2.recalbox.com/rsync/recalbox-$version/root/recalbox/recalbox.version`
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
	/recalbox/scripts/rsync-update/rsync-update.sh
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
        sed -i "s/eth[0-9]\+/$eth/g" /etc/network/interfaces
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
        sed -i "s/wlan[0-9]\+/$wlan/g" /etc/network/interfaces

        if [[ "$mode" == "enable" ]]; then
                echo "`logtime` : enabling wifi" >> $log
                cat $wpafile | grep network >> $log
                if [ "$?" != "0" ]; then
                        echo "`logtime` : creating network entry in $wpafile" >> $log
                        echo -e "network={\n\tssid=\"\"\n\tpsk=\"\"\n}" >> $wpafile
                fi
                sed -i "s/ssid=\".*\"/ssid=\"$ssid\"/g" $wpafile
                sed -i "s/psk=\".*\"/psk=\"$psk\"/g" $wpafile
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
                /usr/sbin/wpa_supplicant -i$wlan -c/var/lib/wpa_supplicant.conf &
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
		cat /etc/udev/rules.d/99-8bitdo.rules | grep "$mac" >> /dev/null
		if [ "$?" != "0" ]; then
			echo "adding rule for $mac" >> $log
			echo "SUBSYSTEM==\"input\", ATTRS{uniq}==\"$mac\", MODE=\"0666\", ENV{ID_INPUT_JOYSTICK}=\"1\"" >> /etc/udev/rules.d/99-8bitdo.rules
			killall udevd
			/etc/init.d/S10udev start
		fi
	fi
	
	hidd --connect $mac 
        exit $?
fi

exit 10


