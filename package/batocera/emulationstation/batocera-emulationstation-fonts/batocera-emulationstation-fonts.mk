################################################################################
#
# batocera-emulationstation-fonts
#
################################################################################

BATOCERA_EMULATIONSTATION_FONTS_VERSION = 1.0
BATOCERA_EMULATIONSTATION_FONTS_SOURCE=

define BATOCERA_EMULATIONSTATION_FONTS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/fonts/truetype/droid
	cp package/batocera/emulationstation/batocera-emulationstation-fonts/DroidSansFallbackFull.ttf $(TARGET_DIR)/usr/share/fonts/truetype/droid
	cp package/batocera/emulationstation/batocera-emulationstation-fonts/fontawesome-webfont.ttf   $(TARGET_DIR)/usr/share/fonts/truetype
endef

$(eval $(generic-package))
