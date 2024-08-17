################################################################################
#
# dolphinbar-guns
#
################################################################################
DOLPHINBAR_GUNS_VERSION = 1
DOLPHINBAR_GUNS_LICENSE = GPL
DOLPHINBAR_GUNS_SOURCE=

define DOLPHINBAR_GUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/dolphinbar-guns/99-dolphinbar.rules $(TARGET_DIR)/etc/udev/rules.d/99-dolphinbar.rules
endef

$(eval $(generic-package))
