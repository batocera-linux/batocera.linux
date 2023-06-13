################################################################################
#
# uboot files for Anbernic RGXX3
#
################################################################################

UBOOT_ANBERNIC_RGXX3_VERSION = 1.0
UBOOT_ANBERNIC_RGXX3_SOURCE =

define UBOOT_ANBERNIC_RGXX3_BUILD_CMDS
endef

define UBOOT_ANBERNIC_RGXX3_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-anbernic-rgxx3
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-anbernic-rgxx3/u-boot-rockchip.bin $(BINARIES_DIR)/uboot-anbernic-rgxx3/u-boot-rockchip.bin
endef

$(eval $(generic-package))
