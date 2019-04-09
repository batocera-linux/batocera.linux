################################################################################
#
# Recalbox themes for EmulationStation : https://github.com/recalbox/recalbox-themes
#
################################################################################
# Version.: Commits on Apr 9, 2019
RECALBOX_THEMES_VERSION = 1693d996643065ffa6f6eb3de4225f8743d3f1e5
RECALBOX_THEMES_SITE = $(call github,batocera-linux,recalbox-themes,$(RECALBOX_THEMES_VERSION))

define RECALBOX_THEMES_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
	cp -r $(@D)/themes/recalbox \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
	cp -r $(@D)/themes/batocera-light \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
endef

$(eval $(generic-package))
