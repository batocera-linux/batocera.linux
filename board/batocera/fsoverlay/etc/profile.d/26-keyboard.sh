#!/bin/sh

log="/userdata/system/logs/batocera.log"

# Set keyboard environment variables
settings_kb_layout="$(/usr/bin/batocera-settings-get system.kblayout || echo 'us')"
[ -z "$settings_kb_layout" ] && settings_kb_layout="us"
settings_kb_variant="$(/usr/bin/batocera-settings-get system.kbvariant || echo '')"

# Export variables for graphical sessions (Sway, Xorg)
export XKB_LAYOUT="$settings_kb_layout"
export XKB_VARIANT="$settings_kb_variant"
echo "Keyboard layout set to ${XKB_LAYOUT}" >> $log
echo "Keyboard variant set to ${XKB_VARIANT}" >> $log
