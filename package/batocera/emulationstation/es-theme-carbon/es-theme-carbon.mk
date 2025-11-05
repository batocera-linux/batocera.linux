################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Nov 5, 2025
ES_THEME_CARBON_VERSION = d03375dfd6af53ba5f2bcd3ced13df9032afc54e
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
