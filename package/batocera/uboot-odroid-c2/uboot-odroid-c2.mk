################################################################################
#
# odroidc2-uboot
#
################################################################################

UBOOT_ODROID_C2_VERSION = 1.0.0
UBOOT_ODROID_C2_SOURCE = batocera-odroidc2-uboot-$(UBOOT_ODROID_C2_VERSION).tar.gz
UBOOT_ODROID_C2_SITE = https://github.com/batocera-linux/batocera-odroidc2-uboot/releases/download/$(UBOOT_ODROID_C2_VERSION)

define UBOOT_ODROID_C2_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin         $(BINARIES_DIR)/u-boot.bin
	cp $(@D)/bl1.bin.hardkernel $(BINARIES_DIR)/bl1.bin.hardkernel
endef

$(eval $(generic-package))
