#!/bin/bash
echo -e "info : Launching post update scripts\n"
touch "/root/update-scripts.done"

updatesDones=`cat "/root/update-scripts.done"`
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
                	echo "$num" >> "/root/update-scripts.done"
        	fi
	fi
}

#startUpdate "01" "/recalbox/scripts/rsync-update/updates/01-replace-es-settings.sh"

exit 0
