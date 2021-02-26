################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Jan 8, 2021
ES_THEME_CARBON_VERSION = 643dfd67e3ab34462b0f282264b1123c9c7c9a41
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
