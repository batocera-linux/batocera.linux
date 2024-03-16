################################################################################
#
# uboot files for Hugsun X99 TV Box
#
################################################################################

UBOOT_HUGSUN_X99_VERSION = 1.0
UBOOT_HUGSUN_X99_SOURCE =

define UBOOT_HUGSUN_X99_BUILD_CMDS
endef

define UBOOT_HUGSUN_X99_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-hugsun-x99
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-hugsun-x99/idbloader.bin $(BINARIES_DIR)/uboot-hugsun-x99/idbloader.bin
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-hugsun-x99/uboot.img $(BINARIES_DIR)/uboot-hugsun-x99/uboot.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-hugsun-x99/trust.bin $(BINARIES_DIR)/uboot-hugsun-x99/trust.bin
endef

$(eval $(generic-package))
