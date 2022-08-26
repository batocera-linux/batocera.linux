################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Aug 17, 2022
ES_THEME_CARBON_VERSION = 8f2081bfbc01abc7ceaecb2c13684270452d02cc
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
