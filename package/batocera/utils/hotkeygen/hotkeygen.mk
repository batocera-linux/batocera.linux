################################################################################
#
# hotkeygen
#
################################################################################

HOTKEYGEN_LICENSE = GPL
HOTKEYGEN_SETUP_TYPE=hatch
HOTKEYGEN_DEPENDENCIES = python-pyudev python-evdev python-batocera-common

define HOTKEYGEN_INSTALL_CONFIG_FILES
	mkdir -p $(TARGET_DIR)/etc/init.d
	mkdir -p $(TARGET_DIR)/etc/hotkeygen
	mkdir -p $(TARGET_DIR)/usr/share/hotkeygen
	$(INSTALL) -m 0755 $(@D)/hotkeygen.service $(TARGET_DIR)/etc/init.d/S90hotkeygen
	$(INSTALL) -m 0644 $(@D)/conf/default_context.conf $(TARGET_DIR)/etc/hotkeygen/default_context.conf
	$(INSTALL) -m 0644 $(@D)/conf/common_context.conf $(TARGET_DIR)/etc/hotkeygen/common_context.conf
	$(INSTALL) -m 0644 $(@D)/conf/default_mapping.conf $(TARGET_DIR)/etc/hotkeygen/default_mapping.conf
	$(INSTALL) -m 0644 $(@D)/conf/specific/*.mapping $(TARGET_DIR)/usr/share/hotkeygen/
endef

HOTKEYGEN_POST_INSTALL_TARGET_HOOKS += HOTKEYGEN_INSTALL_CONFIG_FILES

define HOTKEYGEN_INSTALL_SM8250_CONFIG
	$(INSTALL) -m 0644 $(@D)/conf/default_mapping-sm8250.conf $(TARGET_DIR)/etc/hotkeygen/default_mapping.conf
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8250),y)
	HOTKEYGEN_POST_INSTALL_TARGET_HOOKS += HOTKEYGEN_INSTALL_SM8250_CONFIG
endif

$(eval $(local-python-package))
