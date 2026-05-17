################################################################################
#
# uboot-odroid-m2
#
# Pre-built U-Boot binary from Armbian (v2025.10)
# Built with: BL31 v1.48 + DDR v1.18 from armbian/rkbin
# Building from source with Buildroot's toolchain produces binaries that
# cause SError kernel panics during paging_init on this board.
# Same pattern as uboot-odroid-m1.
#
################################################################################

UBOOT_ODROID_M2_VERSION = 1.0
UBOOT_ODROID_M2_SOURCE =

define UBOOT_ODROID_M2_BUILD_CMDS
endef

define UBOOT_ODROID_M2_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/odroid-m2
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-odroid-m2/u-boot-rockchip.bin \
	    $(BINARIES_DIR)/odroid-m2/u-boot-rockchip.bin
endef

$(eval $(generic-package))
