################################################################################
#
# uboot-orangepi-5-ultra
#
################################################################################

UBOOT_ORANGEPI_5_ULTRA_VERSION = 2017.09
UBOOT_ORANGEPI_5_ULTRA_SOURCE =

define UBOOT_ORANGEPI_5_ULTRA_BUILD_CMDS
endef

define UBOOT_ORANGEPI_5_ULTRA_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5-ultra
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-ultra/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5-ultra/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-ultra/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-5-ultra/u-boot.itb
endef

$(eval $(generic-package))
