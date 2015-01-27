#!/bin/bash
cp /recalbox/scripts/rsync-update/updates/es_settings.cfg /root/.emulationstation/es_settings.cfg

killall -9 emulationstation
reboot
