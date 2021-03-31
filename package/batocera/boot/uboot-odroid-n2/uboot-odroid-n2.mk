################################################################################
#
# uboot files for odroid n2
#
################################################################################
# Version.: Commits on Mar 28, 2020
UBOOT_ODROID_N2_VERSION = 141
UBOOT_ODROID_N2_SOURCE = u-boot-odroidn2-$(UBOOT_ODROID_N2_VERSION).tar.gz
UBOOT_ODROID_N2_SITE = https://github.com/hardkernel/u-boot/releases/download/travis%2Fodroidn2-$(UBOOT_ODROID_N2_VERSION)

define UBOOT_ODROID_N2_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin $(BINARIES_DIR)/u-boot-odroidn2.bin
endef

$(eval $(generic-package))
