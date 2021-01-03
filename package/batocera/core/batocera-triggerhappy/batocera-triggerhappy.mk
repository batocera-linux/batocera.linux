################################################################################
#
# batocera triggerhappy
#
################################################################################

BATOCERA_TRIGGERHAPPY_VERSION = 1
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

define BATOCERA_TRIGGERHAPPY_INSTALL_ODROIDGOA_CONFIG
	mkdir -p $(TARGET_DIR)/etc/triggerhappy/triggers.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/multimedia_keys_Hardkernel_ODROID_GO3.conf $(TARGET_DIR)/etc/triggerhappy/triggers.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/multimedia_keys_Anbernic_RG351P.conf       $(TARGET_DIR)/etc/triggerhappy/triggers.d

	# erase because some models are missing
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-triggerhappy/conf/multimedia_keys_odroidgoadvance.conf       $(TARGET_DIR)/etc/triggerhappy/triggers.d/multimedia_keys.conf
endef

BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_CONFIG

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	BATOCERA_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += BATOCERA_TRIGGERHAPPY_INSTALL_ODROIDGOA_CONFIG
endif

$(eval $(generic-package))
