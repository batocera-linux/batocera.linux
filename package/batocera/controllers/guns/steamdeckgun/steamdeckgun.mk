################################################################################
#
# steamdeckgun
#
################################################################################
STEAMDECKGUN_VERSION = 1.0
STEAMDECKGUN_LICENSE = GPL
STEAMDECKGUN_SOURCE=

define STEAMDECKGUN_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/steamdeckgun/99-steamdeckgun.rules $(TARGET_DIR)/etc/udev/rules.d/99-steamdeckgun.rules
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/steamdeckgun/steamdeckgun-add      $(TARGET_DIR)/usr/bin/steamdeckgun-add
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/steamdeckgun/steamdeckgun-remap    $(TARGET_DIR)/usr/bin/steamdeckgun-remap
endef

$(eval $(generic-package))
