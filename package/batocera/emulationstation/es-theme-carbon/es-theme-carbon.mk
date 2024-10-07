################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version: Commits on Sep 16, 2024
ES_THEME_CARBON_VERSION = 06db7dc11c1eb618ccaccad6343e861071271dd5
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
