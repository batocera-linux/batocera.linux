################################################################################
#
# firmware-wlan-aml
#
################################################################################
# Version.: Commits on Jan 15, 2023
FIRMWARE_WLAN_AML_VERSION = 59fe14f8f4d5c06ab5d7a5244ced4036509adfbe
FIRMWARE_WLAN_AML_SITE = $(call github,LibreELEC,brcmfmac_sdio-firmware,$(FIRMWARE_WLAN_AML_VERSION))
FIRMWARE_WLAN_AML_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_WLAN_AML_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_WLAN_AML_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_WLAN_AML_TARGET_DIR)
	cp -r $(@D)/* $(FIRMWARE_WLAN_AML_TARGET_DIR)/
endef

$(eval $(generic-package))
