################################################################################
#
# uboot files for X96 Mate
#
################################################################################

UBOOT_X96_MATE_VERSION = 1.0
UBOOT_X96_MATE_SOURCE =

define UBOOT_X96_MATE_BUILD_CMDS
endef

define UBOOT_X96_MATE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-x96-mate
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-x96-mate/u-boot-sunxi-with-spl.bin $(BINARIES_DIR)/uboot-x96-mate/u-boot-sunxi-with-spl.bin
endef

$(eval $(generic-package))
