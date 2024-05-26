################################################################################
#
# batocera triggerhappy
#
################################################################################

BATOCERA_TRIGGERHAPPY_VERSION = 1.1
BATOCERA_TRIGGERHAPPY_LICENSE = GPL
BATOCERA_TRIGGERHAPPY_DEPENDENCIES = triggerhappy # to erase the trigger happy S50 startup script
BATOCERA_TRIGGERHAPPY_SOURCE=

define BATOCERA_TRIGGERHAPPY_INSTALL_CONFIG
	mkdir -p $(TARGET_DIR)/etc/triggerhappy/triggers.d
	mkdir -p $(TARGET_DIR)/etc/init.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/multimedia_keys.conf          $(TARGET_DIR)/etc/triggerhappy/triggers.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/multimedia_keys_disabled.conf $(TARGET_DIR)/etc/triggerhappy/triggers.d
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/triggerhappy.service  $(TARGET_DIR)/etc/init.d/S50triggerhappy
endef

define BATOCERA_TRIGGERHAPPY_INSTALL_RK3326_CONFIG
    cp -v $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/rk3326/*.conf      $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

define BATOCERA_TRIGGERHAPPY_INSTALL_RK3399_CONFIG
	cp -v $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/rk3399/*.conf      $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

define BATOCERA_TRIGGERHAPPY_INSTALL_RK3128_CONFIG
	cp -v $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/rk3128/*.conf      $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

define BATOCERA_TRIGGERHAPPY_INSTALL_X86_64_CONFIG
	cp -v $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/x86_64/*.conf      $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_CONFIG

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_RK3326_CONFIG
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_RK3399_CONFIG
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
	BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_RK3128_CONFIG
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_X86_64_CONFIG
endif

$(eval $(generic-package))
