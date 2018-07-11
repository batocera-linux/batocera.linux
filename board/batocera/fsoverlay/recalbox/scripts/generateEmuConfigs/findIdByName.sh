function findIdByName {
	joysticksystemindex=-1

	name="$1"
	handlers=`cat /proc/bus/input/devices | grep -A 6 "$name" | grep "H: Handlers"`
	regex="js([0-9]+)"
	echo "searching id of joystick '$name' in $handlers" >> ~/generateconfig.log
	IFS=$'\n'
	for handler in $handlers; do
		echo "searching in $handler" >> ~/generateconfig.log
	    	[[ $handler =~ $regex ]]
		joystickIndex="${BASH_REMATCH[1]}"
		echo "values ${BASH_REMATCH['1']} ${usedJoysticks[$joystickIndex]}" >> ~/generateconfig.log

		if [ -n "$joystickIndex" ] && [ -z "${usedJoysticks[$joystickIndex]}" ]; then
			echo "found joystick index for $1 : $joystickIndex" >> ~/generateconfig.log
			usedJoysticks[$joystickIndex]=1
			joysticksystemindex="${BASH_REMATCH[1]}"
			break
		fi
	done
}
