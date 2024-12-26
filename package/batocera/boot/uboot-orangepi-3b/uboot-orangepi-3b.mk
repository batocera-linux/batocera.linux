################################################################################
#
# uboot-orangepi-3b
#
################################################################################

UBOOT_ORANGEPI_3B_VERSION = v2017.09
UBOOT_ORANGEPI_3B_SOURCE =

define UBOOT_ORANGEPI_3B_BUILD_CMDS
endef

define UBOOT_ORANGEPI_3B_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-3b
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-3b/idbloader.img \
	    $(BINARIES_DIR)/uboot-orangepi-3b/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-3b/u-boot.itb \
	    $(BINARIES_DIR)/uboot-orangepi-3b/u-boot.itb
endef

$(eval $(generic-package))
