################################################################################
#
# NESTOPIA
#
################################################################################
LIBRETRO_NESTOPIA_VERSION = master
LIBRETRO_NESTOPIA_SITE = $(call github,libretro,nestopia,master)

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
define LIBRETRO_NESTOPIA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro/ platform="$(PLATFORM)"
endef

define LIBRETRO_NESTOPIA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/nestopia_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nestopia_libretro.so
endef

$(eval $(generic-package))
