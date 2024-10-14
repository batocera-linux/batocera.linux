#!/bin/bash

reportOnceConfigurationAvailable() {
    STARTFILE="/var/run/virtual-events.started"
    LOADERFILE="/var/run/virtual-events.waiting"

    test -e "${STARTFILE}" && return # normal behavior
    echo "keboardtopads ${ACTION} ${DEVNAME} ${DEVPATH} keyboardToPadsLauncher ${1} run" >> "${LOADERFILE}"
    exit 0
}

getConfigName() {
    SAFENAME=$(echo "${1}" | sed -e s+'[^a-zA-Z0-9]'++g) # keep only letters and integers
    echo "${SAFENAME}.v${2}.p${3}.yml"
}

doHelp() {
    echo "keyboardToPadsLauncher <event> <run|checkconfig>" >&2
}

PHYSDEV=$1
if ! test -e "${PHYSDEV}"
then
    doHelp
    exit 1
fi

# handle de device at boot : wait /userdata is available
reportOnceConfigurationAvailable "${PHYSDEV}"

# get the name / vid / pid
PHYSNAME=$(evtest --info "${PHYSDEV}" | grep -E '^Input device name:' | sed -e s+"^Input device name: \"\(.*\)\"$"+"\1"+)
PHYSVID=$( evtest --info "${PHYSDEV}" | grep -E '^Input device ID:'   | sed -e s+"^Input device ID: bus.*vendor 0x\([a-f0-9]*\) product .*$"+"\1"+  | sed -e s+'^\(...\)$'+'0\1'+)
PHYSPID=$( evtest --info "${PHYSDEV}" | grep -E '^Input device ID:'   | sed -e s+"^Input device ID: bus.*product 0x\([a-f0-9]*\) version .*$"+"\1"+ | sed -e s+'^\(...\)$'+'0\1'+)

CONFIGNAME=$(getConfigName "${PHYSNAME}" "${PHYSVID}" "${PHYSPID}")
CONFIGFILE=""
test -e "/usr/share/keyboardToPads/inputs/${CONFIGNAME}"               && CONFIGFILE="/usr/share/keyboardToPads/inputs/${CONFIGNAME}"
test -e "/userdata/system/configs/keyboardToPads/inputs/${CONFIGNAME}" && CONFIGFILE="/userdata/system/configs/keyboardToPads/inputs/${CONFIGNAME}"

ACTION=$2

if test "${ACTION}" == "checkconfigsys"
then
    if test -e "/usr/share/keyboardToPads/inputs/${CONFIGNAME}"
    then
       echo 0
       exit 0
    fi
    if test -e "/userdata/system/configs/keyboardToPads/inputs/${CONFIGNAME}"
    then
	echo 0
	exit 0
    fi
    # keep keyboard to 1
    echo 1
    exit 0
fi

if test "${ACTION}" == "checkconfig"
then
    echo "Device ${PHYSNAME} / vendor id: ${PHYSVID} / product id: ${PHYSPID}"
    echo "checking /userdata/system/configs/keyboardToPads/inputs/${CONFIGNAME}..."
    echo "checking /usr/share/keyboardToPads/inputs/${CONFIGNAME}..."

    CONFIGFILE=""
    test -e "/usr/share/keyboardToPads/inputs/${CONFIGNAME}"               && CONFIGFILE="/usr/share/keyboardToPads/inputs/${CONFIGNAME}"
    test -e "/userdata/system/configs/keyboardToPads/inputs/${CONFIGNAME}" && CONFIGFILE="/userdata/system/configs/keyboardToPads/inputs/${CONFIGNAME}"
    if test -n "${CONFIGFILE}"
    then
	echo "Using config ${CONFIGFILE}" >&2
	exit 0
    fi

    echo "No config file found." >&2
    exit 1
else
    if test "${ACTION}" == "run"
    then
	if test -n "${CONFIGFILE}"
	then
	    echo "using config file ${CONFIGFILE}" >&2
	    keyboardToPads --config "${CONFIGFILE}" --rules > "/run/udev/rules.d/${CONFIGNAME}.rules" || exit 1
	    udevadm control --reload-rules || exit 1
	    if test -t 1 # check output is a tty
	    then
		keyboardToPads --config "${CONFIGFILE}" --input "${1}" --run
	    else
		nohup keyboardToPads --config "${CONFIGFILE}" --input "${1}" --run &
	    fi
	else
	    # no config file found, do 1 to 1 mapping to enable keyboard
	    # map the same, but this one will have ID_INPUT_KEYBOARD set to 1
	    if test -t 1 # check output is a tty
	    then
		evsieve --input "${1}" --output name="Default virtual keyboard"
	    else
		nohup evsieve --input "${1}" --output name="Default virtual keyboard" &
	    fi
	fi
    else
	doHelp
    fi
fi
