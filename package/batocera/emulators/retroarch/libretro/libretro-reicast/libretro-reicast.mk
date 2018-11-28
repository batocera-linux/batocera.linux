################################################################################
#
# LIBRETRO-REICAST
#
################################################################################
# Version.: Commits on Nov 26, 2018
LIBRETRO_REICAST_VERSION = 01ffff9facb9b970ac2a7c5336fd1bf301e386f7
LIBRETRO_REICAST_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_VERSION))

LIBRETRO_REICAST_PLATFORM = $(LIBRETRO_PLATFORM)

# LIBRETRO_PLATFORM is not good for this core, because
# for rpi, it contains "unix rpi" and this core do an "if unix elif rpi ..."

# special cases for special plateform then...
# an other proper way may be to redo the Makefile to do "if rpi elif unix ..." (from specific to general)
# the Makefile imposes that the platform has gles (or force FORCE_GLES is set) to not link with lGL

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	LIBRETRO_REICAST_PLATFORM = rpi-gles
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	LIBRETRO_REICAST_PLATFORM = rpi2-gles
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_REICAST_PLATFORM = rpi3-gles
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
	LIBRETRO_REICAST_PLATFORM = odroid-ODROID-XU3-gles
endif

define LIBRETRO_REICAST_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile HAVE_OPENMP=0 platform="$(LIBRETRO_REICAST_PLATFORM)"
endef

define LIBRETRO_REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/reicast_libretro.so
endef

$(eval $(generic-package))
