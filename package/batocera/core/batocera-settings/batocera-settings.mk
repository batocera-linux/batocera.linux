################################################################################
#
# batocera-settings
#
################################################################################

BATOCERA_SETTINGS_VERSION = 0.0.3
BATOCERA_SETTINGS_LICENSE = MIT
BATOCERA_SETTINGS_SITE = $(call github,batocera-linux,mini_settings,$(BATOCERA_SETTINGS_VERSION))
BATOCERA_SETTINGS_CONF_OPTS = \
  -Ddefault_config_path=/userdata/system/batocera.conf \
  -Dget_exe_name=batocera-settings-get \
  -Dset_exe_name=batocera-settings-set

$(eval $(meson-package))
