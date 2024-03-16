################################################################################
#
# batocera-steam
#
################################################################################

BATOCERA_STEAM_VERSION = 1
BATOCERA_STEAM_SOURCE=

define BATOCERA_STEAM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-steam/batocera-steam \
	    $(TARGET_DIR)/usr/bin/
	install -m 0755 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-steam/batocera-steam-update \
		$(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
