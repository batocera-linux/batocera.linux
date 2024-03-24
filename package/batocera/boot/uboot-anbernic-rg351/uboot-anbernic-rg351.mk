################################################################################
#
# uboot files for anbernic RG351
#
################################################################################

UBOOT_ANBERNIC_RG351_VERSION = 3ae3501eb60160c60de065501f8da8a484433f3b
UBOOT_ANBERNIC_RG351_SITE = https://github.com/tonyjih/RG351-u-boot
UBOOT_ANBERNIC_RG351_SITE_METHOD=git

UBOOT_ANBERNIC_RG351_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_ANBERNIC_RG351_BUILD_CMDS
        cd $(@D) && $(@D)/make.sh odroidgoa
endef

define UBOOT_ANBERNIC_RG351_INSTALL_TARGET_CMDS
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
