################################################################################
#
# Batocera Retroachievements sounds
#
################################################################################

define BATOCERA_RETROACHIEVEMENTS_SOUNDS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/libretro/assets/sounds/
	cp -r $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/retroarch/batocera-retroachievements-sounds/sounds/*.ogg $(TARGET_DIR)/usr/share/libretro/assets/sounds/
endef

$(eval $(generic-package))
