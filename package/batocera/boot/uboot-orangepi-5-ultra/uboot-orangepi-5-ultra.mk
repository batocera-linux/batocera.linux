################################################################################
#
# uboot-orangepi-5-ultra
#
################################################################################

UBOOT_ORANGEPI_5_ULTRA_VERSION = 1.0.0
UBOOT_ORANGEPI_5_ULTRA_SOURCE =

define UBOOT_ORANGEPI_5_ULTRA_BUILD_CMDS
endef

define UBOOT_ORANGEPI_5_ULTRA_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5-ultra
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-ultra/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5-ultra/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-ultra/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-5-ultra/u-boot.itb
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-ultra/rkspi_loader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5-ultra/rkspi_loader.img
endef

$(eval $(generic-package))
