################################################################################
#
# es-background-musics
#
################################################################################

ES_BACKGROUND_MUSICS_VERSION = 1.0
ES_BACKGROUND_MUSICS_LICENSE = TO BE CONFIRMED # was in the recalbox-themes git when it was open before the licence restriction changes
ES_BACKGROUND_MUSICS_SOURCE=

define ES_BACKGROUND_MUSICS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/music

	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/es-background-musics/music/* $(TARGET_DIR)/usr/share/batocera/music/
endef

$(eval $(generic-package))
