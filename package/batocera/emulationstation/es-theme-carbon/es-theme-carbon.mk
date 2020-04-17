################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Apr 17, 2020
ES_THEME_CARBON_VERSION = 198cf20ad51c13ab4943fa16d8d91bcea7bf166a
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
