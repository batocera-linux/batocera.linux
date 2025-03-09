################################################################################
#
# onehit-guns
#
################################################################################
ONEHIT_GUNS_VERSION = 1
ONEHIT_GUNS_LICENSE = GPL
ONEHIT_GUNS_SOURCE=

define ONEHIT_GUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/onehit-guns/99-onehit.rules $(TARGET_DIR)/etc/udev/rules.d/99-onehit.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/onehit-guns/onehit-add $(TARGET_DIR)/usr/bin/onehit-add
endef

$(eval $(generic-package))
