################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 17, 2019
BATOCERA_BEZEL_VERSION = b37f3c48dfda2e98bddfb97346e95a1624c77de7
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
