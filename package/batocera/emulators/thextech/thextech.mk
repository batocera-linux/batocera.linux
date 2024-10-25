################################################################################
#
# TheXTech
#
################################################################################

THEXTECH_VERSION = v1.3.6.6
THEXTECH_SITE = https://github.com/Wohlstand/TheXTech
THEXTECH_SITE_METHOD = git
THEXTECH_GIT_SUBMODULES = YES
THEXTECH_LICENSE = GPLv3
THEXTECH_DEPENDENCIES = sdl2 sdl2_mixer sdl2_ttf

THEXTECH_CONF_ENV = GIT_DISCOVERY_ACROSS_FILESYSTEM=1

THEXTECH_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
THEXTECH_CONF_OPTS += -DUSE_SYSTEM_SDL2=ON
THEXTECH_CONF_OPTS += -DTHEXTECH_ENABLE_TTF_SUPPORT=ON

ifneq ($(BR2_PACKAGE_HAS_LIBGL),y)
    THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_DESKTOP_MODERN=OFF
    THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_DESKTOP_LEGACY=OFF
ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_ES_MODERN=ON
    THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_ES_LEGACY=OFF
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_ES_MODERN=OFF
    THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_ES_LEGACY=ON
endif
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
    THEXTECH_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali
    THEXTECH_CONF_OPTS += -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

define THEXTECH_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/output/bin/thextech $(TARGET_DIR)/usr/bin/
	cp -avf $(@D)/output/lib/libSDL2_mixer_ext.so* $(TARGET_DIR)/usr/lib/
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -avf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/thextech/thextech.keys \
	    $(TARGET_DIR)/usr/share/evmapy/
endef

$(eval $(cmake-package))
