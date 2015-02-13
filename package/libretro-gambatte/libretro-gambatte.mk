################################################################################
#
# GAMBATTE
#
################################################################################
LIBRETRO_GAMBATTE_VERSION = master
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,master)
PLATFORM =
ifeq ($(BR2_ARM_CPU_ARMV6),y)
        PLATFORM = armv6
endif

ifeq ($(BR2_cortex_a7),y)
        PLATFORM = armv7
endif

ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),hard)
        PLATFORM += hardfloat
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        PLATFORM += neon
endif

define LIBRETRO_GAMBATTE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libgambatte/ -f Makefile.libretro platform="$(PLATFORM)"
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libgambatte/gambatte_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gambatte_libretro.so
endef

$(eval $(generic-package))
