#!/bin/sh

log="/userdata/system/logs/batocera.log"

# Set language environment variables
settings_lang="$(/usr/bin/batocera-settings-get system.language || echo 'en_US')"
[ -z "${settings_lang}" ] && settings_lang=en_US
export LC_ALL="${settings_lang}.UTF-8"
export LANG=${LC_ALL}
echo "Language set to ${LC_ALL}" >> $log
