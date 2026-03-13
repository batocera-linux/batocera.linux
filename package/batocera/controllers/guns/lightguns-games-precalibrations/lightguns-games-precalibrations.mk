################################################################################
#
# lightguns-games-precalibrations
#
################################################################################
# Version:Commits on Mar 11, 2026
LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION = b2a36161d99ea81b2fdd454941b50927a4cc14eb
LIGHTGUNS_GAMES_PRECALIBRATIONS_SITE = $(call github,batocera-linux,lightguns-games-precalibrations,$(LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION))

define LIGHTGUNS_GAMES_PRECALIBRATIONS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-precalibrations
	cp -pr $(@D)/saves/* $(TARGET_DIR)/usr/share/batocera/guns-precalibrations/
endef

$(eval $(generic-package))
