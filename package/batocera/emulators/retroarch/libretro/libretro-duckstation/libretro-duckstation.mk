################################################################################
#
# LIBRETRO_DUCKSTATION
#
################################################################################
# Version.: Commits on Dec 18, 2020

LIBRETRO_DUCKSTATION_DEPENDENCIES = fmt boost ffmpeg sdl2
LIBRETRO_DUCKSTATION_SITE_METHOD=git
LIBRETRO_DUCKSTATION_GIT_SUBMODULES=YES
LIBRETRO_DUCKSTATION_LICENSE = GPLv2

LIBRETRO_DUCKSTATION_VERSION = 208e746467f2594aaf5e17b4ed68fdd28948f26e
LIBRETRO_DUCKSTATION_SITE = https://github.com/stenzek/duckstation.git

LIBRETRO_DUCKSTATION_CONF_OPTS = -DBUILD_LIBRETRO_CORE=ON -DENABLE_DISCORD_PRESENCE=OFF
LIBRETRO_DUCKSTATION_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_DUCKSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
LIBRETRO_DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF -DBUILD_SDL_FRONTEND=OFF -DUSE_EGL=OFF -DUSE_WAYLAND=OFF -DUSE_X11=OFF

LIBRETRO_DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
LIBRETRO_DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

define LIBRETRO_DUCKSTATION_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/duckstation_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro
endef

$(eval $(cmake-package))
