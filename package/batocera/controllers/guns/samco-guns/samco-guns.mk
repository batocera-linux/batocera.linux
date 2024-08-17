################################################################################
#
# samco-guns
#
################################################################################
SAMCO_GUNS_VERSION = 1
SAMCO_GUNS_LICENSE = GPL
SAMCO_GUNS_SOURCE=

define SAMCO_GUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/samco-guns/99-samco-guns.rules $(TARGET_DIR)/etc/udev/rules.d/99-samco-guns.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/samco-guns/virtual-samco-gun-status $(TARGET_DIR)/usr/bin/virtual-samco-gun-status
endef

$(eval $(generic-package))
