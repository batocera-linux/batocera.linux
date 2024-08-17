################################################################################
#
# aelightgun
#
################################################################################
AELIGHTGUN_VERSION = 1
AELIGHTGUN_LICENSE = GPL
AELIGHTGUN_SOURCE=

define AELIGHTGUN_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/aelightgun/99-aelightgun.rules $(TARGET_DIR)/etc/udev/rules.d/99-aelightgun.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/aelightgun/virtual-aelightgun-add $(TARGET_DIR)/usr/bin/virtual-aelightgun-add
endef

$(eval $(generic-package))
