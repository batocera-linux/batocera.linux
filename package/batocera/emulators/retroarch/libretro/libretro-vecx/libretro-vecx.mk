################################################################################
#
# VECX
#
################################################################################
# Version.: Commits on Oct 18, 2020
LIBRETRO_VECX_VERSION = 7f8d42e0f5e891997afa72a639dbcc0f3be710c6
LIBRETRO_VECX_SITE = $(call github,libretro,libretro-vecx,$(LIBRETRO_VECX_VERSION))
LIBRETRO_VECX_LICENSE = GPLv2|LGPLv2.1

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_VECX_DEPENDENCIES += libgl
else
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_VECX_DEPENDENCIES += libgles
LIBRETRO_VECX_MAKE_OPTS += GLES=1
else
LIBRETRO_VECX_MAKE_OPTS += HAS_GPU=0
endif
endif

LIBRETRO_VECX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_VECX_PLATFORM = rpi
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_VECX_PLATFORM = rpi-mesa
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_VECX_PLATFORM = classic_armv8_a35
endif

LIBRETRO_VECX_MAKE_OPTS += platform="$(LIBRETRO_VECX_PLATFORM)"

define LIBRETRO_VECX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro $(LIBRETRO_VECX_MAKE_OPTS)
endef

define LIBRETRO_VECX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vecx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vecx_libretro.so
endef

$(eval $(generic-package))
