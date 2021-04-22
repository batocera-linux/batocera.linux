################################################################################
#
# uboot files for odroid go advance
#
################################################################################

UBOOT_ODROID_GOA_VERSION = 0e26e35cb18a80005b7de45c95858c86a2f7f41e
UBOOT_ODROID_GOA_SITE = https://github.com/hardkernel/u-boot.git
UBOOT_ODROID_GOA_SITE_METHOD=git

UBOOT_ODROID_GOA_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_ODROID_GOA_BUILD_CMDS
        cd $(@D) && $(@D)/make.sh odroidgoa
endef

define UBOOT_ODROID_GOA_INSTALL_TARGET_CMDS
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
