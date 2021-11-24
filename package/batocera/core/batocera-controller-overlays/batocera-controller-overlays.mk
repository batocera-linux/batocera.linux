################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Nov 24, 2021
BATOCERA_CONTROLLER_OVERLAYS_VERSION = ff04f89e34e621c51a8716a942fec0f1ef301454
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
