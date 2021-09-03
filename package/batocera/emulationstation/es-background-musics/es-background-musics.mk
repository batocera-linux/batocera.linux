################################################################################
#
# es-background-musics
#
################################################################################

ES_BACKGROUND_MUSICS_VERSION = 2.0
ES_BACKGROUND_MUSICS_LICENSE = See license.md, they are free to use with Batocera
ES_BACKGROUND_MUSICS_SOURCE=

define ES_BACKGROUND_MUSICS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/music

	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/es-background-musics/music/* $(TARGET_DIR)/usr/share/batocera/music/
endef

$(eval $(generic-package))
