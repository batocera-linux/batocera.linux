################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Nov 1, 2021
BATOCERA_CONTROLLER_OVERLAYS_VERSION = cf7c810b2c54ffa322a4d3ab65577895800008d9
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    # cp -f $(@D)/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    find $(@D) -iname '*.png' -not -iname '*-4k.png' -exec cp '{}' '$(TARGET_DIR)/usr/share/batocera/controller-overlays/' ';'
endef

$(eval $(generic-package))
