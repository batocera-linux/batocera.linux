################################################################################
#
# Raxda-zero-uboot
#
################################################################################

RZERO_UBOOT_VERSION = def48de7f399d407f1f61615d5e738220216ce83
RZERO_UBOOT_SITE = https://github.com/Multi-Retropie/rzero-uboot.git
RZERO_UBOOT_SITE_METHOD=git

define RZERO_UBOOT_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin $(BINARIES_DIR)/u-boot.bin
	cp $(@D)/u-boot.bin.sd.bin $(BINARIES_DIR)/u-boot.bin.sd.bin
endef

$(eval $(generic-package))
