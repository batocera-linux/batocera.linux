################################################################################
#
# BATOCERA BLUETOOTH
#
################################################################################

BATOCERA_BLUETOOTH_VERSION = 2
BATOCERA_BLUETOOTH_LICENSE = GPL
BATOCERA_BLUETOOTH_SOURCE=

BATOCERA_BLUETOOTH_STACK=

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI_GLES2),y) # all but RPi4
	BATOCERA_BLUETOOTH_STACK=bcm921 piscan
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y) # tinkerboard only ??
	BATOCERA_BLUETOOTH_STACK=rfkreset rtk115
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_BLUETOOTH_STACK=rfkreset bcm150
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_3_LTS)$(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2),y)
	BATOCERA_BLUETOOTH_STACK=rfkreset sprd
endif

define BATOCERA_BLUETOOTH_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/init.d/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-bluetooth/S32bluetooth.template $(TARGET_DIR)/etc/init.d/S32bluetooth
	sed -i -e s+"@INTERNAL_BLUETOOTH_STACK@"+"$(BATOCERA_BLUETOOTH_STACK)"+ $(TARGET_DIR)/etc/init.d/S32bluetooth
endef

$(eval $(generic-package))
