################################################################################
#
# uboot files for Anbernic RG351P
#
################################################################################

UBOOT_RG351P_VERSION = 99113eeaa71a5c524c752096190ec5ab28c3720d
UBOOT_RG351P_SITE = https://github.com/batocera-linux/RG351P_u-boot
UBOOT_RG351P_SITE_METHOD=git

UBOOT_RG351P_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_RG351P_BUILD_CMDS
        cd $(@D) && $(@D)/make.sh odroidgo2
endef

define UBOOT_RG351P_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rg351p
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/rg351p/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/rg351p/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/rg351p/trust.img
endef

$(eval $(generic-package))
