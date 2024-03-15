################################################################################
#
# uboot files for ROCK 3C
#
################################################################################

UBOOT_ROCK_3C_VERSION = 2023.07.02
UBOOT_ROCK_3C_SOURCE =

define UBOOT_ROCK_3C_BUILD_CMDS
endef

define UBOOT_ROCK_3C_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-rock-3c
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock-3c/idbloader.img $(BINARIES_DIR)/uboot-rock-3c/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock-3c/u-boot.itb $(BINARIES_DIR)/uboot-rock-3c/u-boot.itb
endef

$(eval $(generic-package))
