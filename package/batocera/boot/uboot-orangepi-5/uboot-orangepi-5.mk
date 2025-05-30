################################################################################
#
# uboot-orangepi-5
#
################################################################################

UBOOT_ORANGEPI_5_VERSION = 1.1.8
UBOOT_ORANGEPI_5_SOURCE =

define UBOOT_ORANGEPI_5_BUILD_CMDS
endef

define UBOOT_ORANGEPI_5_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-5/u-boot.itb
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5/rkspi_loader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5/rkspi_loader.img
endef

$(eval $(generic-package))
