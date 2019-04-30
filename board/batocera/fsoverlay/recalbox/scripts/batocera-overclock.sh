#!/bin/bash

ARCH=$(cat /usr/share/batocera/batocera.arch)
GRPICONFFILE="/boot/config.txt"

if test "${ARCH}" = "rpi3"
then
    if grep -q "^Raspberry Pi 3 Model [A-Z] Plus" "/proc/device-tree/model"
    then
	ARCH="rpi3+"
    fi
fi

preBootRPIConfig() {
    mount -o remount,rw /boot
}

postBootRPIConfig() {
    mount -o remount,ro /boot
}

doList() {
    case "${ARCH}" in
	"rpi")
	    echo "none NONE"
	    echo "high HIGH (950Mhz)"
	    echo "turbo TURBO (1000Mhz)"
	    echo "extrem EXTREM (1100Mhz)"
	;;
	"rpi2")
	    echo "none NONE (900Mhz)"
	    echo "high HIGH (1050Mhz)"
	;;
	"rpi3")
	    echo "none NONE (1200Mhz)"
	    echo "high HIGH (1300Mhz)"
	    echo "turbo TURBO (1325Mhz)"
	    echo "extrem EXTREM (1350Mhz)"
	    ;;
	"rpi3+")
	    echo "none NONE (1400Mhz)"
	    echo "high HIGH (1425Mhz)"
	    echo "turbo TURBO (1450Mhz)"
	    echo "extrem EXTREM (1500Mhz)"
	;;
	*)
	    echo "none NONE"
    esac
}

setValue_rpiNone() {
    preBootRPIConfig || return 1
    for entry in arm_freq core_freq sdram_freq force_turbo over_voltage over_voltage_sdram gpu_freq
    do
	sed -i "/^${entry}/d" "${GRPICONFFILE}"
    done
    postBootRPIConfig || return 1
}

setValue_rpiPutVars() {
    arm_freq=$1
    core_freq=$2
    sdram_freq=$3
    force_turbo=$4
    over_voltage=$5
    over_voltage_sdram=$6
    gpu_freq=$7

    preBootRPIConfig || return 1

    # put variable lines if not existing
    for entry in arm_freq core_freq sdram_freq force_turbo over_voltage over_voltage_sdram gpu_freq
    do
	if ! grep -q "${entry}" "${GRPICONFFILE}"
	then
	    if ! echo "${entry}=" >> "${GRPICONFFILE}"
	    then
		return 1
	    fi
	fi
    done

    # put values
    sed -i "s/#\?arm_freq=.*/arm_freq=${arm_freq}/g"                               "${GRPICONFFILE}" || return 1
    sed -i "s/#\?core_freq=.*/core_freq=${core_freq}/g"                            "${GRPICONFFILE}" || return 1
    sed -i "s/#\?sdram_freq=.*/sdram_freq=${sdram_freq}/g"                         "${GRPICONFFILE}" || return 1
    sed -i "s/#\?force_turbo=.*/force_turbo=${force_turbo}/g"                      "${GRPICONFFILE}" || return 1
    sed -i "s/#\?over_voltage=.*/over_voltage=${over_voltage}/g"                   "${GRPICONFFILE}" || return 1
    sed -i "s/#\?over_voltage_sdram=.*/over_voltage_sdram=${over_voltage_sdram}/g" "${GRPICONFFILE}" || return 1
    sed -i "s/#\?gpu_freq=.*/gpu_freq=${gpu_freq}/g"                               "${GRPICONFFILE}" || return 1

    postBootRPIConfig || return 1
}

setValue() {
    VALUE=$1

    case "${ARCH}" in
	"rpi")
	    case "${VALUE}" in
		"none")
		    setValue_rpiNone
		    ;;
		"high")
		    # arm_freq core_freq sdram_freq force_turbo over_voltage over_voltage_sdram gpu_freq
		    setValue_rpiPutVars  950 250 450 0 6 0 250
		    ;;
		"turbo")
		    setValue_rpiPutVars 1000 500 600 0 6 0 250
		    ;;
		"extrem")
		    setValue_rpiPutVars 1100 550 600 1 8 6 250
		    ;;
	    esac
	    ;;
	"rpi2")
	    case "${VALUE}" in
		"none")
		    setValue_rpiNone
		    ;;
		"high")
		    setValue_rpiPutVars 1050 525 450 0 4 2 350
		    ;;
	    esac
	    ;;
	"rpi3")
	    case "${VALUE}" in
		"none")
		    setValue_rpiNone
		    ;;
		"high")
		    setValue_rpiPutVars 1300 525 500 0 4 4 500
		    ;;
		"turbo")
		    setValue_rpiPutVars 1325 525 520 0 4 4 500
		    ;;
		"extrem")
		    setValue_rpiPutVars 1350 550 550 1 4 5 525
		    ;;
	    esac
	    ;;
	"rpi3+")
	    case "${VALUE}" in
		"none")
		    setValue_rpiNone
		    ;;
		"high")
		    setValue_rpiPutVars 1425 525 500 0 4 4 500
		    ;;
		"turbo")
		    setValue_rpiPutVars 1450 525 520 0 4 4 500
		    ;;
		"extrem")
		    setValue_rpiPutVars 1500 550 550 1 4 5 525
		    ;;
	    esac
	    ;;
    esac
}

ACTION=$1
shift

case "${ACTION}" in
    "list")
	if ! doList
	then
	    exit 1
	fi
	;;
    "set")
	VALUE=$1
	if ! setValue "${VALUE}"
	then
	    exit 1
	fi
esac

exit 0
