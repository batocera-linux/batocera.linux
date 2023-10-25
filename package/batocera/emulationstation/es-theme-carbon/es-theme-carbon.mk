################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Oct 24, 2023
ES_THEME_CARBON_VERSION = 91d85c7849cc550b0cac4e75cb8e0923d3b61b5e
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
