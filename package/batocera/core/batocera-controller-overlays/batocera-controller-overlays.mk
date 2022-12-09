################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: May 22, 2022
BATOCERA_CONTROLLER_OVERLAYS_VERSION = 38e1c60b7dd09afaa71bc04bf7ef4a101ab6fb80
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
