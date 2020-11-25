################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Nov 1, 2020
ES_THEME_CARBON_VERSION = c961b70df3c3795150732706c65457d6d6c10944
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
