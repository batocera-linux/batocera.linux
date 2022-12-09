################################################################################
#
# firmware-wlan-aml
#
################################################################################
# Version.: Commits on Apr 18, 2022
FIRMWARE_WLAN_AML_VERSION = 1da9185bddb6ec3c975f5739335e7e23b7e2b6d0
FIRMWARE_WLAN_AML_SITE = $(call github,LibreELEC,brcmfmac_sdio-firmware,$(FIRMWARE_WLAN_AML_VERSION))
FIRMWARE_WLAN_AML_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_WLAN_AML_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_WLAN_AML_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_WLAN_AML_TARGET_DIR)
	cp -r $(@D)/* $(FIRMWARE_WLAN_AML_TARGET_DIR)/
endef

$(eval $(generic-package))
