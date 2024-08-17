################################################################################
#
# aimtrak-guns
#
################################################################################
AIMTRAK_GUNS_VERSION = 1
AIMTRAK_GUNS_LICENSE = GPL
AIMTRAK_GUNS_SOURCE=

define AIMTRAK_GUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/aimtrak-guns/99-Aimtrak_ATRAK.rules $(TARGET_DIR)/etc/udev/rules.d/99-Aimtrak_ATRAK.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/aimtrak-guns/aimtrak-add $(TARGET_DIR)/usr/bin/aimtrak-add
endef

$(eval $(generic-package))
