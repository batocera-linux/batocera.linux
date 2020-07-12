################################################################################
#
# tritium-h5-uboot
#
################################################################################

UBOOT_TRITIUM_H5_VERSION = c3fc0e2e2fee03ea7398f01ef7a84eed258d2489
UBOOT_TRITIUM_H5_SITE = https://github.com/Multi-Retropie/tritium-h5.git
UBOOT_TRITIUM_H5_SITE_METHOD=git

define UBOOT_TRITIUM_H5_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot-sunxi-with-spl.bin $(BINARIES_DIR)/
endef

$(eval $(generic-package))
