################################################################################
#
# firmware-rockpro64
#
################################################################################

FIRMWARE_ROCKPRO64_VERSION = 02b850257864982e2c2baf93ad1d932230386db7
FIRMWARE_ROCKPRO64_SITE = $(call github,kszaq,brcmfmac_sdio-firmware-aml,$(FIRMWARE_ROCKPRO64_VERSION))
FIRMWARE_ROCKPRO64_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_ROCKPRO64_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_ROCKPRO64_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ROCKPRO64_TARGET_DIR)
	cp -r $(@D)/firmware/brcm/nvram_ap6359sa.txt 	    $(FIRMWARE_ROCKPRO64_TARGET_DIR)/
	cp -r $(@D)/firmware/brcm/BCM4359C0.hcd      	    $(FIRMWARE_ROCKPRO64_TARGET_DIR)/
	cp -r $(@D)/firmware/brcm/fw_bcm4359c0_ag.bin       $(FIRMWARE_ROCKPRO64_TARGET_DIR)/
	cp -r $(@D)/firmware/brcm/fw_bcm4359c0_ag_apsta.bin $(FIRMWARE_ROCKPRO64_TARGET_DIR)/
endef

$(eval $(generic-package))
