################################################################################
#
# CHEATS
#
################################################################################
# Version.: Commits on Nov 24, 2019
LIBRETRO_CHEATS_VERSION = 9bd7f8f7a2a4e8e062c997e813e79432c487635d
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))

define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
	cp -r $(@D)/cht/* $(TARGET_DIR)/usr/share/batocera/datainit/cheats/cht
endef

$(eval $(generic-package))
