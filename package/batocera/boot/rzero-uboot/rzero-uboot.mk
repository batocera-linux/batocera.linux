################################################################################
#
# Raxda-zero-uboot
#
################################################################################

RZERO_UBOOT_VERSION = 895299bd84b0a5782851d0f142cc3aa686dc5a95
RZERO_UBOOT_SITE = https://github.com/Multi-Retropie/rzero-uboot.git
RZERO_UBOOT_SITE_METHOD=git

define _UBOOT_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin.sd.bin $(BINARIES_DIR)/u-boot.bin.sd.bin
endef

$(eval $(generic-package))
