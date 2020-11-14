################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Nov 1, 2020
ES_THEME_CARBON_VERSION = 7f4a95ff45e4c800f31cb77e24fd0d5f40db41d7
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
