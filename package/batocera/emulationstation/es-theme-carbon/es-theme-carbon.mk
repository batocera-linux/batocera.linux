################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version: Commits on Jun 10, 2024
ES_THEME_CARBON_VERSION = 403525528eb0561785ed604b999ac723708dd37a
ES_THEME_CARBON_SITE = $(call github,fabricecaruso,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
