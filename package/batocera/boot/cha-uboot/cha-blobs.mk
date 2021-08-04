################################################################################
#
# cha-uboot
#
################################################################################

CHA_UBOOT_VERSION = dc7940b2e8fd43099ef0f287a6564209938062cd
CHA_UBOOT_SITE = https://github.com/Multi-Retropie/cha-uboot.git
CHA_UBOOT_SITE_METHOD=git

define CHA_UBOOT_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot-sunxi-with-spl.bin $(BINARIES_DIR)/u-boot-sunxi-with-spl.bin
endef

$(eval $(generic-package))
