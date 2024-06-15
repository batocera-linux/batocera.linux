################################################################################
#
# uboot-rock-5c
#
################################################################################

UBOOT_ROCK_5C_VERSION = 2024.03
UBOOT_ROCK_5C_SOURCE =

define UBOOT_ROCK_5C_BUILD_CMDS
endef

define UBOOT_ROCK_5C_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rock-5c
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock-5c/idbloader.img \
	    $(BINARIES_DIR)/rock-5c/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock-5c/u-boot.itb \
	    $(BINARIES_DIR)/rock-5c/u-boot.itb
endef

$(eval $(generic-package))
