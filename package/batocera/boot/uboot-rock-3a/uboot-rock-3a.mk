################################################################################
#
# uboot files for ROCK 3A
#
################################################################################

UBOOT_ROCK_3A_VERSION = 2023.07.02
UBOOT_ROCK_3A_SOURCE =

define UBOOT_ROCK_3A_BUILD_CMDS
endef

define UBOOT_ROCK_3A_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-rock-3a
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock-3a/idbloader.img $(BINARIES_DIR)/uboot-rock-3a/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock-3a/u-boot.itb $(BINARIES_DIR)/uboot-rock-3a/u-boot.itb
endef

$(eval $(generic-package))
