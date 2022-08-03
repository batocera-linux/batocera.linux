################################################################################
#
# firmware-orangepi4-lts
#
################################################################################

FIRMWARE_ORANGEPI4_LTS_VERSION = c93f7bc339c7bddd007f022e9fa1802a772d3498
FIRMWARE_ORANGEPI4_LTS_SITE = $(call github,dmanlfc,opi4-lts-firmware,$(FIRMWARE_ORANGEPI4_LTS_VERSION))

FIRMWARE_ORANGEPI4_LTS_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI4_LTS_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)
	mkdir -p $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/uwe5622
	cp -r $(@D)/wcnmodem-38222.bin     $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/uwe5622/
	cp -r $(@D)/wifi_2355b001_1ant.ini $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/uwe5622/
	cp -r $(@D)/bt_configure_pskey.ini $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
	cp -r $(@D)/bt_configure_rf.ini    $(FIRMWARE_ORANGEPI4_LTS_TARGET_DIR)/
endef

$(eval $(generic-package))
