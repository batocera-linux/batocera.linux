################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on April 21, 2022
ES_THEME_CARBON_VERSION = 2ea66b738c9894403045e196954edf4bebe16c4c
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
