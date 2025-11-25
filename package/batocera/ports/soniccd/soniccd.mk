################################################################################
#
# soniccd
#
################################################################################

SONICCD_VERSION = 1.3.3
SONICCD_SITE = https://github.com/RSDKModding/RSDKv3-Decompilation
SONICCD_SITE_METHOD = git
SONICCD_GIT_SUBMODULES = YES
SONICCD_LICENSE = Custom

SONICCD_DEPENDENCIES = sdl2 libogg libvorbis libtheora

SONICCD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONICCD_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SONICCD_CONF_OPTS += -DRETRO_OUTPUT_NAME=soniccd
SONICCD_CONF_OPTS += -DRETRO_SDL_VERSION=2

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    SONICCD_DEPENDENCIES += libglew libglu
endif

define SONICCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/soniccd $(TARGET_DIR)/usr/bin/soniccd
endef

$(eval $(cmake-package))
