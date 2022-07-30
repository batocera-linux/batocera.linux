################################################################################
#
# firmware-orangepi4-lts
#
################################################################################

FIRMWARE_ORANGEPI4_LTS_VERSION = f354574e9fa9fc7411c28d45b6336615dca47252
FIRMWARE_ORANGEPI4_LTS_SITE = $(call github,dmanlfc,opi4-lts-firmware,$(FIRMWARE_ORANGEPI4_LTS_VERSION))

FIRMWARE_ORANGEPI4_LTS_TARGET_DIR=$(TARGET_DIR)/lib/firmware/uwe5622

define FIRMWARE_ORANGEPI4_LTS_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)
	cp -r $(@D)/wcnmodem.bin           $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
	cp -r $(@D)/wcnmodem-38222.bin     $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
	cp -r $(@D)/wifi_2355b001_1ant.ini $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
endef

$(eval $(generic-package))
