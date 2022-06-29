#!/bin/bash

EVENT=$1

test "$EVENT" = "gameStart" || test "$EVENT" = "gameStop" || exit 0

/etc/init.d/S18governor save
CPU_GOVERNOR="$(/usr/bin/batocera-settings-get system.cpu.governor)"

if { [ "${EVENT}" = "gameStart" ] && [ "${CPU_GOVERNOR}" = "performance" ]; }
then
  echo performance > /sys/devices/platform/ff400000.gpu/devfreq/ff400000.gpu/governor
  echo performance > /sys/devices/platform/dmc/devfreq/dmc/governor
else
  echo simple_ondemand > /sys/devices/platform/ff400000.gpu/devfreq/ff400000.gpu/governor
  echo dmc_ondemand    > /sys/devices/platform/dmc/devfreq/dmc/governor
fi

exit 0
