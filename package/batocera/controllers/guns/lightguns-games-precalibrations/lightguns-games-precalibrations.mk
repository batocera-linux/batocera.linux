################################################################################
#
# lightguns-games-precalibrations
#
################################################################################
# Version:Commits on Oct 7, 2026
LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION = 8538cdaddb00a7ba1a520afb81cd41e22f72ba14
LIGHTGUNS_GAMES_PRECALIBRATIONS_SITE = $(call github,batocera-linux,lightguns-games-precalibrations,$(LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION))

define LIGHTGUNS_GAMES_PRECALIBRATIONS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-precalibrations
	cp -pr $(@D)/saves/* $(TARGET_DIR)/usr/share/batocera/guns-precalibrations/
endef

$(eval $(generic-package))
