################################################################################
#
# BSNES-HD
#
################################################################################
# Version.: Commits on Mar 30, 2021
LIBRETRO_BSNES_HD_VERSION = d2d7815c25ec3f0e3df0afd3b8a0df81ecd0e25f
LIBRETRO_BSNES_HD_SITE = $(call github,DerKoun,bsnes-hd,$(LIBRETRO_BSNES_HD_VERSION))
LIBRETRO_BSNES_HD_LICENSE = GPLv3

define LIBRETRO_BSNES_HD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/bsnes -f GNUmakefile target="libretro" platform=linux local=false
endef

define LIBRETRO_BSNES_HD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_hd_beta_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_hd_libretro.so
endef

$(eval $(generic-package))
