################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Jan 8, 2021
ES_THEME_CARBON_VERSION = 549cc1d013a5c79b90816f076865cbf7061afd0d
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
