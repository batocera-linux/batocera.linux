################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Mar 25, 2026
ES_THEME_CARBON_VERSION = b921e1734d88d6bc7b9e8cb97dd8f8b91ba2058a
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
