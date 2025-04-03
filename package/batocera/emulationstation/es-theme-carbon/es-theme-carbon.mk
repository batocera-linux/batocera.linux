################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version: Commits on Apr 3, 2025
ES_THEME_CARBON_VERSION = a380e0066fa37099349120555282fc890ae6ea4c
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
