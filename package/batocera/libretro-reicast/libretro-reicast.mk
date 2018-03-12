################################################################################
#
# REICAST
#
################################################################################
LIBRETRO_REICAST_VERSION = fff2eb2f92251db82cb763d3ab1d19be4a705f95
LIBRETRO_REICAST_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_VERSION))

LIBRETRO_REICAST_PLATFORM = $(LIBRETRO_PLATFORM)

# LIBRETRO_PLATFORM is not good for this core, because
# for rpi, it contains "unix rpi" and this core do an "if unix elif rpi ..."

# special cases for special plateform then...
# an other proper way may be to redo the Makefile to do "if rpi elif unix ..." (from specific to general)
# the Makefile imposes that the platform has gles (or force FORCE_GLES is set) to not link with lGL

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI1),y)
	LIBRETRO_REICAST_PLATFORM = rpi-gles
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
	LIBRETRO_REICAST_PLATFORM = rpi2-gles
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
	LIBRETRO_REICAST_PLATFORM = rpi3-gles
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_XU4),y)
	LIBRETRO_REICAST_PLATFORM = odroid-ODROID-XU3-gles
endif

define LIBRETRO_REICAST_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="$(LIBRETRO_REICAST_PLATFORM)"
endef

define LIBRETRO_REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/libretro-reicast_libretro.so
endef

$(eval $(generic-package))
