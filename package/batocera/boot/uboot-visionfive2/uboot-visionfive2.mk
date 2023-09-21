################################################################################
#
# uboot files for StarFive VisionFive 2
#
################################################################################

UBOOT_VISIONFIVE2_VERSION = 3.6.1
UBOOT_VISIONFIVE2_SOURCE =

define UBOOT_VISIONFIVE2_BUILD_CMDS
endef

define UBOOT_VISIONFIVE2_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-visionfive2
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-visionfive2/visionfive2_fw_payload.img $(BINARIES_DIR)/uboot-visionfive2/visionfive2_fw_payload.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-visionfive2/u-boot-spl.bin.normal.out $(BINARIES_DIR)/uboot-visionfive2/u-boot-spl.bin.normal.out
endef

$(eval $(generic-package))
