################################################################################
#
# uboot files for evb-rk3399 (Generic RK3399 board)
#
################################################################################

UBOOT_EVB_RK3399_VERSION = 1.0
UBOOT_EVB_RK3399_SOURCE =

define UBOOT_EVB_RK3399_BUILD_CMDS
endef

define UBOOT_EVB_RK3399_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-evb-rk3399
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-evb-rk3399/idbloader.img $(BINARIES_DIR)/uboot-evb-rk3399/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-evb-rk3399/uboot.img $(BINARIES_DIR)/uboot-evb-rk3399/uboot.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-evb-rk3399/trust.img $(BINARIES_DIR)/uboot-evb-rk3399/trust.img
endef

$(eval $(generic-package))
