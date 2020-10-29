################################################################################
#
# uboot files for odroid xu4
#
################################################################################

UBOOT_ODROID_XU4_VERSION = odroidxu4-v2017.05
UBOOT_ODROID_XU4_SITE = https://github.com/hardkernel/u-boot.git
UBOOT_ODROID_XU4_SITE_METHOD=git

define UBOOT_ODROID_XU4_INSTALL_TARGET_CMDS
	cp $(@D)/sd_fuse/bl1.bin.hardkernel            $(BINARIES_DIR)/bl1.bin.hardkernel
	cp $(@D)/sd_fuse/bl2.bin.hardkernel.720k_uboot $(BINARIES_DIR)/bl2.bin.hardkernel.720k_uboot
	cp $(@D)/sd_fuse/tzsw.bin.hardkernel           $(BINARIES_DIR)/tzsw.bin.hardkernel
	#cp $(@D)/sd_fuse/u-boot.bin.hardkernel         $(BINARIES_DIR)/u-boot.bin.hardkernel
endef

$(eval $(generic-package))
