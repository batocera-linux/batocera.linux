################################################################################
#
# firmware-orangepi
#
################################################################################
# Version.: Commits on Jan 13, 2023
FIRMWARE_ORANGEPI_VERSION = 75747c7034b1136b4674269e248b69bf1a5e4039
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))
FIRMWARE_ORANGEPI_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	cp -r $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)
endef

$(eval $(generic-package))
