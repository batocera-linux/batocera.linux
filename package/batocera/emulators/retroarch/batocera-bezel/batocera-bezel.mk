################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Mar 14, 2019
BATOCERA_BEZEL_VERSION = 6efde44ab27c6835612acae0035cf1710e8f74ed
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
