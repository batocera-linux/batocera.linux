################################################################################
#
# LIBRETRO-FLYCAST
#
################################################################################
# Version.: Commits on Apr 15, 2020
LIBRETRO_FLYCAST_VERSION = 51661bb384e7cbdea9d67dbb1fdf18639eec0859
LIBRETRO_FLYCAST_SITE = $(call github,libretro,flycast,$(LIBRETRO_FLYCAST_VERSION))
LIBRETRO_FLYCAST_LICENSE = GPLv2

LIBRETRO_FLYCAST_PLATFORM = $(LIBRETRO_PLATFORM)

# LIBRETRO_PLATFORM is not good for this core, because
# for rpi, it contains "unix rpi" and this core do an "if unix elif rpi ..."

# special cases for special plateform then...
# an other proper way may be to redo the Makefile to do "if rpi elif unix ..." (from specific to general)
# the Makefile imposes that the platform has gles (or force FORCE_GLES is set) to not link with lGL

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_FLYCAST_PLATFORM = rpi-rpi4
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm FORCE_GLES=1 LDFLAGS=-lrt
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_FLYCAST_PLATFORM = rpi-rpi3
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm FORCE_GLES=1 LDFLAGS=-lrt
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	LIBRETRO_FLYCAST_PLATFORM = odroid
	LIBRETRO_FLYCAST_EXTRA_ARGS += BOARD=ODROID-XU4 FORCE_GLES=1 ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	LIBRETRO_FLYCAST_PLATFORM = rockpro64
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm FORCE_GLES=1 LDFLAGS=-lrt
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCK960),y)
	LIBRETRO_FLYCAST_PLATFORM = rockpro64
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm FORCE_GLES=1 LDFLAGS=-lrt
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_FLYCAST_PLATFORM = odroid-n2
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm FORCE_GLES=1 LDFLAGS=-lrt
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_FLYCAST_PLATFORM = classic_armv8_a35
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm FORCE_GLES=1 LDFLAGS=-lrt
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TINKERBOARD),y)
	LIBRETRO_FLYCAST_PLATFORM = tinkerboard
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
	LIBRETRO_FLYCAST_PLATFORM = tinkerboard
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm
endif

define LIBRETRO_FLYCAST_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/ -f Makefile HAVE_OPENMP=1 $(LIBRETRO_FLYCAST_EXTRA_ARGS) platform="$(LIBRETRO_FLYCAST_PLATFORM)"
endef

define LIBRETRO_FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/flycast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/flycast_libretro.so
endef

$(eval $(generic-package))
