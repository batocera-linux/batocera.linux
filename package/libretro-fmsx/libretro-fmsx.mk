################################################################################
#
# FMSX
#
################################################################################
LIBRETRO_FMSX_VERSION = master
LIBRETRO_FMSX_SITE = $(call github,libretro,fmsx-libretro,master)
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
define LIBRETRO_FMSX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) platform="$(PLATFORM)"
endef

define LIBRETRO_FMSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fmsx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fmsx_libretro.so
endef

$(eval $(generic-package))
