################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Jan 29, 2019
ES_THEME_CARBON_VERSION = 37413452b33497385c314b4d630d1b1ccafbb7d6
ES_THEME_CARBON_SITE = $(call github,RetroPie,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    
    cp -r package/batocera/emulationstation/es-theme-carbon/theme/* \
        $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
