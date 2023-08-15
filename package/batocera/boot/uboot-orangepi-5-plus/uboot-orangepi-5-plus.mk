################################################################################
#
# uboot files for OrangePi 5 Plus
#
################################################################################

UBOOT_ORANGEPI_5_PLUS_VERSION = 2017.09
UBOOT_ORANGEPI_5_PLUS_SOURCE =

define UBOOT_ORANGEPI_5_PLUS_BUILD_CMDS
endef

define UBOOT_ORANGEPI_5_PLUS_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5-plus
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-plus/idbloader.img $(BINARIES_DIR)/uboot-orangepi-5-plus/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-plus/u-boot.itb $(BINARIES_DIR)/uboot-orangepi-5-plus/u-boot.itb
endef

$(eval $(generic-package))
