################################################################################
#
# firmware-orangepi4-lts
#
################################################################################

FIRMWARE_ORANGEPI4_LTS_VERSION = fce535aa55bda4f96631a3c9257f7361a7008f6b
FIRMWARE_ORANGEPI4_LTS_SITE = $(call github,dmanlfc,opi4-lts-firmware,$(FIRMWARE_ORANGEPI4_LTS_VERSION))

FIRMWARE_ORANGEPI4_LTS_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI4_LTS_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)
	cp -r $(@D)/*.bin $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
	cp -r $(@D)/*.ini $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
endef

$(eval $(generic-package))
