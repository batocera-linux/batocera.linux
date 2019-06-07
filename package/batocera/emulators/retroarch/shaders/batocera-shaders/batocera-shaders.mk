################################################################################
#
# batocera shaders
#
################################################################################

BATOCERA_SHADERS_VERSION = 1.0
BATOCERA_SHADERS_SOURCE=
BATOCERA_SHADERS_DEPENDENCIES= glsl-shaders

define BATOCERA_SHADERS_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders
	cp -r package/batocera/emulators/retroarch/shaders/batocera-shaders/configs $(TARGET_DIR)/usr/share/batocera/shaders
endef

$(eval $(generic-package))
