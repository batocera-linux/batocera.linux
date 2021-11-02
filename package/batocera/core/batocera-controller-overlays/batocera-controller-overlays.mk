################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Nov 2, 2021
BATOCERA_CONTROLLER_OVERLAYS_VERSION = b66c846ed8ba741933fa1b0ff7c78ba89541856a
BATOCERA_CONTROLLER_OVERLAYS_SITE = $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    # cp -f $(@D)/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    find $(@D) -iname '*.png' -not -iname '*-4k.png' -exec cp '{}' '$(TARGET_DIR)/usr/share/batocera/controller-overlays/' ';'
endef

$(eval $(generic-package))
