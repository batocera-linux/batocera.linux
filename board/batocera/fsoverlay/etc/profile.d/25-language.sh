#!/bin/sh

log="/userdata/system/logs/language.log"

# --- language ---

settings_lang="$(/usr/bin/batocera-settings-get system.language || echo 'en_US')"
[ -z "${settings_lang}" ] && settings_lang=en_US

export LC_ALL="${settings_lang}.UTF-8"
export LANG=${LC_ALL}

echo "Language set to ${LC_ALL}" > "$log"

# --- keyboard layout ---

settings_kb="$(/usr/bin/batocera-settings-get system.kblayout)"
settings_kb_variant="$(/usr/bin/batocera-settings-get system.kbvariant)"

if [ "$settings_kb_variant" = "none" ] || [ -z "$settings_kb_variant" ]; then
    settings_kb_variant=""
fi

if [ -z "$settings_kb" ]; then
    settings_kb=$(echo "${settings_lang}" | cut -c1-2 | tr '[:upper:]' '[:lower:]')
fi

[ -z "$settings_kb" ] && settings_kb="us"

# wayland requires the default layout set
export XKB_DEFAULT_LAYOUT="$settings_kb"

if [ -n "$settings_kb_variant" ]; then
    export XKB_DEFAULT_VARIANT="$settings_kb_variant"
    export XKB_VARIANT="$settings_kb_variant"
else
    export XKB_DEFAULT_VARIANT=""
    export XKB_VARIANT=""
fi

# keep this for xorg
export XKB_LAYOUT="$settings_kb"

echo "Keyboard layout set to ${settings_kb} (variant: ${settings_kb_variant:-none})" >> "$log"
