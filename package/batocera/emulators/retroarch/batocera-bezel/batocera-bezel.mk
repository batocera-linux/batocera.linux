################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Mar 6, 2019
BATOCERA_BEZEL_VERSION = e3ecfc4c0f3310dd63fbb4c49da1c95ae4c1b2f0
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
