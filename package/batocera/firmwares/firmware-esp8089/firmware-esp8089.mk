################################################################################
#
# firmware-esp8089
#
################################################################################
# Version: Commits on Aug 7, 2016
FIRMWARE_ESP8089_VERSION = 38cb0c10d70754392932a52d9335a29eed9c3b94
FIRMWARE_ESP8089_SITE = $(call github,jwrdegoede,esp8089,$(FIRMWARE_ESP8089_VERSION))

FIRMWARE_ESP8089_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define FIRMWARE_ESP8089_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ESP8089_TARGET_DIR)
	cp -f $(@D)/firmware/* $(FIRMWARE_ESP8089_TARGET_DIR)
endef

$(eval $(generic-package))
