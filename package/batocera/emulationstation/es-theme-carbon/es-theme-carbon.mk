################################################################################
#
# es-theme-carbon
#
################################################################################
# Version: Commits on Jan 26, 2026
ES_THEME_CARBON_VERSION = 507eb2c025fb51277166dfedbb493b8ac576d14c
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
