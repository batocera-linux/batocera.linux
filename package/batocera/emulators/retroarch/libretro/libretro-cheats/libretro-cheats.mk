################################################################################
#
# CHEATS
#
################################################################################
# Version.: Commits on May 05, 2019
LIBRETRO_CHEATS_VERSION = b960fa8c56a14fa237f4b573359bc0caf6ccdc11
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))

define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
	cp -r $(@D)/cht/* $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
endef

$(eval $(generic-package))
