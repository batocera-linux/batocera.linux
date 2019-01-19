################################################################################
#
# FBA
#
################################################################################
#LIBRETRO_FBA_VERSION = Commits on Jan 14, 2019
LIBRETRO_FBA_VERSION = fd71e36822aff4d7833293b6f2fd0b404d4bddda
LIBRETRO_FBA_SITE = $(call github,libretro,fbalpha,$(LIBRETRO_FBA_VERSION))

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
    LIBRETRO_FBA_EXTRA_ARGS = HAVE_NEON=1
else
    LIBRETRO_FBA_EXTRA_ARGS = HAVE_NEON=0
endif

define LIBRETRO_FBA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f makefile.libretro platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_FBA_EXTRA_ARGS)
endef

define LIBRETRO_FBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fbalpha_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fba_libretro.so
endef

$(eval $(generic-package))
