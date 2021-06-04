################################################################################
#
# uboot files for odroid c2
#
################################################################################
UBOOT_ODROID_C2_VERSION = 2021.04
UBOOT_ODROID_C2_SOURCE = $(UBOOT_ODROID_C2_VERSION).tar.gz
UBOOT_ODROID_C2_SITE = https://github.com/batocera-linux/uboot-odroid-c2/archive/refs/tags

define UBOOT_ODROID_C2_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/odroid-c2/
	cp $(@D)/* $(BINARIES_DIR)/odroid-c2/
endef

$(eval $(generic-package))
