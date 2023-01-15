################################################################################
#
# firmware-rock5b
#
################################################################################

FIRMWARE_ROCK5B_VERSION = bf5f91cb0e641962630979a8b73f668ae8bd8ed9
FIRMWARE_ROCK5B_SITE = $(call github,radxa,rkwifibt,$(FIRMWARE_ROCK5B_VERSION))
FIRMWARE_ROCK5B_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_ROCK5B_TARGET_DIR=$(TARGET_DIR)/lib/firmware/brcm

define FIRMWARE_ROCK5B_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ROCK5B_TARGET_DIR)
	find $(@D)/firmware -type f -exec cp -v {} $(FIRMWARE_ROCKPRO64_TARGET_DIR) \;
endef

$(eval $(generic-package))
