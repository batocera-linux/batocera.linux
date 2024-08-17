################################################################################
#
# blamcon
#
################################################################################
BLAMCON_VERSION = 1
BLAMCON_LICENSE = GPL
BLAMCON_SOURCE=

define BLAMCON_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/blamcon/99-blamcon.rules $(TARGET_DIR)/etc/udev/rules.d/99-blamcon.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/blamcon/virtual-blamcon-add $(TARGET_DIR)/usr/bin/virtual-blamcon-add
endef

$(eval $(generic-package))
