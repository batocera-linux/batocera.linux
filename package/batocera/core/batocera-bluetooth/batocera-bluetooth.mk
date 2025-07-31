################################################################################
#
# batocera-bluetooth
#
################################################################################

BATOCERA_BLUETOOTH_VERSION = 2.4
BATOCERA_BLUETOOTH_LICENSE = GPL
BATOCERA_BLUETOOTH_SOURCE=

BATOCERA_BLUETOOTH_STACK=

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
    BATOCERA_BLUETOOTH_STACK=bcm921 piscan
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y) # tinkerboard only ??
    BATOCERA_BLUETOOTH_STACK=rfkreset rtk115
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
    BATOCERA_BLUETOOTH_STACK=rfkreset bcm150
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H6)$(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
    BATOCERA_BLUETOOTH_STACK=rfkreset sprd
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2),y)
    BATOCERA_BLUETOOTH_STACK=kvim4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_T527),y)
    BATOCERA_BLUETOOTH_STACK=bcm4345c5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3568),y)
    BATOCERA_BLUETOOTH_STACK=bcm4345c0
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    BATOCERA_BLUETOOTH_STACK=aic8800
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO),y)
    BATOCERA_BLUETOOTH_STACK=syn43711a0
endif

define BATOCERA_BLUETOOTH_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/etc/init.d/
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-bluetooth/S29namebluetooth \
        $(TARGET_DIR)/etc/init.d/S29namebluetooth
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-bluetooth/S32bluetooth.template \
        $(TARGET_DIR)/etc/init.d/S32bluetooth
    sed -i -e s+"@INTERNAL_BLUETOOTH_STACK@"+"$(BATOCERA_BLUETOOTH_STACK)"+ \
        $(TARGET_DIR)/etc/init.d/S32bluetooth
endef

$(eval $(generic-package))
