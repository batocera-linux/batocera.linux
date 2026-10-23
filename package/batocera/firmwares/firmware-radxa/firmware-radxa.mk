################################################################################
#
# firmware-radxa
#
################################################################################

FIRMWARE_RADXA_VERSION = 0.2.43
FIRMWARE_RADXA_SITE = $(call github,radxa-pkg,radxa-firmware,$(FIRMWARE_RADXA_VERSION))
FIRMWARE_RADXA_LICENSE = GPL-3.0
FIRMWARE_RADXA_LICENSE_FILES = LICENSE

ifeq ($(BR2_PACKAGE_ALLLINUXFIRMWARES),y)
FIRMWARE_RADXA_DEPENDENCIES += alllinuxfirmwares
endif
ifeq ($(BR2_PACKAGE_EXTRALINUXFIRMWARES),y)
FIRMWARE_RADXA_DEPENDENCIES += extralinuxfirmwares
endif
ifeq ($(BR2_PACKAGE_FIRMWARE_ARMBIAN),y)
FIRMWARE_RADXA_DEPENDENCIES += firmware-armbian
endif
ifeq ($(BR2_PACKAGE_FIRMWARE_ORANGEPI),y)
FIRMWARE_RADXA_DEPENDENCIES += firmware-orangepi
endif

FIRMWARE_RADXA_FILES = \
	brcm/brcmfmac43456-sdio.bin \
	brcm/brcmfmac43456-sdio.clm_blob \
	brcm/brcmfmac43456-sdio.txt \
	brcm/BCM4345C5.hcd

define FIRMWARE_RADXA_INSTALL_FILES
	$(foreach f,$(FIRMWARE_RADXA_FILES), \
		$(INSTALL) -D -m 0644 $(FIRMWARE_RADXA_DIR)/radxa-firmware/lib/firmware/$(f) \
			$(TARGET_DIR)/lib/firmware/$(f)$(sep))
endef

define FIRMWARE_RADXA_INSTALL_TARGET_CMDS
	$(FIRMWARE_RADXA_INSTALL_FILES)
endef

FIRMWARE_RADXA_TARGET_FINALIZE_HOOKS += FIRMWARE_RADXA_INSTALL_FILES

$(eval $(generic-package))
