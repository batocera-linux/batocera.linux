#!/bin/bash 
#
# Suspend or shutdown
#

SUSPEND_MODE="$(/usr/bin/batocera-settings-get system.suspendmode)"

###############################
command="$1"
tz="$2"
if [ "${SUSPEND_MODE}" = "suspend" ]; then
	pm-is-supported --suspend && pm-suspend
elif [ "${SUSPEND_MODE}" = "hybrid" ]; then
	# pm-hibernate is not supported on the Win600 at the moment
	pm-is-supported --suspend-hybrid && pm-suspend-hybrid
else
	/sbin/shutdown -h now
fi
