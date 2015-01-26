#!/bin/bash
echo -e "info : Launching post update scripts\n"
touch "/root/updates.done"

updatesDones=`cat "/root/updates.done"`
function startUpdate {
	num="$1"
	script="$2"
	echo "$updatesDones" | grep "$num"
	if (( $? != "0")); then
		echo "starting update $num"
		eval "$script"
		if (("$?" != "0")); then
          	      echo "error : error occured with $script"
                	exit "$num"
        	else
                	echo "$num" >> "/root/updates.done"
        	fi
	fi
}

#startUpdate "08" "/retrobox/scripts/rsync-update/updates/08-remove-udev-retroarch-rule.sh"

exit 0
