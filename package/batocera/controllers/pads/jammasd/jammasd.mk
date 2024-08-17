################################################################################
#
# jammasd
#
################################################################################

JAMMASD_VERSION = 1
JAMMASD_LICENCE = GPL
JAMMASD_SOURCE = 

define JAMMASD_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/jammasd/99-jammasd.rules $(TARGET_DIR)/etc/udev/rules.d/99-jammasd.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/jammasd/jammASDSplit $(TARGET_DIR)/usr/bin/jammASDSplit
endef

$(eval $(generic-package))
