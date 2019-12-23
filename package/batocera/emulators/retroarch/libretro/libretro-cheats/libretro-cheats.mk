################################################################################
#
# CHEATS
#
################################################################################
# Version.: Commits on Dez 04, 2019
LIBRETRO_CHEATS_VERSION = a4ab7c4fb53e047e3a420b098922ce16e3e1d3cf
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))

define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
	cp -r $(@D)/cht/* $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
endef

$(eval $(generic-package))
