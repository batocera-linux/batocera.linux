################################################################################
#
# firmware-armbian
#
################################################################################
# Version: Commits on Mar 14, 2025
FIRMWARE_ARMBIAN_VERSION = 509fadf8bd4eabc122670ffc37f8e92dae68656e
FIRMWARE_ARMBIAN_SITE = https://github.com/armbian/firmware
FIRMWARE_ARMBIAN_SITE_METHOD = git

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	rsync -au --checksum --force $(@D)/ $(FIRMWARE_ARMBIAN_TARGET_DIR)/
endef

$(eval $(generic-package))
