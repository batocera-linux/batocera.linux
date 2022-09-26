################################################################################
#
# firmware-orangepi
#
################################################################################
# Version.: Commits on Sep 6, 2022
FIRMWARE_ORANGEPI_VERSION = 70accf15b75b9a603920f0a8fda45d1739fd410c
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))
FIRMWARE_ORANGEPI_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	cp -r $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)
endef

$(eval $(generic-package))
