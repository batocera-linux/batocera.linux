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
	mkdir -p $(TARGET_DIR)/etc/hotkeygen
	install -m 0755 $(HOTKEYGEN_PATH)/hotkeygen.py $(TARGET_DIR)/usr/bin/hotkeygen
	install -m 0755 $(HOTKEYGEN_PATH)/hotkeygen.service $(TARGET_DIR)/etc/init.d/S90hotkeygen
	install -m 0644 $(HOTKEYGEN_PATH)/conf/default_context.conf $(TARGET_DIR)/etc/hotkeygen/default_context.conf
	install -m 0644 $(HOTKEYGEN_PATH)/conf/common_context.conf $(TARGET_DIR)/etc/hotkeygen/common_context.conf
	install -m 0644 $(HOTKEYGEN_PATH)/conf/default_mapping.conf $(TARGET_DIR)/etc/hotkeygen/default_mapping.conf
endef

define HOTKEYGEN_INSTALL_SM8250_CONFIG
	install -m 0644 $(HOTKEYGEN_PATH)/conf/default_mapping-sm8250.conf $(TARGET_DIR)/etc/hotkeygen/default_mapping.conf
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8250),y)
	HOTKEYGEN_POST_INSTALL_TARGET_HOOKS += HOTKEYGEN_INSTALL_SM8250_CONFIG
endif

$(eval $(generic-package))
