################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 18, 2019
BATOCERA_BEZEL_VERSION = e0ae21fd4be804c081efa381fb5c0f811d52547e
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
