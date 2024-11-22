################################################################################
#
# uboot-odroid-m1s
#
################################################################################

UBOOT_ODROID_M1S_VERSION = 2024.07
UBOOT_ODROID_M1S_SOURCE =

define UBOOT_ODROID_M1S_BUILD_CMDS
endef

define UBOOT_ODROID_M1S_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-odroid-m1s
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-odroid-m1s/u-boot-rockchip.bin \
	    $(BINARIES_DIR)/uboot-odroid-m1s/u-boot-rockchip.bin
endef

$(eval $(generic-package))
