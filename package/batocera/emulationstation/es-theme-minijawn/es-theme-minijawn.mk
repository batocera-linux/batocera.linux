################################################################################
#
# EmulationStation theme "MiniJawn"
#
################################################################################
# Version.: Commits on Sept 2019
ES_THEME_MINIJAWN_VERSION = cdf15459e757efc088edde3f4ac09a20c8959757
ES_THEME_MINIJAWN_SITE = $(call github,pacdude,es-theme-minijawn,$(ES_THEME_MINIJAWN_VERSION))

define ES_THEME_MINIJAWN_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-minijawn
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-minijawn
endef

$(eval $(generic-package))
