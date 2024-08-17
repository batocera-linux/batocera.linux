################################################################################
#
# Retro Shooter Lightguns
#
################################################################################
RETROSHOOTER_GUNS_VERSION = 1
RETROSHOOTER_GUNS_LICENSE = GPL
RETROSHOOTER_GUNS_SOURCE=

define RETROSHOOTER_GUNS_INSTALL_TARGET_CMDS
  $(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/retroshooter-guns/99-retroshooter-guns.rules              $(TARGET_DIR)/etc/udev/rules.d/99-retroshooter-guns.rules
  $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/retroshooter-guns/retroshooter-guns-add                   $(TARGET_DIR)/usr/bin/retroshooter-guns-add
  $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/retroshooter-guns/batocera-retroshooter-calibrator        $(TARGET_DIR)/usr/bin/batocera-retroshooter-calibrator
  $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/retroshooter-guns/batocera-retroshooter-calibrator-daemon $(TARGET_DIR)/usr/bin/batocera-retroshooter-calibrator-daemon
endef

$(eval $(generic-package))
