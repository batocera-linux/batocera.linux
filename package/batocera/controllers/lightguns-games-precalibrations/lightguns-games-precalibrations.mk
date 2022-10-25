################################################################################
#
# lightguns-games-precalibrations
#
################################################################################
# Version:Commits on Oct 25, 2022
LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION = 97c6258c411230a9361aa81ada47862d004a2d9d
LIGHTGUNS_GAMES_PRECALIBRATIONS_SITE = $(call github,batocera-linux,lightguns-games-precalibrations,$(LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION))

define LIGHTGUNS_GAMES_PRECALIBRATIONS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-precalibrations
	cp -pr $(@D)/saves/* $(TARGET_DIR)/usr/share/batocera/guns-precalibrations/
endef

$(eval $(generic-package))
