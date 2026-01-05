################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Jan 3, 2026
ES_THEME_CARBON_VERSION = 7c82223651b4f8c2ca1ff630f50360d1dbe530ad
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
