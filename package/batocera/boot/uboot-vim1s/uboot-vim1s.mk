################################################################################
#
# uboot files for VIM1S
#
################################################################################

UBOOT_VIM1S_VERSION = 2019.01
UBOOT_VIM1S_SOURCE =

define UBOOT_VIM1S_BUILD_CMDS
endef

define UBOOT_VIM1S_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-vim1s/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-vim1s/u-boot.bin.sd.bin.signed $(BINARIES_DIR)/uboot-vim1s/u-boot.bin.sd.signed
endef

$(eval $(generic-package))
