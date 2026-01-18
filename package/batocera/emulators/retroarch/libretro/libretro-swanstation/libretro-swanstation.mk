################################################################################
#
# libretro-swanstation
#
################################################################################
# Version: Commits on Aug 2, 2025
LIBRETRO_SWANSTATION_VERSION = 4d309c05fd7bdc503d91d267bd542edb8d192b09
LIBRETRO_SWANSTATION_SITE = $(call github,libretro,swanstation,$(LIBRETRO_SWANSTATION_VERSION))
LIBRETRO_SWANSTATION_LICENSE = GPLv2
LIBRETRO_SWANSTATION_DEPENDENCIES = fmt boost ffmpeg retroarch
LIBRETRO_SWANSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_SWANSTATION_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LIBRETRO_SWANSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

LIBRETRO_SWANSTATION_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_WAYLAND),y)
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_WAYLAND=ON
else
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_WAYLAND=OFF
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_X11=ON
else
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_GLX=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_EGL=ON
else
  LIBRETRO_SWANSTATION_CONF_OPTS += -DUSE_EGL=OFF
endif

define LIBRETRO_SWANSTATION_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/swanstation_libretro.so \
	    $(TARGET_DIR)/usr/lib/libretro/swanstation_libretro.so
endef

$(eval $(cmake-package))
