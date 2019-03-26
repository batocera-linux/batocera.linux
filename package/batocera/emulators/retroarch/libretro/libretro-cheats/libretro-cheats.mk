################################################################################
#
# CHEATS
#
################################################################################
# Version.: Commits on Mar 25, 2019
LIBRETRO_CHEATS_VERSION = d4a13174712598ed41afc50f5c3ba24cd933a3d8
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))

define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
	cp -r $(@D)/cht/* $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
endef

$(eval $(generic-package))
