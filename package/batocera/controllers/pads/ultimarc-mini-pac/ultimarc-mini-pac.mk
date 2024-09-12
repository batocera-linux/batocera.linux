################################################################################
#
# ultimarc-mini-pac
#
################################################################################

ULTIMARC_MINI_PAC_VERSION = 1
ULTIMARC_MINI_PAC_LICENCE = GPL
ULTIMARC_MINI_PAC_SOURCE = 

define ULTIMARC_MINI_PAC_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/ultimarc-mini-pac/99-ultimarc-mini-pac.rules $(TARGET_DIR)/etc/udev/rules.d/99-ultimarc-mini-pac.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/ultimarc-mini-pac/ultimarc-mini-pacSplit $(TARGET_DIR)/usr/bin/ultimarc-mini-pacSplit
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/ultimarc-mini-pac/ultimarc-ipac4Split    $(TARGET_DIR)/usr/bin/ultimarc-ipac4Split
endef

$(eval $(generic-package))
