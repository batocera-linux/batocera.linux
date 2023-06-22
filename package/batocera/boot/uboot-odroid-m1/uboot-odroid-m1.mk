################################################################################
#
# uboot files for HardKernel ODROID M1
#
################################################################################

UBOOT_ODROID_M1_VERSION = 1.0
UBOOT_ODROID_M1_SOURCE =

define UBOOT_ODROID_M1_BUILD_CMDS
endef

define UBOOT_ODROID_M1_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-odroid-m1
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-odroid-m1/idbloader.img $(BINARIES_DIR)/uboot-odroid-m1/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-odroid-m1/u-boot.itb $(BINARIES_DIR)/uboot-odroid-m1/u-boot.itb
endef

$(eval $(generic-package))
