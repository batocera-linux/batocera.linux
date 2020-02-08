################################################################################
#
# CHEATS
#
################################################################################
# Version.: Commits on Feb 05, 2020
LIBRETRO_CHEATS_VERSION = 5b280d4e0caa5eecd56571e3415695b8369b5480
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))

define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
	cp -r $(@D)/cht/* $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
endef

$(eval $(generic-package))
