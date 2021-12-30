################################################################################
#
# firmware-wlan-aml
#
################################################################################
# Version.: Commits on Dec 16, 2021
FIRMWARE_WLAN_AML_VERSION = 371e416064e9bf8f0f173ce94de17981b6503f71
FIRMWARE_WLAN_AML_SITE = $(call github,LibreELEC,brcmfmac_sdio-firmware,$(FIRMWARE_WLAN_AML_VERSION))

FIRMWARE_WLAN_AML_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_WLAN_AML_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_WLAN_AML_TARGET_DIR)
	cp -r $(@D)/* $(FIRMWARE_WLAN_AML_TARGET_DIR)/
endef

$(eval $(generic-package))
