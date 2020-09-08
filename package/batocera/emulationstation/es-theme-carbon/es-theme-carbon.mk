################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Jun 17, 2020
ES_THEME_CARBON_VERSION = f7fc5e88119b8a8960c14b6a7910d6bdea0006ae
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
