################################################################################
#
# firmware-orangepi-lts
#
################################################################################

FIRMWARE_ORANGEPI_LTS_VERSION = fed041f02d02c5e257d033db2144bfc1c7f5e91e
FIRMWARE_ORANGEPI_LTS_SITE = $(call github,dmanlfc,opi4-lts-firmware,$(FIRMWARE_ORANGEPI_LTS_VERSION))

FIRMWARE_ORANGEPI_LTS_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI_LTS_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI_LTS_TARGET_DIR)
	cp -r $(@D)/*.bin $(FIRMWARE_ORANGEPI_LTS_TARGET_DIR)/
	cp -r $(@D)/*.ini $(FIRMWARE_ORANGEPI_LTS_TARGET_DIR)/
	$(INSTALL) -D -m 0755 $(@D)/hciattach_opi $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
