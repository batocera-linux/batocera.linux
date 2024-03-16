################################################################################
#
# uboot files for Rock960
#
################################################################################

UBOOT_ROCK960_VERSION = 1.0
UBOOT_ROCK960_SOURCE =

define UBOOT_ROCK960_BUILD_CMDS
endef

define UBOOT_ROCK960_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-rock960
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock960/idbloader.img $(BINARIES_DIR)/uboot-rock960/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock960/uboot.img $(BINARIES_DIR)/uboot-rock960/uboot.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-rock960/trust.img $(BINARIES_DIR)/uboot-rock960/trust.img
endef

$(eval $(generic-package))
