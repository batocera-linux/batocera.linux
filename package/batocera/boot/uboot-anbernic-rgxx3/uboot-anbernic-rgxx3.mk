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
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-anbernic-rgxx3/idbloader.img $(BINARIES_DIR)/uboot-anbernic-rgxx3/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-anbernic-rgxx3/uboot.img $(BINARIES_DIR)/uboot-anbernic-rgxx3/uboot.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-anbernic-rgxx3/resource.img $(BINARIES_DIR)/uboot-anbernic-rgxx3/resource.img
endef

$(eval $(generic-package))
