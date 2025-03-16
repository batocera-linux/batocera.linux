################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version: Commits on Oct 16, 2024
ES_THEME_CARBON_VERSION = 3fa86fa167fa31a58aef6041e93065d62ae259b8
ES_THEME_CARBON_SITE = $(call github,mittonk,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
