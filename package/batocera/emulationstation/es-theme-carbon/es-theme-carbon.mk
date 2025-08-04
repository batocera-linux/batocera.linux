################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Jul 5, 2025
ES_THEME_CARBON_VERSION = 6391092f4ee2ee8a1cc7814a710ee1cc4d9be9c0
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
