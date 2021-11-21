################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Nov 21, 2021
BATOCERA_CONTROLLER_OVERLAYS_VERSION = f900c3eb578b9d5646ee6a74fc356f5e4707c643
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
