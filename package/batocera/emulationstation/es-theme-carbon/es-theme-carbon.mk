################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Jan 8, 2021
ES_THEME_CARBON_VERSION = 6b1960eec824423c83918f4c6abd3df0e25efbe1
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
