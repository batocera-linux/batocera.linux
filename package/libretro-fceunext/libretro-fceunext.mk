################################################################################
#
# FCEUNEXT
#
################################################################################
LIBRETRO_FCEUNEXT_VERSION = master
LIBRETRO_FCEUNEXT_SITE = $(call github,libretro,fceu-next,master)

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
define LIBRETRO_FCEUNEXT_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/fceumm-code -f Makefile.libretro platform="$(PLATFORM)"
endef

define LIBRETRO_FCEUNEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm-code/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceunext_libretro.so
endef

$(eval $(generic-package))
