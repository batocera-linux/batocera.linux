################################################################################
#
# LIBRETRO-REICAST
#
################################################################################
# Version.: Commits on Jan 22, 2019
LIBRETRO_REICAST_VERSION = b3ac84189693a9d97624282f3dd511ad932a4233
LIBRETRO_REICAST_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_VERSION))

LIBRETRO_REICAST_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_REICAST_EXTRA_ARGS = HAVE_OPENMP=0

# LIBRETRO_PLATFORM is not good for this core, because
# for rpi, it contains "unix rpi" and this core do an "if unix elif rpi ..."

# special cases for special plateform then...
# an other proper way may be to redo the Makefile to do "if rpi elif unix ..." (from specific to general)
# the Makefile imposes that the platform has gles (or force FORCE_GLES is set) to not link with lGL

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_REICAST_PLATFORM = rpi2
	LIBRETRO_REICAST_EXTRA_ARGS += FORCE_GLES=1 ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
	LIBRETRO_REICAST_PLATFORM = odroid
	LIBRETRO_REICAST_EXTRA_ARGS += BOARD=ODROID-XU4 FORCE_GLES=1 ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	LIBRETRO_REICAST_PLATFORM = rockpro64
	LIBRETRO_REICAST_EXTRA_ARGS += ARCH=arm
endif

define LIBRETRO_REICAST_BUILD_CMDS
    CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile $(LIBRETRO_REICAST_EXTRA_ARGS) platform="$(LIBRETRO_REICAST_PLATFORM)"
endef

define LIBRETRO_REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/reicast_libretro.so
endef

$(eval $(generic-package))
