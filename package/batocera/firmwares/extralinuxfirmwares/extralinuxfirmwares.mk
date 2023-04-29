################################################################################
#
# extralinuxfirmware
#
################################################################################
# Version.: Commits on Apr 29, 2023
EXTRALINUXFIRMWARES_VERSION = 5ba8541f5ae4a5a8402d5770fb43efe70ca9ce67
EXTRALINUXFIRMWARES_SITE = $(call github,batocera-linux,extralinuxfirmwares,$(EXTRALINUXFIRMWARES_VERSION))
EXTRALINUXFIRMWARES_DEPENDENCIES = alllinuxfirmwares

EXTRALINUXFIRMWARES_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define EXTRALINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(EXTRALINUXFIRMWARES_TARGET_DIR)
	cp -a $(@D)/* $(EXTRALINUXFIRMWARES_TARGET_DIR)/
endef

$(eval $(generic-package))
