################################################################################
#
# VECX
#
################################################################################
# Version.: Commits on Mar 12, 2021
LIBRETRO_VECX_VERSION = 0f3f04b0e5bbb484a84e3416d07f0ae8cdac386e
LIBRETRO_VECX_SITE = $(call github,libretro,libretro-vecx,$(LIBRETRO_VECX_VERSION))
LIBRETRO_VECX_LICENSE = GPLv2|LGPLv2.1

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_VECX_DEPENDENCIES += libgl
else
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_VECX_DEPENDENCIES += libgles
LIBRETRO_VECX_MAKE_OPTS += GLES=1
LIBRETRO_VECX_MAKE_OPTS += GL_LIB=-lGLESv2
else
LIBRETRO_VECX_MAKE_OPTS += HAS_GPU=0
endif
endif

LIBRETRO_VECX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_aarch64),y)
LIBRETRO_VECX_PLATFORM = unix

else ifeq ($(BR2_PACKAGE_BATOCERA_RPI_VCORE),y)
LIBRETRO_VECX_PLATFORM = rpi

else ifeq ($(BR2_PACKAGE_BATOCERA_RPI_MESA3D),y)
LIBRETRO_VECX_PLATFORM = rpi-mesa

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_VECX_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
LIBRETRO_VECX_PLATFORM = unix
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
