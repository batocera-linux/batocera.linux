################################################################################
#
# batocera bezel
#
################################################################################

BATOCERA_BEZEL_VERSION = master
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/recalbox/share_init/decorations
	cp -r $(@D)/* $(TARGET_DIR)/recalbox/share_init/decorations
endef

$(eval $(generic-package))
