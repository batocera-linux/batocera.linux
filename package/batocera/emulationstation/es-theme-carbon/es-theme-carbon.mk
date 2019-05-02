################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################

ES_THEME_CARBON_VERSION = master
ES_THEME_CARBON_SITE = $(call github,RetroPie,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
