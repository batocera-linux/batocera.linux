#!/bin/bash

if [ ! "$1" ];then
	echo -e "usage : recalbox-config.sh [command] [args]\nWith command in\n\toverscan [enable|disable]\n\tlsaudio\n\tgetaudio\n\taudio [hdmi|jack|auto|custom|x,y]\n\tcanupdate\n\tupdate\n\twifi [enable|disable] ssid key\n\tstorage [current|list|INTERNAL|ANYEXTERNAL|RAM|DEV UUID]\n\tsetRootPassword [password]\n\tgetRootPassword\n\ttz [|tz]"
	exit 1
fi
configFile="/boot/config.txt"
storageFile="/boot/recalbox-boot.conf"
command="$1"
mode="$2"
extra1="$3"
extra2="$4"
arch=`cat /recalbox/recalbox.arch`

recalboxupdateurl="https://batocera-linux.xorhub.com/upgrades"

preBootConfig() {
    mount -o remount,rw /boot
}

postBootConfig() {
    mount -o remount,ro /boot
}

log=/recalbox/share/system/logs/recalbox.log
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.py"

echo "---- recalbox-config.sh ----" >> $log

if [ "$command" == "getRootPassword" ]; then
    # security disabled, force the default one without changing boot configuration
    securityenabled="`$systemsetting  -command load -key system.security.enabled`"
    if [ "$securityenabled" != "1" ];then
	echo "linux"
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

if [ "$command" == "lsoutputs" ]
then
    if [[ "${arch}" =~ "x86" ]]
    then
	echo "auto"
	xrandr --listConnectedOutputs
    else
	echo "auto"
    fi
fi

if [ "$command" == "setoutput" ]
then
    if [[ "${arch}" =~ "x86" ]]
    then
	if xrandr --listConnectedOutputs | grep -qE "^${mode}$"
	then
	    # disable all other outputs
	    xrandr --listConnectedOutputs | grep -vE "^${mode}$" |
		while read OUTP
		do
		    xrandr --output "${OUTP}" --off
		done
	else
	    # disable all except the first one
	    xrandr --listConnectedOutputs |
		(
		    read FIRSTOUTPUT
		    while read OUTP
		    do
			xrandr --output "${OUTP}" --off
		    done
		)
	fi
    else
	echo "auto"
    fi
fi

if [ "$command" == "lsaudio" ];then
    if [[ "${arch}" =~ "rpi" ]]
    then
	echo "hdmi"
	echo "jack"
	echo "auto"
    elif [[ "${arch}" =~ "x86" ]];then
	echo "auto"
	echo "custom"
	LANG=C aplay -l | grep -E '^card [0-9]*:' | sed -e s+'^card \([0-9]*\): [^,]*, device \([0-9]*\): [^\[]* \[\([^]]*\)].*$'+'\1,\2 \3'+
    else
	echo "auto"
    fi
fi

if [ "$command" == "getaudio" ];then
    $systemsetting -command load -key audio.device
    exit 0
fi

if [ "$command" == "audio" ];then
    # this code is specific to the rpi
    # don't set it on other boards
    # find a more generic way would be nice
    if [[ "${arch}" =~ "rpi" ]]
    then
	# this is specific to the rpi
	cmdVal="0"
	if [ "$mode" == "hdmi" ];then
	    cmdVal="2"
	elif [ "$mode" == "jack" ];then
	    cmdVal="1"
	fi
        echo "`logtime` : setting audio output mode : $mode" >> $log
	amixer cset numid=3 $cmdVal || exit 1
    elif [[ "${arch}" =~ "x86" ]]
    then
	# auto: no .asoundrc file
	# custom: don't touch the .asoundrc file
	# any other, create the .asoundrd file
	if [ "$mode" == "auto" ];then
	    rm -rf /recalbox/share/system/.asoundrc || exit 1
	elif [ "$mode" != "custom" ];then
	    if echo "${mode}" | grep -qE '^[0-9]*,[0-9]* '
	    then
		cardnb=$(echo "${mode}" | sed -e s+'^\([0-9]*\),.*$'+'\1'+)
		devicenb=$(echo "${mode}" | sed -e s+'^[0-9]*,\([0-9]*\) .*$'+'\1'+)
		cat > /recalbox/share/system/.asoundrc <<EOF
	    pcm.!default { type plug slave { pcm "hw:${cardnb},${devicenb}" } }
	    ctl.!default { type hw card ${cardnb} }
EOF
		aplay "/recalbox/system/resources/sounds/Mallet.wav"
	    fi
	fi
    fi
    exit 0
fi

if [ "$command" == "volume" ];then
	if [ "$mode" != "" ];then
        	echo "`logtime` : setting audio volume : $mode" >> $log

		# on my pc, the master is turned off at boot
		# i don't know what are the rules to set here.
		amixer set Master unmute      || exit 1
                amixer set Master    -- ${mode}% || exit 1

		# maximize the sound to be sure it's not 0, allow errors
		amixer set PCM       -- 100% #|| exit 1
		amixer set Headphone -- 100% #|| exit 1
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
	updateurl="`$systemsetting  -command load -key updates.url`"

	# customizable upgrade url website
	if test -n "${updateurl}"
	then
	    recalboxupdateurl="${updateurl}"
	fi

	#echo "Update url: ${recalboxupdateurl}/${arch}/${updatetype}/last"
	available=`wget -qO- ${recalboxupdateurl}/${arch}/${updatetype}/last/batocera.version`
	if [[ "$?" != "0" ]];then
	        echo "Unable to access the url" >&2
		exit 2
	fi
	installed=`cat /recalbox/batocera.version`

	echo "Current: ${installed}"
	echo "New: ${available}"

	if [[ "$available" != "$installed" ]]; then
		exit 0
	fi
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
	    cat > "/var/lib/connman/recalbox_wifi.config" <<EOF
[global]
Name=recalbox

[service_recalbox_default]
Type=wifi
Name=${ssid}
EOF
	    if test "${psk}" != ""
	    then
		echo "Passphrase=${psk}" >> "/var/lib/connman/recalbox_wifi.config"
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

	INTERNAL_DEVICE=$(/recalbox/scripts/recalbox-part.sh share_internal)
	PARTPREFIX=$(/recalbox/scripts/recalbox-part.sh prefix "${INTERNAL_DEVICE}")
	lsblk -n -P -o NAME,FSTYPE,LABEL,UUID,SIZE,TYPE |
	    grep 'TYPE="part"' |
	    grep -v "FSTYPE=\"swap\"" |
	    sed -e s+'^NAME="'+'NAME="/dev/'+ -e s+'LABEL=""'+'LABEL="NO_NAME"'+ |
	    grep -vE "^NAME=\"${PARTPREFIX}" |
	    sed -e s+'^NAME="[^"]*" FSTYPE="[^"]*" LABEL="\([^"]*\)" UUID="\([^"]*\)" SIZE="\([^"]*\)" TYPE="[^"]*"$'+'DEV \2 \1 - \3'+
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
   killall -9 hcitool
   /etc/init.d/S32bluetooth stop
   rm -rf /var/lib/bluetooth
   mkdir /var/lib/bluetooth
   rm -f /recalbox/share/system/bluetooth/bluetooth.tar
   /etc/init.d/S32bluetooth start
   exit 0
fi

if [ "$command" == "tz" ];then
    if test "$mode" == ""
    then
	cat /recalbox/system/resources/tz
    else
	if test -f "/usr/share/zoneinfo/${mode}"
	then
	    echo "${mode}" > /etc/timezone
            ln -sf "/usr/share/zoneinfo/${mode}" /etc/localtime
	fi
    fi
    exit $?
fi

exit 10
