################################################################################
#
# uboot-orangepi-5-plus
#
################################################################################

UBOOT_ORANGEPI_5_PLUS_VERSION = 1.2.0
UBOOT_ORANGEPI_5_PLUS_SOURCE =

define UBOOT_ORANGEPI_5_PLUS_BUILD_CMDS
endef

UBOOT_ORANGEPI_5_PLUS_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-plus

define UBOOT_ORANGEPI_5_PLUS_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5-plus
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-plus/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5-plus/idbloader.img
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-plus/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-5-plus/u-boot.itb
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-plus/rkspi_loader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5-plus/rkspi_loader.img
endef

$(eval $(generic-package))
