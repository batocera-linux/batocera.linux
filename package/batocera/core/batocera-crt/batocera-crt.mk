################################################################################
#
# batocera crt script
#
################################################################################

BATOCERA_CRT_VERSION = 1.0
BATOCERA_CRT_LICENSE = GPL
BATOCERA_CRT_SOURCE=

define BATOCERA_CRT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/
	rsync -arv $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-crt/BUILD_15KHz/ $(TARGET_DIR)/usr/share/batocera/datainit/system/BUILD_15KHz/
endef

$(eval $(generic-package))
