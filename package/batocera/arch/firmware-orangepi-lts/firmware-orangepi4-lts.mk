################################################################################
#
# firmware-orangepi-lts
#
################################################################################
#Version: Commits on Sep 29, 2022
FIRMWARE_ORANGEPI_LTS_VERSION = 4159bc34f3f6a25732fe59e3d92e6658f17e45ce
FIRMWARE_ORANGEPI_LTS_SITE = $(call github,dmanlfc,opi4-lts-firmware,$(FIRMWARE_ORANGEPI_LTS_VERSION))

FIRMWARE_ORANGEPI_LTS_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI_LTS_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI_LTS_TARGET_DIR)
	cp -r $(@D)/*.bin $(FIRMWARE_ORANGEPI_LTS_TARGET_DIR)/
	cp -r $(@D)/*.ini $(FIRMWARE_ORANGEPI_LTS_TARGET_DIR)/
	$(INSTALL) -D -m 0755 $(@D)/hciattach_opi $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
