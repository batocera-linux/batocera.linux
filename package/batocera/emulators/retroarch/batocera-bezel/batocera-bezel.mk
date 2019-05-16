################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 16, 2019
BATOCERA_BEZEL_VERSION = afb4e9af1789373c876fb3c2dce67beb10096c2c
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
