################################################################################
#
# uboot-orangepi-5-pro
#
################################################################################

UBOOT_ORANGEPI_5_PRO_VERSION = 2017.09
UBOOT_ORANGEPI_5_PRO_SOURCE =

define UBOOT_ORANGEPI_5_PRO_BUILD_CMDS
endef

define UBOOT_ORANGEPI_5_PRO_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-5-pro
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-pro/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-5-pro/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-5-pro/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-5-pro/u-boot.itb
endef

$(eval $(generic-package))
