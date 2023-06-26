################################################################################
#
# armbian firmware
#
################################################################################
# Version.: Commits on Jun 24, 2023
BATOCERA_FIRMWARE_ARMBIAN_VERSION = fad830894d83dcb1a4fe72a610fa92ba2ca7c112
BATOCERA_FIRMWARE_ARMBIAN_SITE = $(call github,armbian,firmware,$(BATOCERA_FIRMWARE_ARMBIAN_VERSION))

BATOCERA_FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define BATOCERA_FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(BATOCERA_FIRMWARE_ARMBIAN_TARGET_DIR)
	cp -a $(@D)/* $(BATOCERA_FIRMWARE_ARMBIAN_TARGET_DIR)/
endef

$(eval $(generic-package))
