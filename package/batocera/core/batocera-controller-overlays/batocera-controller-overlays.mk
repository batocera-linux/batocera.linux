################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Dec 13, 2023
BATOCERA_CONTROLLER_OVERLAYS_VERSION = 9e881b9cd861b7ae8d6df0cdb3149cc485a8f208
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
