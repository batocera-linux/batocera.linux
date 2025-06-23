################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Jun 22, 2025
ES_THEME_CARBON_VERSION = 0677b6ee8c6b200f54882e5b952ff59104406165
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
