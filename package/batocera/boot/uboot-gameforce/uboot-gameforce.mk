################################################################################
#
# uboot files for gameforce chi
#
################################################################################

UBOOT_GAMEFORCE_VERSION = 3f696081df4f44ef2ccfe2d7033889607bb7dd45
UBOOT_GAMEFORCE_SITE = $(call github,shantigilbert,u-boot,$(UBOOT_GAMEFORCE_VERSION))
UBOOT_GAMEFORCE_LICENSE = GPLv2

UBOOT_GAMEFORCE_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_GAMEFORCE_BUILD_CMDS
    cd $(@D) && $(@D)/make.sh odroidgoa
endef

define UBOOT_GAMEFORCE_INSTALL_TARGET_CMDS
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
