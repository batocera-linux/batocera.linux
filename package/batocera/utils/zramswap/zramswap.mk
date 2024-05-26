################################################################################
#
# zramswap
#
################################################################################

ZRAMSWAP_VERSION = 0.0.1
ZRAMSWAP_SOURCE =
ZRAMSWAP_SITE =

define ZRAMSWAP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/zramswap/zramswap $(TARGET_DIR)/usr/share/batocera/services/
endef

$(eval $(generic-package))
