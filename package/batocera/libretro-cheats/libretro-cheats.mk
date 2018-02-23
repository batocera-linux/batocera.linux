################################################################################
#
# CHEATS
#
################################################################################
LIBRETRO_CHEATS_VERSION = master
LIBRETRO_CHEATS_SITE = $(call github,libretro,libretro-database,$(LIBRETRO_CHEATS_VERSION))


define LIBRETRO_CHEATS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/recalbox/share/cheats/cht
	cp -r $(@D)/cht/* \
		$(TARGET_DIR)/recalbox/share/cheats/cht
endef

$(eval $(generic-package))
