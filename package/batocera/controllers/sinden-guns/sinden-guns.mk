################################################################################
#
# sinden-guns
#
################################################################################
SINDEN_GUNS_VERSION = 1
SINDEN_GUNS_LICENSE = GPL
SINDEN_GUNS_SOURCE=

define SINDEN_GUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/sinden-guns/99-sinden.rules $(TARGET_DIR)/etc/udev/rules.d/99-sinden.rules
endef

$(eval $(generic-package))
