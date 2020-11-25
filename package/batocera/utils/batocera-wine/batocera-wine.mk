################################################################################
#
# batocera wine
#
################################################################################

BATOCERA_WINE_VERSION = 1.0
BATOCERA_WINE_LICENSE = GPL
BATOCERA_WINE_SOURCE=

define BATOCERA_WINE_INSTALL_TARGET_CMDS
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-wine/batocera-wine $(TARGET_DIR)/usr/bin/batocera-wine
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-wine/bsod.py       $(TARGET_DIR)/usr/bin/bsod-wine
	ln -fs /userdata/system/99-nvidia.conf $(TARGET_DIR)/etc/X11/xorg.conf.d/99-nvidia.conf
endef

$(eval $(generic-package))
