################################################################################
#
# batocera-settings
#
################################################################################

BATOCERA_SETTINGS_VERSION = 0.0.5
BATOCERA_SETTINGS_LICENSE = MIT
BATOCERA_SETTINGS_SITE = $(call github,batocera-linux,mini_settings,$(BATOCERA_SETTINGS_VERSION))
BATOCERA_SETTINGS_CONF_OPTS = \
  -Ddefault_config_path=/userdata/system/batocera.conf \
  -Dget_exe_name=batocera-settings-get \
  -Dset_exe_name=batocera-settings-set

define BATOCERA_SETTINGS_INSTALL_TARGET_CMDS
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-settings/batocera-settings-get-master $(TARGET_DIR)/usr/bin/batocera-settings-get-master
endef

$(eval $(meson-package))
