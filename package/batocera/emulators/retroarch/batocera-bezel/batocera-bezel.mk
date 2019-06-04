################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on June 04, 2019
BATOCERA_BEZEL_VERSION = daee848e5cf6553871e80d529739724cd34f7666
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
