################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Mar 9, 2019
BATOCERA_BEZEL_VERSION = 0b68fe5f6034e3efb67b527de3bbc19fa47b32d7
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
