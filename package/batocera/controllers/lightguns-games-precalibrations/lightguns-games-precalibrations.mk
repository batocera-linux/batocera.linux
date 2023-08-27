################################################################################
#
# lightguns-games-precalibrations
#
################################################################################
# Version:Commits on Oct 25, 2022
LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION = a30c16db1276ee05250784c8d431357cfb249af0
LIGHTGUNS_GAMES_PRECALIBRATIONS_SITE = $(call github,batocera-linux,lightguns-games-precalibrations,$(LIGHTGUNS_GAMES_PRECALIBRATIONS_VERSION))

define LIGHTGUNS_GAMES_PRECALIBRATIONS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-precalibrations
	cp -pr $(@D)/saves/* $(TARGET_DIR)/usr/share/batocera/guns-precalibrations/
endef

$(eval $(generic-package))
