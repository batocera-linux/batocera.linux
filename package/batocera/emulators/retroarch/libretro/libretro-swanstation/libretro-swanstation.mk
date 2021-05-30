################################################################################
#
# LIBRETRO_SWANSTATION
#
################################################################################
# Version.: Commits on Apr 14, 2021
LIBRETRO_SWANSTATION_VERSION = a39c7512c47c125f554c4e4725217c16628683e4
LIBRETRO_SWANSTATION_SITE = $(call github,libretro,duckstation,$(LIBRETRO_SWANSTATION_VERSION))
LIBRETRO_SWANSTATION_LICENSE = GPLv2
LIBRETRO_SWANSTATION_DEPENDENCIES = fmt boost ffmpeg retroarch

LIBRETRO_SWANSTATION_CONF_OPTS = -DBUILD_LIBRETRO_CORE=ON -DENABLE_DISCORD_PRESENCE=OFF
LIBRETRO_SWANSTATION_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_SWANSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
LIBRETRO_SWANSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF -DBUILD_SDL_FRONTEND=OFF -DUSE_EGL=OFF -DUSE_WAYLAND=OFF -DUSE_X11=OFF

LIBRETRO_SWANSTATION_CONF_ENV += LDFLAGS=-lpthread

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
LIBRETRO_SWANSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

define LIBRETRO_SWANSTATION_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/swanstation_libretro.so \
	$(TARGET_DIR)/usr/lib/libretro/swanstation_libretro.so
endef

$(eval $(cmake-package))
