################################################################################
#
# uboot files for tinkerboard
#
################################################################################
UBOOT_TINKERBOARD_VERSION = 2019.01
UBOOT_TINKERBOARD_SOURCE = $(UBOOT_TINKERBOARD_VERSION).tar.gz
UBOOT_TINKERBOARD_SITE = https://github.com/batocera-linux/uboot-tinkerboard/archive/refs/tags

define UBOOT_TINKERBOARD_INSTALL_TARGET_CMDS
	mkdir -p     $(BINARIES_DIR)/tinkerboard/
	cp $(@D)/*   $(BINARIES_DIR)/tinkerboard/
endef

$(eval $(generic-package))
