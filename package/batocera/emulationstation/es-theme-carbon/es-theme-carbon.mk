################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Nov 30, 2021
ES_THEME_CARBON_VERSION = 94c6322799fc543abf5205292002d1aedce89ffc
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
