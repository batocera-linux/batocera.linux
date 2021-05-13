################################################################################
#
# uboot files for Anbernic RG351V
#
################################################################################

UBOOT_RG351V_VERSION = 3fb31d92d27704fd3cd40053d5ef20469133a8bd
UBOOT_RG351V_SITE = https://github.com/batocera-linux/RG351V_uboot
UBOOT_RG351V_SITE_METHOD=git

UBOOT_RG351V_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_RG351V_BUILD_CMDS
        cd $(@D) && $(@D)/make.sh odroidgo2
endef

define UBOOT_RG351V_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rg351v
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/rg351v/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/rg351v/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/rg351v/trust.img
endef

$(eval $(generic-package))
