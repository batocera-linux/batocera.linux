################################################################################
#
# hotkeygen
#
################################################################################

HOTKEYGEN_VERSION = 1.0
HOTKEYGEN_LICENSE = GPL
HOTKEYGEN_SOURCE=
HOTKEYGEN_DEPENDENCIES = python-pyudev python-evdev

HOTKEYGEN_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/hotkeygen

define HOTKEYGEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/etc/init.d
	install -m 0755 $(HOTKEYGEN_PATH)/hotkeygen.py $(TARGET_DIR)/usr/bin/hotkeygen
	install -m 0755 $(HOTKEYGEN_PATH)/hotkeygen.service $(TARGET_DIR)/etc/init.d/S90hotkeygen
endef

$(eval $(generic-package))
