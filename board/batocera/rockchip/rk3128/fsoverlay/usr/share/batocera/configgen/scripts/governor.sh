#!/bin/bash

EVENT=$1

case "${EVENT}" in
    gameStart)
	echo performance > /sys/devices/platform/ff400000.gpu/devfreq/ff400000.gpu/governor
	echo performance > /sys/devices/platform/dmc/devfreq/dmc/governor
	echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
    ;;
    gameStop)
	echo simple_ondemand > /sys/devices/platform/ff400000.gpu/devfreq/ff400000.gpu/governor
	echo dmc_ondemand    > /sys/devices/platform/dmc/devfreq/dmc/governor
	echo performance     > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
    ;;
esac

exit 0
