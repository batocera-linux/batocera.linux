################################################################################
#
# uboot files for VIM4
#
################################################################################

UBOOT_VIM4_VERSION = 2019.01
UBOOT_VIM4_SOURCE =

define UBOOT_VIM4_BUILD_CMDS
endef

define UBOOT_VIM4_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-vim4/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-vim4/u-boot.bin.sd.bin.signed $(BINARIES_DIR)/uboot-vim4/u-boot.bin.sd.signed
endef

$(eval $(generic-package))
