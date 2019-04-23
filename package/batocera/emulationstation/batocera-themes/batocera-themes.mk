################################################################################
#
# Batocera themes for EmulationStation
#
################################################################################
# Version.: Commits on Apr 10, 2019
BATOCERA_THEMES_VERSION = 9a32d45f78bd5bc932b510e655fa8f2a0b34ac79
BATOCERA_THEMES_SITE = $(call github,batocera-linux,batocera-themes,$(BATOCERA_THEMES_VERSION))

define BATOCERA_THEMES_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
	cp -r $(@D)/themes/batocera $(TARGET_DIR)/usr/share/batocera/datainit/system/.emulationstation/themes/
endef

$(eval $(generic-package))
