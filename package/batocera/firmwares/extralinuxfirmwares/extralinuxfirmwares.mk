################################################################################
#
# extralinuxfirmware
#
################################################################################
# Version.: Commits on Mar 12, 2023
EXTRALINUXFIRMWARES_VERSION = 2477566638a6fe22ba2ad79b7508a314b925b577
EXTRALINUXFIRMWARES_SITE = $(call github,batocera-linux,extralinuxfirmwares,$(EXTRALINUXFIRMWARES_VERSION))
EXTRALINUXFIRMWARES_DEPENDENCIES = alllinuxfirmwares

EXTRALINUXFIRMWARES_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define EXTRALINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(EXTRALINUXFIRMWARES_TARGET_DIR)
	cp -a $(@D)/* $(EXTRALINUXFIRMWARES_TARGET_DIR)/
endef

$(eval $(generic-package))
