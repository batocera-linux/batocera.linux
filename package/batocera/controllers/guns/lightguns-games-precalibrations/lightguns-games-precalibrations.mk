################################################################################
#
# lightguns-games-precalibrations
#
################################################################################
# Version:Commits on Oct 7, 2026
LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION = c399dc858ef1a1db750c203d2b3f8177704f516e
LIGHTGUNS_GAMES_PRECALIBRATIONS_SITE = $(call github,batocera-linux,lightguns-games-precalibrations,$(LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION))

define LIGHTGUNS_GAMES_PRECALIBRATIONS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-precalibrations
	cp -pr $(@D)/saves/* $(TARGET_DIR)/usr/share/batocera/guns-precalibrations/
endef

$(eval $(generic-package))
