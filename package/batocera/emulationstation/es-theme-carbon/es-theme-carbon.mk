################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Nov 1, 2020
ES_THEME_CARBON_VERSION = 3b7605a99783742257e1a0b5c79ab79c14038a1c
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
