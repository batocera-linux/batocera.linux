################################################################################
#
# Recalbox themes for EmulationStation : https://github.com/recalbox/recalbox-themes
#
################################################################################
# Version.: Commits on Apr 7, 2019
RECALBOX_THEMES_VERSION = 2937c7b34becf9d5138b823774cecff8f1972996
RECALBOX_THEMES_SITE = $(call github,batocera-linux,recalbox-themes,$(RECALBOX_THEMES_VERSION))

define RECALBOX_THEMES_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
	cp -r $(@D)/themes/recalbox \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
	cp -r $(@D)/themes/batocera-light \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
endef

$(eval $(generic-package))
