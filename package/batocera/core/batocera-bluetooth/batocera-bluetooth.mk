################################################################################
#
# BATOCERA BLUETOOTH
#
################################################################################

BATOCERA_BLUETOOTH_VERSION = 1.0
BATOCERA_BLUETOOTH_LICENSE = GPL
BATOCERA_BLUETOOTH_SOURCE=

BATOCERA_BLUETOOTH_STACK=

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1)$(BR2_PACKAGE_BATOCERA_TARGET_RPI2)$(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	BATOCERA_BLUETOOTH_STACK=bcm921 piscan
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	BATOCERA_BLUETOOTH_STACK=rfkreset rtk115
endif

define BATOCERA_BLUETOOTH_INSTALL_TARGET_CMDS
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-bluetooth/S32bluetooth.template $(TARGET_DIR)/etc/init.d/S32bluetooth
	sed -i -e s+"@INTERNAL_BLUETOOTH_STACK@"+"$(BATOCERA_BLUETOOTH_STACK)"+ $(TARGET_DIR)/etc/init.d/S32bluetooth
endef

$(eval $(generic-package))
