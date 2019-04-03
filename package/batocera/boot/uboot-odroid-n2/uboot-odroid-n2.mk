################################################################################
#
# uboot files for odroid n2
#
################################################################################

UBOOT_ODROID_N2_VERSION = 1.0
UBOOT_ODROID_N2_SOURCE = u-boot-odroidn2-1.tar.gz
UBOOT_ODROID_N2_SITE = https://github.com/hardkernel/u-boot/releases/download/travis%2Fodroidn2-1

define UBOOT_ODROID_N2_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin $(BINARIES_DIR)/u-boot.bin
endef

$(eval $(generic-package))
