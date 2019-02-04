################################################################################
#
# CHEATS
#
################################################################################
# Version.: Commits on Feb 4, 2019
LIBRETRO_CHEATS_VERSION = b2853574592aa6fce1adaaf2bdc5f16eb7609ee9
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))

define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
	cp -r $(@D)/cht/* $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
endef

$(eval $(generic-package))
