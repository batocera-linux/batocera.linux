################################################################################
#
# LIBRETRO FLYCAST WINCE
#
################################################################################
# Version.: Commits on Aug 13, 2019
LIBRETRO_FLYCAST_WINCE_VERSION = 33c2ce0fcacd43b963448d1899c30dbbb15e8464
LIBRETRO_FLYCAST_WINCE_SITE = $(call github,libretro,flycast,$(LIBRETRO_FLYCAST_WINCE_VERSION))
LIBRETRO_FLYCAST_WINCE_LICENSE = GPLv2

LIBRETRO_FLYCAST_WINCE_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_FLYCAST_WINCE_EXTRA_ARGS = HAVE_OPENMP=0

# LIBRETRO_PLATFORM is not good for this core, because
# for rpi, it contains "unix rpi" and this core do an "if unix elif rpi ..."

# special cases for special plateform then...
# an other proper way may be to redo the Makefile to do "if rpi elif unix ..." (from specific to general)
# the Makefile imposes that the platform has gles (or force FORCE_GLES is set) to not link with lGL

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_FLYCAST_WINCE_PLATFORM = rpi3
	LIBRETRO_FLYCAST_WINCE_EXTRA_ARGS += FORCE_GLES=1 ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
	LIBRETRO_FLYCAST_WINCE_PLATFORM = odroid
	LIBRETRO_FLYCAST_WINCE_EXTRA_ARGS += BOARD=ODROID-XU4 FORCE_GLES=1 ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	LIBRETRO_FLYCAST_WINCE_PLATFORM = rockpro64
	LIBRETRO_FLYCAST_WINCE_EXTRA_ARGS += ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_FLYCAST_WINCE_PLATFORM = odroidn2
	LIBRETRO_FLYCAST_WINCE_EXTRA_ARGS += ARCH=arm
endif

define LIBRETRO_FLYCAST_WINCE_BUILD_CMDS
    CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile $(LIBRETRO_FLYCAST_WINCE_EXTRA_ARGS) platform="$(LIBRETRO_FLYCAST_WINCE_PLATFORM)"
endef

define LIBRETRO_FLYCAST_WINCE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/flycast_wince_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/flycast_wince_libretro.so
endef

$(eval $(generic-package))
