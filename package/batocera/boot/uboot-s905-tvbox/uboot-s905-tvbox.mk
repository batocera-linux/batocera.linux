################################################################################
#
# uboot files for s905 tv boxes
#
################################################################################
UBOOT_S905_TVBOX_VERSION = 2021.04
UBOOT_S905_TVBOX_SOURCE = $(UBOOT_S905_TVBOX_VERSION).tar.gz
UBOOT_S905_TVBOX_SITE = https://github.com/batocera-linux/uboot-s905-tvbox/archive/refs/tags

define UBOOT_S905_TVBOX_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/s905-tvbox/
	cp $(@D)/* $(BINARIES_DIR)/s905-tvbox/
endef

$(eval $(generic-package))
