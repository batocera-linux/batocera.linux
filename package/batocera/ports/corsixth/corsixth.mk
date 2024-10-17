################################################################################
#
# corsixth
#
################################################################################

CORSIXTH_VERSION = v0.68.0
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES = sdl2 sdl2_image lua luafilesystem lpeg luasocket 
CORSIXTH_DEPENDENCIES += luasec sdl2_mixer ffmpeg

define CORSIXTH_INSTALL_EVMAPY
    # evmap config
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/corsixth/corsixth.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

CORSIXTH_POST_INSTALL_TARGET_HOOKS += CORSIXTH_INSTALL_EVMAPY

$(eval $(cmake-package))
