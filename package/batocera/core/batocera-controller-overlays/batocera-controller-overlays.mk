################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: May 18, 2022
BATOCERA_CONTROLLER_OVERLAYS_VERSION = 0dfa15a0ae1e32835ba280ff4bf76a73870bc532
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
