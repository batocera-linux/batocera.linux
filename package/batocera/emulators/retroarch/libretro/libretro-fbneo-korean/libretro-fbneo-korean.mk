################################################################################
#
# libretro-fbneo-korean
#
################################################################################
# dsno/Zansword's Korean-patched FBNeo fork (CRC-tolerant driver patches for
# Korean-translated arcade ROMs, standard libretro-fbneo rejects these on
# CRC32 mismatch) mirrored to a personal fork for build reproducibility -
# the original only existed as an uncommitted working tree on a dev machine.
# Source snapshot: FBNeo_Libretro_src_20260725, base upstream commit a2594cfa5.
LIBRETRO_FBNEO_KOREAN_VERSION = c716cc6656dec0eff5580e46b6f5fed3bd05685e
LIBRETRO_FBNEO_KOREAN_SITE = $(call github,Pyohwan,FBNeo,$(LIBRETRO_FBNEO_KOREAN_VERSION))
LIBRETRO_FBNEO_KOREAN_LICENSE = Non-commercial
LIBRETRO_FBNEO_KOREAN_DEPENDENCIES += retroarch
LIBRETRO_FBNEO_KOREAN_EMULATOR_INFO = fbneo_korean.libretro.core.yml

LIBRETRO_FBNEO_KOREAN_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS =

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_FBNEO_KOREAN_PLATFORM = unix-rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_FBNEO_KOREAN_PLATFORM = unix-rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_FBNEO_KOREAN_PLATFORM = unix-rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_FBNEO_KOREAN_PLATFORM = unix-rpi4_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_FBNEO_KOREAN_PLATFORM = unix-rpi5_64
endif

ifeq ($(BR2_arm),y)
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS += USE_CYCLONE=1
endif

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS += HAVE_NEON=1
else
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS += HAVE_NEON=0
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86) $(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS += USE_X64_DRC=1 profile=accuracy
else
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS += profile=performance
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS += USE_EXPERIMENTAL_FLAGS=0
endif

define LIBRETRO_FBNEO_KOREAN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/src/burner/libretro -f Makefile \
		platform="$(LIBRETRO_FBNEO_KOREAN_PLATFORM)" $(LIBRETRO_FBNEO_KOREAN_EXTRA_ARGS) \
        GIT_VERSION="$(shell echo $(LIBRETRO_FBNEO_KOREAN_VERSION) | cut -c 1-7)" \
        TARGET_NAME=fbneo_korean
endef

define LIBRETRO_FBNEO_KOREAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/burner/libretro/fbneo_korean_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fbneo_korean_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
