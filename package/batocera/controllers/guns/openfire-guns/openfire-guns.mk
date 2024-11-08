################################################################################
#
# OpenFIRE FIRECon light guns
#
################################################################################
OPENFIRE_GUNS_VERSION = 1
OPENFIRE_GUNS_LICENSE = GPL
OPENFIRE_GUNS_SOURCE =

define OPENFIRE_GUNS_INSTALL_TARGET_CMDS
  $(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/openfire-guns/99-openfire-guns.rules              $(TARGET_DIR)/etc/udev/rules.d/99-openfire-guns.rules
  $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/openfire-guns/virtual-openfire-add                $(TARGET_DIR)/usr/bin/virtual-openfire-add
endef

$(eval $(generic-package))
