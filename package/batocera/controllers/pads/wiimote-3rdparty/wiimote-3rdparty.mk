################################################################################
#
# wiimote-3rdparty
#
################################################################################
WIIMOTE_3RDPARTY_VERSION = 1
WIIMOTE_3RDPARTY_LICENSE = GPL
WIIMOTE_3RDPARTY_SOURCE=

define WIIMOTE_3RDPARTY_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/wiimote-3rdparty/wiimote3rdPartyConnect $(TARGET_DIR)/usr/bin/wiimote3rdPartyConnect
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/wiimote-3rdparty/wiimote-3rdparty.service $(TARGET_DIR)/usr/share/batocera/services/wiimote3rdparty
endef

$(eval $(generic-package))
