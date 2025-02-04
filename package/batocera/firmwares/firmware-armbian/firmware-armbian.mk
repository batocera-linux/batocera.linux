################################################################################
#
# firmware-armbian
#
################################################################################
# Version: Commits on Jan 26, 2025
FIRMWARE_ARMBIAN_VERSION = 9179a9f05c31505e1bbc90ffb2bfa563e499bfef
FIRMWARE_ARMBIAN_SITE = https://github.com/armbian/firmware
FIRMWARE_ARMBIAN_SITE_METHOD = git

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	cp -aRf $(@D)/* $(FIRMWARE_ARMBIAN_TARGET_DIR)/
endef

$(eval $(generic-package))
