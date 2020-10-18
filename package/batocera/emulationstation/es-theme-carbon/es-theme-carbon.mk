################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Jun 17, 2020
ES_THEME_CARBON_VERSION = 24e0658a1dcbab7df402665fed2b35e60541274d
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
