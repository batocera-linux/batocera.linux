################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Feb 13, 2024
ES_THEME_CARBON_VERSION = 6b868454cad63296a3f36b1d3c5307d60f23ac2b
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
