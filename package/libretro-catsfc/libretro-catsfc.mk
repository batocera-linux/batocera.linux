################################################################################
#
# CATSFC
#
################################################################################
LIBRETRO_CATSFC_VERSION = master
LIBRETRO_CATSFC_SITE = $(call github,libretro,CATSFC-libretro,master)

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
define LIBRETRO_CATSFC_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(PLATFORM)"
endef

define LIBRETRO_CATSFC_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/catsfc_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/catsfc_libretro.so
endef

$(eval $(generic-package))
