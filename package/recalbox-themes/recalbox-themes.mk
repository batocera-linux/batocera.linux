################################################################################
#
# Recalbox themes for EmulationStation : https://github.com/recalbox/recalbox-themes 
#
################################################################################

RECALBOX_THEMES_VERSION = 4.0.X
RECALBOX_THEMES_SITE = $(call github,recalbox,recalbox-themes,$(RECALBOX_THEMES_VERSION))

define RECALBOX_THEMES_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/recalbox/share_init/system/.emulationstation/themes/
	cp -r $(@D)/themes/* \
		$(TARGET_DIR)/recalbox/share_init/system/.emulationstation/themes/
endef

$(eval $(generic-package))

