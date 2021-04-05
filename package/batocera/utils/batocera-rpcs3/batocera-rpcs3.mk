################################################################################
#
# batocera rpcs3
#
################################################################################

BATOCERA_RPCS3_VERSION = 1.0
BATOCERA_RPCS3_LICENSE = GPL
BATOCERA_RPCS3_SOURCE=

define BATOCERA_RPCS3_INSTALL_TARGET_CMDS
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-rpcs3/batocera-rpcs3 $(TARGET_DIR)/usr/bin/batocera-rpcs3

endef

$(eval $(generic-package))
