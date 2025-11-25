################################################################################
#
# sonic2013
#
################################################################################

SONIC2013_VERSION = 1.3.3
SONIC2013_SITE = https://github.com/RSDKModding/RSDKv4-Decompilation
SONIC2013_SITE_METHOD = git
SONIC2013_GIT_SUBMODULES == YES
SONIC2013_LICENSE = Custom

SONIC2013_DEPENDENCIES = sdl2 libogg libvorbis

SONIC2013_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONIC2013_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SONIC2013_CONF_OPTS += -DRETRO_REVISION=3
SONIC2013_CONF_OPTS += -DRETRO_SDL_VERSION=2
SONIC2013_CONF_OPTS += -DRETRO_OUTPUT_NAME=sonic2013

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    SONIC2013_DEPENDENCIES += libglew libglu
endif

define SONIC2013_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/sonic2013 $(TARGET_DIR)/usr/bin/sonic2013
endef

$(eval $(cmake-package))
