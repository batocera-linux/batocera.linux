################################################################################
#
# batocera-nfc
#
################################################################################

BATOCERA_NFC_VERSION = 1.0
BATOCERA_NFC_LICENSE = GPL
BATOCERA_NFC_SOURCE=

define BATOCERA_NFC_POST_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-nfc/batocera-nfc.py $(TARGET_DIR)/usr/bin/batocera-nfc
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-nfc/scripts/on-nfc-connect/default.sh    $(TARGET_DIR)/usr/share/batocera/scripts/on-nfc-connect/default.sh
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-nfc/scripts/on-nfc-disconnect/default.sh $(TARGET_DIR)/usr/share/batocera/scripts/on-nfc-disconnect/default.sh

	# service
	mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-nfc/batocera-nfc.service $(TARGET_DIR)/usr/share/batocera/services/simple_nfc
endef

BATOCERA_NFC_POST_INSTALL_TARGET_HOOKS += BATOCERA_NFC_POST_INSTALL_TARGET_CMDS

$(eval $(generic-package))
