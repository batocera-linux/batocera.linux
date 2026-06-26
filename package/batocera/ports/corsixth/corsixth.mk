################################################################################
#
# corsixth
#
################################################################################

CORSIXTH_VERSION = v0.69.2
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES =  lua luafilesystem luasec lpeg luasocket libcurl
CORSIXTH_DEPENDENCIES += sdl2 sdl2_image sdl2_mixer ffmpeg
CORSIXTH_EMULATOR_INFO = corsixth.emulator.yml

CORSIXTH_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CORSIXTH_CONF_OPTS += -DWITH_UPDATE_CHECK=OFF

define CORSIXTH_INSTALL_EVMAPY
    # evmap config
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/corsixth/corsixth.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

CORSIXTH_POST_INSTALL_TARGET_HOOKS += CORSIXTH_INSTALL_EVMAPY

$(eval $(cmake-package))
$(eval $(emulator-info-package))
