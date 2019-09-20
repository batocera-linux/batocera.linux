################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Sep 19, 2019
ES_THEME_CARBON_VERSION = e1ab9c72f484e0ad41402f9b5142fabd2e2538fd
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r package/batocera/emulationstation/es-theme-carbon/theme/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
