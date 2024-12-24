################################################################################
#
# firmware-orangepi
#
################################################################################
# Version: Commits on Oct 9, 2024
FIRMWARE_ORANGEPI_VERSION = 75ea6fc5f3c454861b39b33823cb6876f3eca598
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI_TARGET_DIR)
	cp -a $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)/
endef

$(eval $(generic-package))
