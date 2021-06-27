################################################################################
#
# uboot files for gameforce chi
#
################################################################################

UBOOT_GAMEFORCE_CHI_VERSION = 0e62bf71de07078bf4c5b46af525472f4cc4df73
UBOOT_GAMEFORCE_CHI_SITE = https://github.com/batocera-linux/gameforce-uboot
UBOOT_GAMEFORCE_CHI_SITE_METHOD=git

UBOOT_GAMEFORCE_CHI_DEPENDENCIES = host-toolchain-optional-linaro-aarch64

define UBOOT_GAMEFORCE_CHI_BUILD_CMDS
        cd $(@D) && $(@D)/make.sh odroidgo2
endef

define UBOOT_GAMEFORCE_CHI_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/gameforce
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/gameforce/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/gameforce/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/gameforce/trust.img
endef

$(eval $(generic-package))
