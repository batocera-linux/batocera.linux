################################################################################
#
# uboot-orangepi-5b
#
################################################################################

UBOOT_ORANGEPI_5B_VERSION = 1.0.8
UBOOT_ORANGEPI_5B_SOURCE =

define UBOOT_ORANGEPI_5B_BUILD_CMDS
endef

define UBOOT_ORANGEPI_5B_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5b
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5b/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5b/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5b/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-5b/u-boot.itb
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5b/rkspi_loader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5b/rkspi_loader.img
endef

$(eval $(generic-package))
