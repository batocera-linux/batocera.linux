################################################################################
#
# ti-firmware
#
################################################################################

TI_FIRMWARE_VERSION = 1.0
TI_FIRMWARE_SOURCE =
TI_FIRMWARE_DEPENDENCIES = alllinuxfirmwares

TI_FIRMWARE_TARGET_DIR=$(TARGET_DIR)/lib/firmware/ti/tas2781/

define TI_FIRMWARE_INSTALL_TARGET_CMDS
	mkdir -p $(TI_FIRMWARE_TARGET_DIR)
	cp -a $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/ti-firmware/*.bin \
	    $(TI_FIRMWARE_TARGET_DIR)
endef

$(eval $(generic-package))
