#!/bin/bash

es_settings="/root/.emulationstation/es_settings.cfg"
log=/root/recalbox.log


command="$1"
varname="$2"
newval="$3"

if [[ "$command" == "get" ]];then
	echo "`logtime` : essetting.sh - searching for $varname" >> $log
	settings=`cat "$es_settings" | sed -n "s/.*name=\"${varname}\" value=\"\(.*\)\".*/\1/p"`
	if [[ "$settings" != "" ]]; then
		echo "`logtime` : essetting.sh - found $varname : $settings" >> $log
		echo "$settings"
		exit 0
	fi
fi
if [[ "$command" == "set" ]];then 
        echo "essetting.sh - setting $varname to $newval" >> $log
	sed -i "s|name=\"${varname}\" value=\".*\"|name=\"${varname}\" value=\"${newval}\"|g" $es_settings
fi

exit 1

