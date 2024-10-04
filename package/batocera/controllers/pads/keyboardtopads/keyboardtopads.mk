################################################################################
#
# keyboardtopads
#
################################################################################

KEYBOARDTOPADS_VERSION = 1
KEYBOARDTOPADS_LICENCE = GPL
KEYBOARDTOPADS_SOURCE = 

define KEYBOARDTOPADS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/keyboardtopads/99-keyboardtopads.rules   $(TARGET_DIR)/etc/udev/rules.d/99-keyboardtopads.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/keyboardtopads/keyboardToPads.py         $(TARGET_DIR)/usr/bin/keyboardToPads
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/keyboardtopads/keyboardToPadsLauncher.sh $(TARGET_DIR)/usr/bin/keyboardToPadsLauncher
	mkdir -p $(TARGET_DIR)/usr/share/keyboardToPads/inputs
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/keyboardtopads/inputs/*.yml              $(TARGET_DIR)/usr/share/keyboardToPads/inputs
endef

$(eval $(generic-package))
