################################################################################
#
# Batocera controller overlays
#
################################################################################
# Last commit: Jan 6, 2024
BATOCERA_CONTROLLER_OVERLAYS_VERSION = 77beba6e9db5575fe22cd27750d85d965bb58f27
BATOCERA_CONTROLLER_OVERLAYS_SITE = \
    $(call github,batocera-linux,batocera-controller-overlays,$(BATOCERA_CONTROLLER_OVERLAYS_VERSION))

define BATOCERA_CONTROLLER_OVERLAYS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/controller-overlays/
    cp -f $(@D)/solid/*.png $(TARGET_DIR)/usr/share/batocera/controller-overlays/
endef

$(eval $(generic-package))
