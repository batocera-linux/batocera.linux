################################################################################
#
# lightguns-games-precalibrations
#
################################################################################
# Version:Commits on Jan 04, 2026
LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION = b672c3a882fa27964e5e69d77c5857b214e5d58e
LIGHTGUNS_GAMES_PRECALIBRATIONS_SITE = $(call github,batocera-linux,lightguns-games-precalibrations,$(LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION))

define LIGHTGUNS_GAMES_PRECALIBRATIONS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-precalibrations
	cp -pr $(@D)/saves/* $(TARGET_DIR)/usr/share/batocera/guns-precalibrations/
endef

$(eval $(generic-package))
