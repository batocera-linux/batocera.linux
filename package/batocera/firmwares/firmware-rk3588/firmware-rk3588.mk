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
endef

$(eval $(generic-package))
