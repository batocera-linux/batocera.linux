################################################################################
#
# uboot files for odroid go advance
#
################################################################################

UBOOT_ODROID_GOA_VERSION = e7b255b54c42c8a805dee7a9409a8838cfa13586
UBOOT_ODROID_GOA_SITE = https://github.com/hardkernel/u-boot.git
UBOOT_ODROID_GOA_SITE_METHOD=git

UBOOT_ODROID_GOA_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_ODROID_GOA_BUILD_CMDS
        cd $(@D) && $(@D)/make.sh odroidgo2
endef

define UBOOT_ODROID_GOA_INSTALL_TARGET_CMDS
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
