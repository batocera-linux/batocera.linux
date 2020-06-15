################################################################################
#
# LIBRETRO-FLYCAST
#
################################################################################
# Version.: Commits on Jun 9, 2020
LIBRETRO_FLYCAST_VERSION = 984153f4da9b0bb1ecadd6b3d1be0e5cfed08edb
LIBRETRO_FLYCAST_SITE = $(call github,libretro,flycast,$(LIBRETRO_FLYCAST_VERSION))
LIBRETRO_FLYCAST_LICENSE = GPLv2

LIBRETRO_FLYCAST_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_FLYCAST_EXTRA_ARGS = HAVE_OPENMP=1

# LIBRETRO_PLATFORM is not good for this core, because
# for rpi, it contains "unix rpi" and this core do an "if unix elif rpi ..."

# special cases for special plateform then...
# an other proper way may be to redo the Makefile to do "if rpi elif unix ..." (from specific to general)
# the Makefile imposes that the platform has gles (or force FORCE_GLES is set) to not link with lGL

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_FLYCAST_PLATFORM = rpi-rpi4
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm
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

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
	LIBRETRO_FLYCAST_PLATFORM = odroid-n2
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=arm64 FORCE_GLES=1 LDFLAGS=-lrt
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

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	LIBRETRO_FLYCAST_EXTRA_ARGS += ARCH=x86
endif

define LIBRETRO_FLYCAST_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile \
		platform="$(LIBRETRO_FLYCAST_PLATFORM)" $(LIBRETRO_FLYCAST_EXTRA_ARGS)
endef

define LIBRETRO_FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/flycast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/flycast_libretro.so
endef

$(eval $(generic-package))
