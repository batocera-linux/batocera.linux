################################################################################
#
# firmware-orangepi
#
################################################################################
# Version: Commits on Mar 19, 2025
FIRMWARE_ORANGEPI_VERSION = db5e86200ae592c467c4cfa50ec0c66cbc40b158
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))

# We have newer BT code
ifeq ($(BR2_PACKAGE_FIRMWARE_RADXA_RKWIFIBT),y)
FIRMWARE_ORANGEPI_DEPENDENCIES = firmware-radxa-rkwifibt
endif

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	rsync -a --checksum $(@D)/ $(TARGET_DIR)/lib/firmware/
	# symlinks for compatibility
	ln -sf /lib/firmware/fw_syn43711a0_sdio.bin \
	    $(TARGET_DIR)/lib/firmware/ap6275p/fw_syn43711a0_sdio.bin
	ln -sf /lib/firmware/nvram_ap6611s.txt \
	    $(TARGET_DIR)/lib/firmware/ap6275p/nvram_ap6611s.txt
	ln -sf /lib/firmware/clm_syn43711a0.blob\
	    $(TARGET_DIR)/lib/firmware/ap6275p/clm_syn43711a0.blob
endef

$(eval $(generic-package))
