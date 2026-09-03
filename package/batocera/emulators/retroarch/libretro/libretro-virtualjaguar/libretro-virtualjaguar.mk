################################################################################
#
# libretro-virtualjaguar
#
################################################################################
# Version: Commits on Aug 26, 2026
LIBRETRO_VIRTUALJAGUAR_VERSION = 9a42b528c5c37f580578d46595b9cf38ae9673f8
LIBRETRO_VIRTUALJAGUAR_SITE = $(call github,libretro,virtualjaguar-libretro,$(LIBRETRO_VIRTUALJAGUAR_VERSION))
LIBRETRO_VIRTUALJAGUAR_LICENSE = GPLv3
LIBRETRO_VIRTUALJAGUAR_DEPENDENCIES += retroarch
LIBRETRO_VIRTUALJAGUAR_EMULATOR_INFO = virtualjaguar.libretro.core.yml

LIBRETRO_VIRTUALJAGUAR_EXTRA_ARGS =

# Makefile.common falls back to uname -m for platform=unix cross-builds when
# BLITTER_SIMD is unset, picking the build host's SIMD instead of the target's
# (e.g. NEON on an ARM64 Mac when cross-compiling for x86_64), so we set it
# explicitly here.
#
# Batocera enables this core on x86 (zen3, x86_64, x86_wow64) and aarch64
# boards only (bcm2712, s922x, a3gen2, rk3576/3588, qcs6490, sm6115/8250/8550/8750).
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
LIBRETRO_VIRTUALJAGUAR_EXTRA_ARGS += BLITTER_SIMD=sse2
else ifeq ($(BR2_aarch64),y)
LIBRETRO_VIRTUALJAGUAR_EXTRA_ARGS += BLITTER_SIMD=neon
else
LIBRETRO_VIRTUALJAGUAR_EXTRA_ARGS += BLITTER_SIMD=scalar
endif

define LIBRETRO_VIRTUALJAGUAR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile \
		platform="unix" $(LIBRETRO_VIRTUALJAGUAR_EXTRA_ARGS) \
		GIT_VERSION="-$(shell echo $(LIBRETRO_VIRTUALJAGUAR_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_VIRTUALJAGUAR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/virtualjaguar_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/virtualjaguar_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
