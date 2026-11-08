################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Nov 8, 2026
ES_THEME_CARBON_VERSION = a897233e9bf6b9cca5c248ffceebf443882de926
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
