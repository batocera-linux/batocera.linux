################################################################################
#
# firmware-orangepi
#
################################################################################
# Version.: Commits on Feb 20, 2023
FIRMWARE_ORANGEPI_VERSION = 79186949b2fbd01c52d55f085106b96dfd670ff6
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))
FIRMWARE_ORANGEPI_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	cp -r $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)
endef

$(eval $(generic-package))
