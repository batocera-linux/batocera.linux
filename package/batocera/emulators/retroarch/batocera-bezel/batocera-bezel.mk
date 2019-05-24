################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 24, 2019
BATOCERA_BEZEL_VERSION = a5bbbe2ff5c13c9949a71f4db24c0252c95ed56c
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
