################################################################################
#
# firmware-rk3588
#
################################################################################

FIRMWARE_RK3588_VERSION = dc92513ebf859d1213c999e44d4a7bf6a1fb04d7
FIRMWARE_RK3588_SITE = $(call github,stvhay,rk3588-firmware,$(FIRMWARE_RK3588_VERSION))
FIRMWARE_RK3588_DEPENDENCIES += alllinuxfirmwares 
FIRMWARE_RK3588_DEPENDENCIES += firmware-radxa-rkwifibt

FIRMWARE_RK3588_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_RK3588_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_RK3588_TARGET_DIR)/rtk_bt
	cp -v $(@D)/rtl8821cs_* $(FIRMWARE_RK3588_TARGET_DIR)/rtk_bt/
	# RTL8852BE BT & WiFi firmware files for Rockchip-linux 6.1.75
	$(INSTALL) -m 0644 -D $(FIRMWARE_RK3588_PKGDIR)/rtl8852bu/rtl8852bu_config.bin \
	    $(FIRMWARE_RK3588_TARGET_DIR)/rtl_bt/rtl8852bu_config.bin
	$(INSTALL) -m 0644 -D $(FIRMWARE_RK3588_PKGDIR)/rtl8852bu/rtl8852bu_fw.bin \
	    $(FIRMWARE_RK3588_TARGET_DIR)/rtl_bt/rtl8852bu_fw.bin
endef

$(eval $(generic-package))
