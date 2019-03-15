################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Mar 15, 2019
BATOCERA_BEZEL_VERSION = 1e0699e0fb2e143087cfdf60c57940e20f36ee8c
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
endef

$(eval $(generic-package))
