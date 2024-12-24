################################################################################
#
# uboot-orangepi-4a
#
################################################################################

UBOOT_ORANGEPI_4A_VERSION = v2018.05-t527
UBOOT_ORANGEPI_4A_SOURCE =

define UBOOT_ORANGEPI_4A_BUILD_CMDS
endef

define UBOOT_ORANGEPI_4A_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-4a
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-4a/boot0_sdcard.fex \
	    $(BINARIES_DIR)/uboot-orangepi-4a/boot0_sdcard.fex
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-4a/boot_package.fex \
	    $(BINARIES_DIR)/uboot-orangepi-4a/boot_package.fex
endef

$(eval $(generic-package))
