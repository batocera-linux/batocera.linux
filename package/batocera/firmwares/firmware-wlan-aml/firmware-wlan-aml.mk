################################################################################
#
# firmware-wlan-aml
#
################################################################################
# Version.: Commits on Dec 5, 2022
FIRMWARE_WLAN_AML_VERSION = 528134d76f87bdd39d6f1ab27d20f28f1759434e
FIRMWARE_WLAN_AML_SITE = $(call github,LibreELEC,brcmfmac_sdio-firmware,$(FIRMWARE_WLAN_AML_VERSION))
FIRMWARE_WLAN_AML_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_WLAN_AML_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_WLAN_AML_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_WLAN_AML_TARGET_DIR)
	cp -r $(@D)/* $(FIRMWARE_WLAN_AML_TARGET_DIR)/
endef

$(eval $(generic-package))
