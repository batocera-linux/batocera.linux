################################################################################
#
# firmware-wlan-aml
#
################################################################################

FIRMWARE_WLAN_AML_VERSION = 6d49ff1bc15a1c55f711292ed22a7687fa2c9e14
FIRMWARE_WLAN_AML_SITE = $(call github,libreelec,brcmfmac_sdio-firmware,$(FIRMWARE_WLAN_AML_VERSION))

FIRMWARE_WLAN_AML_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_WLAN_AML_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_WLAN_AML_TARGET_DIR)


# AP6212
	cp -r $(@D)/BCM43438A1.hcd			$(FIRMWARE_WLAN_AML_TARGET_DIR)/
	cp -r $(@D)/brcmfmac43430-sdio.bin		$(FIRMWARE_WLAN_AML_TARGET_DIR)/
	cp -r $(@D)/brcmfmac43430-sdio.txt		$(FIRMWARE_WLAN_AML_TARGET_DIR)/

# AP6330
  	cp -r $(@D)/BCM4330B1.hcd			$(FIRMWARE_WLAN_AML_TARGET_DIR)/
  	cp -r $(@D)/brcmfmac4330-sdio.bin		$(FIRMWARE_WLAN_AML_TARGET_DIR)/
  	cp -r $(@D)/brcmfmac4330-sdio.txt		$(FIRMWARE_WLAN_AML_TARGET_DIR)/

# AP6335
  	cp -r $(@D)/BCM4335C0.hcd			$(FIRMWARE_WLAN_AML_TARGET_DIR)/
  	cp -r $(@D)/brcmfmac4339-sdio.bin		$(FIRMWARE_WLAN_AML_TARGET_DIR)/
  	cp -r $(@D)/brcmfmac4339-sdio.txt		$(FIRMWARE_WLAN_AML_TARGET_DIR)/

# AP6359
  	cp -r $(@D)/BCM4359C0.hcd			$(FIRMWARE_WLAN_AML_TARGET_DIR)/
  	cp -r $(@D)/brcmfmac4359-sdio.bin		$(FIRMWARE_WLAN_AML_TARGET_DIR)/
  	cp -r $(@D)/brcmfmac4359-sdio.txt		$(FIRMWARE_WLAN_AML_TARGET_DIR)/


endef


$(eval $(generic-package))
