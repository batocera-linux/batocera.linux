################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Apr 18, 2021
ES_THEME_CARBON_VERSION = 69b9478e10200d27541229eda05e138daa5bb077
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
