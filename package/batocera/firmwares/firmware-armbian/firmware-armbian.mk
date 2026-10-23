################################################################################
#
# firmware-armbian
#
################################################################################
# Version: Commits on Nov 5, 2025
FIRMWARE_ARMBIAN_VERSION = 5d4dd2fc8dd4e28ac4c85696b8ab86775babc7c7
FIRMWARE_ARMBIAN_SITE = https://github.com/armbian/firmware
FIRMWARE_ARMBIAN_SITE_METHOD = git

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

FIRMWARE_ARMBIAN_FILES = $(call qstrip,$(BR2_PACKAGE_FIRMWARE_ARMBIAN_FILES))

ifneq ($(FIRMWARE_ARMBIAN_FILES),)
define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	cd $(@D) && rsync -a --relative $(FIRMWARE_ARMBIAN_FILES) $(FIRMWARE_ARMBIAN_TARGET_DIR)
endef
else
define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	rsync -au --checksum --force $(@D)/ $(FIRMWARE_ARMBIAN_TARGET_DIR)/
endef
endif

$(eval $(generic-package))
