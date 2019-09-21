################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Sep 19, 2019
ES_THEME_CARBON_VERSION = 8f958a7d78f610618e398bf73eab5f20dbc5e090
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
