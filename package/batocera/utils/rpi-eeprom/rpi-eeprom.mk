################################################################################
#
# rpi-eeprom
#
################################################################################

RPI_EEPROM_VERSION = 3c822369bec71a2f10514994b6f491d8e2323f9e
RPI_EEPROM_SITE = $(call github,raspberrypi,rpi-eeprom,$(RPI_EEPROM_VERSION))
RPI_EEPROM_LICENSE = BSD-3-Clause
RPI_EEPROM_LICENSE_FILES = LICENCE

RPI_EEPROM_DEPENDENCIES = python3 binutils rpi-utils

define RPI_EEPROM_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    $(INSTALL) -m 0755 -D $(@D)/rpi-eeprom-config $(TARGET_DIR)/usr/bin/rpi-eeprom-config
    $(INSTALL) -m 0755 -D $(@D)/rpi-eeprom-update $(TARGET_DIR)/usr/bin/rpi-eeprom-update
	$(INSTALL) -m 0755 -D $(@D)/rpi-eeprom-digest $(TARGET_DIR)/usr/bin/rpi-eeprom-digest
    mkdir -p $(TARGET_DIR)/etc/default
    $(INSTALL) -m 0755 -D $(@D)/rpi-eeprom-update-default $(TARGET_DIR)/etc/default/rpi-eeprom-update
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
define RPI_EEPROM_INSTALL_BCM2711_FIRMWARE
    mkdir -p $(TARGET_DIR)/lib/firmware/raspberrypi/bootloader-2711/
    cp -af $(@D)/firmware-2711/* $(TARGET_DIR)/lib/firmware/raspberrypi/bootloader-2711/
endef
RPI_EEPROM_POST_INSTALL_TARGET_HOOKS += RPI_EEPROM_INSTALL_BCM2711_FIRMWARE
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
define RPI_EEPROM_INSTALL_BCM2712_FIRMWARE
    mkdir -p $(TARGET_DIR)/lib/firmware/raspberrypi/bootloader-2712/
    cp -af $(@D)/firmware-2712/* $(TARGET_DIR)/lib/firmware/raspberrypi/bootloader-2712/
endef
RPI_EEPROM_POST_INSTALL_TARGET_HOOKS += RPI_EEPROM_INSTALL_BCM2712_FIRMWARE
endif

$(eval $(generic-package))
