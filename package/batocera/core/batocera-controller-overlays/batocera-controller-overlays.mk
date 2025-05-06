################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: May 6, 2025
BATOCERA_CONTROLLER_OVERLAYS_VERSION = a56586aa7c3434db9aeb7a2aee643b8e20a2b153
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
