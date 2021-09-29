################################################################################
#
# Raxda-zero-uboot
#
################################################################################

RZERO_UBOOT_VERSION = 0008019abdd487e75c094b01a09d128c3e2358fb
RZERO_UBOOT_SITE = https://github.com/Multi-Retropie/rzero-uboot.git
RZERO_UBOOT_SITE_METHOD=git

define RZERO_UBOOT_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin $(BINARIES_DIR)/u-boot.bin
	cp $(@D)/u-boot.bin.sd.bin $(BINARIES_DIR)/u-boot.bin.sd.bin
endef

$(eval $(generic-package))
