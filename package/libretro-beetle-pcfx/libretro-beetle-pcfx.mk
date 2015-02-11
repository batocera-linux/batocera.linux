################################################################################
#
# BEETLE_PCFX
#
################################################################################
LIBRETRO_BEETLE_PCFX_VERSION = master
LIBRETRO_BEETLE_PCFX_SITE = $(call github,libretro,beetle-pcfx-libretro,master)
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

define LIBRETRO_BEETLE_PCFX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" AR="$(TARGET_AR)" RANLIB="$(TARGET_RANLIB)" -C $(@D) platform="$(PLATFORM)"
endef

define LIBRETRO_BEETLE_PCFX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pcfx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcfx_libretro.so
endef

$(eval $(generic-package))
