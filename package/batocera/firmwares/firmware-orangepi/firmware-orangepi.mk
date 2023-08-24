################################################################################
#
# firmware-orangepi
#
################################################################################
# Version.: Commits on Jun 2, 2023
FIRMWARE_ORANGEPI_VERSION = d9c6dac6d934bd5923be573e99aac767681f2ca5
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI_TARGET_DIR)
	cp -a $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)/
endef

$(eval $(generic-package))
