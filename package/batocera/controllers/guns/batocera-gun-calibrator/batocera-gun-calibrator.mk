################################################################################
#
# batocera-gun-calibrator
#
################################################################################
BATOCERA_GUN_CALIBRATOR_VERSION = 1
BATOCERA_GUN_CALIBRATOR_LICENSE = GPL
BATOCERA_GUN_CALIBRATOR_SOURCE=

define BATOCERA_GUN_CALIBRATOR_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/batocera-gun-calibrator/batocera-gun-calibrator $(TARGET_DIR)/usr/bin/batocera-gun-calibrator
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/batocera-gun-calibrator/batocera-gun-calibrator-daemon $(TARGET_DIR)/usr/bin/batocera-gun-calibrator-daemon
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/batocera-gun-calibrator/99-gun-calibrator.rules $(TARGET_DIR)/etc/udev/rules.d/99-gun-calibrator.rules

endef

$(eval $(generic-package))
