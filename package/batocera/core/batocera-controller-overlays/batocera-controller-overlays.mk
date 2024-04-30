################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Jan 19, 2024
BATOCERA_CONTROLLER_OVERLAYS_VERSION = 5bec6fe854fbcafb224c5b5ece0818383158f95d
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
