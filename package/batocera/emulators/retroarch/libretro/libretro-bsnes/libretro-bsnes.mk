################################################################################
#
# BSNES
#
################################################################################
# Version.: Commits on Feb 01, 2020 (v114.3)
LIBRETRO_BSNES_VERSION = 3a74cbe0dc1d46458946a4cec5f3c1c0bbf7751e
LIBRETRO_BSNES_SITE = $(call github,DerKoun,bsnes-hd,$(LIBRETRO_BSNES_VERSION))
LIBRETRO_BSNES_LICENSE = GPLv3

define LIBRETRO_BSNES_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" -C $(@D)/bsnes -f GNUmakefile target="libretro" platform=linux local=false
endef

define LIBRETRO_BSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_hd_beta_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_libretro.so
endef

$(eval $(generic-package))
