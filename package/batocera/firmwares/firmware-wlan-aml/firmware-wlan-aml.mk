################################################################################
#
# firmware-wlan-aml
#
################################################################################
# Version.: Commits on Feb 10, 2023
FIRMWARE_WLAN_AML_VERSION = c70355f9ec6d015b91a5c3199aa08b433e2f7caf
FIRMWARE_WLAN_AML_SITE = $(call github,LibreELEC,brcmfmac_sdio-firmware,$(FIRMWARE_WLAN_AML_VERSION))
FIRMWARE_WLAN_AML_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_WLAN_AML_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_WLAN_AML_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_WLAN_AML_TARGET_DIR)
	cp -r $(@D)/* $(FIRMWARE_WLAN_AML_TARGET_DIR)/
endef

$(eval $(generic-package))
