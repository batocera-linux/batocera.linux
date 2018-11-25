################################################################################
#
# batocera shaders
#
################################################################################

BATOCERA_SHADERS_VERSION = 1.0
BATOCERA_SHADERS_SOURCE=

define BATOCERA_SHADERS_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/recalbox/share_init/shaders
	cp -r package/batocera/emulators/retroarch/batocera-shaders/shaders/* $(TARGET_DIR)/recalbox/share_init/shaders
endef

$(eval $(generic-package))
