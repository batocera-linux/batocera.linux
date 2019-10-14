################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Oct 04, 2019
ES_THEME_CARBON_VERSION = ce704fa6abf9f03dd05861d4b7eb68329f61241a
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
