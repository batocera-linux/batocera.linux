################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Feb 12, 2026
BATOCERA_CONTROLLER_OVERLAYS_VERSION = 31670285c54f938ebe3db96a5d3e46ec886fab4c
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
