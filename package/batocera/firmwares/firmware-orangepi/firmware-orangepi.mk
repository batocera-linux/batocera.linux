################################################################################
#
# firmware-orangepi
#
################################################################################
# Version: Commits on Mar 19, 2025
FIRMWARE_ORANGEPI_VERSION = db5e86200ae592c467c4cfa50ec0c66cbc40b158
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))

# We have newer BT code
ifeq ($(BR2_PACKAGE_FIRMWARE_RADXA_RKWIFIBT),y)
FIRMWARE_ORANGEPI_DEPENDENCIES = firmware-radxa-rkwifibt
endif

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	rsync -a --checksum $(@D)/ $(TARGET_DIR)/lib/firmware/
endef

$(eval $(generic-package))
