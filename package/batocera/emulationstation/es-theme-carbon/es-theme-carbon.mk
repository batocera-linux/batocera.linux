################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Dec 9, 2022
ES_THEME_CARBON_VERSION = 2c40e6146d43f891c7b813eeb429c52cf34ca2fd
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
