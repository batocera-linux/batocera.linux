################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Apr 18, 2021
ES_THEME_CARBON_VERSION = 6181edccd04af14e36582fe23218e987a3b06289
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
