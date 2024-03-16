################################################################################
#
# uboot files for OrangePi 800
#
################################################################################

UBOOT_ORANGEPI_800_VERSION = 2024.03.16
UBOOT_ORANGEPI_800_SOURCE =

define UBOOT_ORANGEPI_800_BUILD_CMDS
endef

define UBOOT_ORANGEPI_800_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-800
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-800/idbloader.img $(BINARIES_DIR)/uboot-orangepi-800/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-800/u-boot.itb $(BINARIES_DIR)/uboot-orangepi-800/u-boot.itb
endef

$(eval $(generic-package))
