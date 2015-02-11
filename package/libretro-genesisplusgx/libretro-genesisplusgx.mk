################################################################################
#
# GENESISPLUSGX
#
################################################################################
LIBRETRO_GENESISPLUSGX_VERSION = master
LIBRETRO_GENESISPLUSGX_SITE = $(call github,libretro,Genesis-Plus-GX,master)
ifeq ($(BR2_ARM_CPU_ARMV6),y)
        PLATFORM = armv6
endif
ifeq ($(BR2_cortex_a7),"y")
        PLATFORM = armv7
endif
ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),"hard")
        PLATFORM += hardfloat
endif
ifeq ($(BR2_ARM_FPU_NEON_VFPV4),"y")
        PLATFORM += neon
endif
define LIBRETRO_GENESISPLUSGX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(PLATFORM)"
endef

define LIBRETRO_GENESISPLUSGX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/genesis_plus_gx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/genesisplusgx_libretro.so
endef

$(eval $(generic-package))
