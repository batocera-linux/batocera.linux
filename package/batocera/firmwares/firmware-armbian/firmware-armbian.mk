################################################################################
#
# armbian firmware
#
################################################################################
# Version.: Commits on Jun 24, 2023
FIRMWARE_ARMBIAN_VERSION = fad830894d83dcb1a4fe72a610fa92ba2ca7c112
FIRMWARE_ARMBIAN_SITE = $(call github,armbian,firmware,$(FIRMWARE_ARMBIAN_VERSION))

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	cp -a $(@D)/* $(FIRMWARE_ARMBIAN_TARGET_DIR)/
endef

$(eval $(generic-package))
