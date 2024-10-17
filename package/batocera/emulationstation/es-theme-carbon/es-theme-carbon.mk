################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version: Commits on Oct 16, 2024
ES_THEME_CARBON_VERSION = 421cec038116fe7b6711fa35683470884a28ed55
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
