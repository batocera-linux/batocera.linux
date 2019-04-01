################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Mar 17, 2019
BATOCERA_BEZEL_VERSION = cef4616c8c0f0ca891f4880f94b18f98c59a515a
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
